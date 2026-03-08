import os
import json
import time
import hashlib
import tempfile
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

load_dotenv()

# ── Constants ─────────────────────────────────────────────────────────────────
CHUNK_SIZE       = 4000
CHUNK_OVERLAP    = 200
EMBEDDING_MODEL  = "gemini-embedding-001"  # only model that works on these keys

EMBED_BATCH_SIZE = 5     # chunks per API call per worker
MAX_RETRIES      = 5     # retries before giving up on a batch
RETRY_BASE_DELAY = 3.0   # base seconds for exponential backoff
QUOTA_WAIT       = 65    # seconds to wait on 429 — free tier resets every 60s

BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORSTORE_DIR = os.path.join(BASE_DIR, "data", "vector_stores")
MANIFEST_FILE   = os.path.join(BASE_DIR, "data", "ingest_manifest.json")


# ── API Key Pool ──────────────────────────────────────────────────────────────
def _load_api_keys() -> List[str]:
    """
    Load up to 3 API keys from .env.
    GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, GOOGLE_API_KEY_3
    Falls back to GOOGLE_API_KEY if numbered keys not found.
    Since keys are from 3 DIFFERENT Google accounts, each has its own
    independent quota — true parallel embedding gives ~3x speed.
    """
    keys = []
    for i in range(1, 4):
        k = os.getenv(f"GOOGLE_API_KEY_{i}")
        if k:
            keys.append(k)
    if not keys:
        k = os.getenv("GOOGLE_API_KEY")
        if k:
            keys.append(k)
    if not keys:
        raise ValueError("⚠️  No GOOGLE_API_KEY found in .env file")
    print(f"  🔑 {len(keys)} API key(s) from {len(keys)} separate accounts — true parallel mode")
    return keys

API_KEYS = _load_api_keys()


def _make_embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=api_key,
    )


# ── Boilerplate filter ────────────────────────────────────────────────────────
SKIP_KEYWORDS = [
    "independent auditor", "auditor's report", "statutory auditor",
    "notes to financial", "pursuant to regulation", "as per section",
    "hereby certify", "din:", "cin:", "we have audited",
    "basis of opinion", "key audit matters",
]

def _is_useful_chunk(text: str) -> bool:
    if len(text.strip()) < 150:
        return False
    text_lower = text.lower()
    return sum(1 for kw in SKIP_KEYWORDS if kw in text_lower) < 2


# ── Manifest helpers ──────────────────────────────────────────────────────────
def _load_manifest() -> Dict:
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_manifest(manifest: Dict) -> None:
    os.makedirs(os.path.dirname(MANIFEST_FILE), exist_ok=True)
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()

def is_already_ingested(ticker: str, url: str) -> bool:
    return f"{ticker}::{_url_hash(url)}" in _load_manifest()

def mark_ingested(ticker: str, url: str) -> None:
    manifest = _load_manifest()
    manifest[f"{ticker}::{_url_hash(url)}"] = {"url": url, "ts": time.time()}
    _save_manifest(manifest)


# ── PDF helpers ───────────────────────────────────────────────────────────────
def download_and_extract(pdf_url: str, metadata: Dict) -> List[Document]:
    temp_pdf_path = None
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(pdf_url, headers=headers, timeout=30)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(response.content)
            temp_pdf_path = tmp.name
        loader = PyMuPDFLoader(temp_pdf_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata.update(metadata)
        return docs
    except Exception as e:
        print(f"    ⚠️  Error processing PDF: {e}")
        return []
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


# ── Single worker ─────────────────────────────────────────────────────────────
def _worker_embed(
    worker_id: int,
    api_key: str,
    batches: List[List[Document]],
) -> Optional[FAISS]:
    """
    One worker embeds all its assigned batches using its own dedicated API key
    from a separate Google account — fully independent quota, no sharing.

    On 429 quota exhaustion: waits 65 seconds for the quota window to reset.
    On other errors: exponential backoff.
    """
    embeddings = _make_embeddings(api_key)
    combined: Optional[FAISS] = None

    for batch_num, batch in enumerate(batches, 1):
        store = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                store = FAISS.from_documents(batch, embeddings)
                break  # success — exit retry loop
            except Exception as e:
                error_str = str(e)

                if attempt == MAX_RETRIES:
                    print(f"    ❌ Worker {worker_id} batch {batch_num} failed after {MAX_RETRIES} retries")
                    break

                # 429 quota exhausted — wait for full reset window
                if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                    print(f"    ⏳ Worker {worker_id} quota hit — waiting {QUOTA_WAIT}s for reset… (batch {batch_num})")
                    time.sleep(QUOTA_WAIT)
                # 500/503 server error — short backoff
                elif "500" in error_str or "503" in error_str:
                    wait = RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"    ⏳ Worker {worker_id} server error — retrying in {wait:.1f}s… (batch {batch_num})")
                    time.sleep(wait)
                # Any other error — short backoff
                else:
                    wait = RETRY_BASE_DELAY * (2 ** attempt)
                    print(f"    ⏳ Worker {worker_id} error — retrying in {wait:.1f}s… (batch {batch_num}, attempt {attempt + 1})")
                    time.sleep(wait)

        if store is None:
            continue  # skip failed batch, continue with rest

        if combined is None:
            combined = store
        else:
            combined.merge_from(store)

        print(f"    ✅ Worker {worker_id} | {batch_num}/{len(batches)} done")

    return combined


# ── Parallel coordinator ──────────────────────────────────────────────────────
def embed_chunks_parallel(chunks: List[Document]) -> Optional[FAISS]:
    """
    Distributes chunks across all API keys in round-robin fashion,
    then runs all workers simultaneously via ThreadPoolExecutor.

    With 3 keys from 3 different Google accounts:
    - Each key has its own independent quota
    - All 3 workers run at the same time
    - ~3x faster than sequential single-key embedding
    """
    num_keys = len(API_KEYS)

    # Build all batches first
    all_batches: List[List[Document]] = [
        chunks[i: i + EMBED_BATCH_SIZE]
        for i in range(0, len(chunks), EMBED_BATCH_SIZE)
    ]
    total_batches = len(all_batches)

    # Distribute round-robin across workers
    worker_batches: List[List[List[Document]]] = [[] for _ in range(num_keys)]
    for idx, batch in enumerate(all_batches):
        worker_batches[idx % num_keys].append(batch)

    print(f"    ⚡ {len(chunks)} chunks → {total_batches} batches → {num_keys} parallel worker(s)")
    for i, wb in enumerate(worker_batches):
        if wb:
            print(f"       Worker {i + 1} (Account {i + 1}): {len(wb)} batches")

    # Launch all workers in parallel
    results: List[Optional[FAISS]] = [None] * num_keys
    with ThreadPoolExecutor(max_workers=num_keys) as executor:
        future_to_idx = {
            executor.submit(
                _worker_embed,
                i + 1,
                API_KEYS[i],
                worker_batches[i],
            ): i
            for i in range(num_keys)
            if worker_batches[i]
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"    ❌ Worker {idx + 1} crashed: {e}")

    # Merge all worker results
    combined: Optional[FAISS] = None
    for store in results:
        if store is None:
            continue
        if combined is None:
            combined = store
        else:
            combined.merge_from(store)

    return combined


# ── Public API ────────────────────────────────────────────────────────────────
def ingest_documents(
    ticker: str,
    doc_targets: List[Dict],
    force: bool = False,
) -> bool:
    """
    Download, chunk, filter boilerplate, and embed PDFs for `ticker` into FAISS.

    doc_targets format:
        [{"url": str, "metadata": {"title": str, "type": str, "ticker": str}}]

    Already-ingested URLs are skipped unless force=True.
    Returns True if vector store is ready for querying.
    """
    ticker = ticker.upper().strip()
    db_path = os.path.join(VECTORSTORE_DIR, f"faiss_{ticker}")
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    # Load existing store if present
    existing_store: Optional[FAISS] = None
    if os.path.exists(db_path):
        try:
            existing_store = FAISS.load_local(
                db_path,
                _make_embeddings(API_KEYS[0]),
                allow_dangerous_deserialization=True,
            )
            print(f"  📂 Loaded existing vector store for {ticker}")
        except Exception:
            existing_store = None

    new_docs_added = False

    for target in doc_targets:
        url  = target["url"]
        meta = target["metadata"]

        if not force and is_already_ingested(ticker, url):
            print(f"    ✅ Already ingested: {meta.get('title', url)[:60]}")
            continue

        print(f"  📄 Downloading: {meta.get('title', url)[:60]}")
        raw_docs = download_and_extract(url, meta)
        if not raw_docs:
            continue

        chunks = splitter.split_documents(raw_docs)
        useful = [c for c in chunks if _is_useful_chunk(c.page_content)]
        print(f"    ✂️  {len(chunks)} chunks → {len(useful)} after boilerplate filter")

        if not useful:
            print(f"    ⚠️  No useful chunks found, skipping.")
            continue

        new_store = embed_chunks_parallel(useful)
        if new_store is None:
            print(f"    ⚠️  Embedding failed entirely for {meta.get('title', url)[:50]}")
            continue

        if existing_store is None:
            existing_store = new_store
        else:
            existing_store.merge_from(new_store)

        mark_ingested(ticker, url)
        new_docs_added = True

    if existing_store is None:
        print(f"  ⚠️  No embeddings available for {ticker}.")
        return False

    existing_store.save_local(db_path)
    if new_docs_added:
        print(f"  💾 Vector store saved → {db_path}")
    return True