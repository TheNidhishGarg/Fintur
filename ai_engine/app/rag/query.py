import os
import re
import json
from typing import Optional, List, Dict, Tuple
from datetime import datetime

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from app.tools.documents import fetch_company_documents
from app.rag.ingest import ingest_documents

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORSTORE_DIR = os.path.join(BASE_DIR, "data", "vector_stores")
EMBEDDING_MODEL = "gemini-embedding-001"

# How many results to surface per retrieval call
RETRIEVAL_K = 8


# ── Utilities ─────────────────────────────────────────────────────────────────
def _normalize_ticker(ticker: str) -> str:
    return ticker.upper().replace(".NS", "").strip()


def _extract_year(text: str) -> Optional[int]:
    m = re.search(r"\b(20\d{2})\b", text)
    return int(m.group(1)) if m else None


def _parse_concall_period(period: str) -> Tuple[int, str]:
    year_match = re.search(r"\b(20\d{2})\b", period)
    year = int(year_match.group(1)) if year_match else 0
    cleaned = period.strip()
    for fmt in ("%d %b %Y", "%d-%b-%Y", "%d %B %Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.year, dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return year, cleaned


def _detect_backtest_year(search_query: str) -> Optional[int]:
    text = search_query.lower()
    if "backtest" not in text and "backtesting" not in text:
        return None
    years = re.findall(r"\b(20\d{2})\b", search_query)
    return int(years[-1]) if years else None


# ── Document selection helpers ────────────────────────────────────────────────
def _select_annual_targets(
    doc_links: Dict,
    backtest_year: Optional[int],
    max_count: int = 2,
) -> List[Dict]:
    """
    Pick the most relevant annual report PDFs.

    - backtest mode  → report(s) from (backtest_year - 1)
    - current mode   → latest `max_count` reports
    """
    reports = doc_links.get("Annual_Reports", [])
    if not reports:
        return []

    year_doc: List[Tuple[int, Dict]] = []
    for item in reports:
        year = _extract_year(item.get("title", ""))
        if year and item.get("url"):
            year_doc.append((year, item))

    if not year_doc:
        return []

    year_doc.sort(key=lambda x: x[0], reverse=True)

    if backtest_year:
        target_year = backtest_year - 1
        filtered = [(y, d) for y, d in year_doc if y == target_year]
        if not filtered:
            filtered = [(y, d) for y, d in year_doc if y < target_year][:1]
        selected = filtered[:max_count]
    else:
        selected = year_doc[:max_count]

    return [
        {
            "url": d["url"],
            "metadata": {
                "title": d.get("title", f"Annual Report {y}"),
                "type": "Annual_Report",
                "year": y,
            },
        }
        for y, d in selected
    ]


def _select_concall_targets(
    doc_links: Dict,
    backtest_year: Optional[int],
    max_count: int = 3,
) -> List[Dict]:
    """
    Pick the most relevant concall transcripts.

    - backtest mode  → last `max_count` concalls within (backtest_year - 1)
    - current mode   → last `max_count` concalls overall
    """
    concalls = doc_links.get("Concall_Transcripts", [])
    if not concalls:
        return []

    entries: List[Tuple[int, str, Dict]] = []
    for item in concalls:
        if not item.get("url"):
            continue
        year, sort_key = _parse_concall_period(item.get("period", ""))
        entries.append((year, sort_key, item))

    if not entries:
        return []

    if backtest_year:
        target_year = backtest_year - 1
        entries = [e for e in entries if e[0] == target_year]

    entries.sort(key=lambda x: (x[0], x[1]), reverse=True)
    selected = entries[:max_count]

    return [
        {
            "url": item["url"],
            "metadata": {
                "title": f"Concall {item.get('period', sort_key)}",
                "type": "Concall_Transcript",
                "year": year,
            },
        }
        for year, sort_key, item in selected
    ]


# ── Main tool ─────────────────────────────────────────────────────────────────
@tool
def search_company_documents(ticker: str, search_query: str) -> str:
    """
    Searches Annual Reports and Concall transcripts for a company using
    semantic vector search (FAISS + Google embeddings).

    Documents are downloaded and embedded on first use, then cached locally —
    subsequent calls cost ZERO API embedding credits and return results instantly.

    Args:
        ticker (str): NSE ticker symbol, e.g. 'RELIANCE'.
        search_query (str): Natural-language question or topic to search for.
                            Include 'backtest YYYY' to restrict context to
                            documents from the year prior to YYYY.

    Returns:
        JSON string with retrieved passages and their source metadata.
    """
    norm_ticker = _normalize_ticker(ticker)
    db_path = os.path.join(VECTORSTORE_DIR, f"faiss_{norm_ticker}")
    backtest_year = _detect_backtest_year(search_query)

    # ── Step 1: Fetch document index from Screener ────────────────────────────
    url = f"https://www.screener.in/company/{norm_ticker}/consolidated/"
    doc_links = fetch_company_documents.invoke({"url": url})

    if not isinstance(doc_links, dict) or "error" in doc_links:
        return json.dumps(
            {"error": f"Could not fetch document links for {norm_ticker}.", "details": doc_links},
            indent=2,
        )

    # ── Step 2: Build ingestion targets ──────────────────────────────────────
    annual_targets  = _select_annual_targets(doc_links, backtest_year, max_count=2)
    concall_targets = _select_concall_targets(doc_links, backtest_year, max_count=3)
    all_targets = annual_targets + concall_targets

    if not all_targets:
        return json.dumps(
            {"message": f"No documents found on Screener for '{norm_ticker}'."},
            indent=2,
        )

    # ── Step 3: Ingest (skipped automatically for already-cached docs) ────────
    # Add ticker to every metadata dict
    for t in all_targets:
        t["metadata"]["ticker"] = norm_ticker

    success = ingest_documents(norm_ticker, all_targets)
    if not success:
        return json.dumps(
            {"error": f"Ingestion failed for {norm_ticker}. Check API key / network."},
            indent=2,
        )

    # ── Step 4: Retrieve relevant passages ───────────────────────────────────
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    try:
        vectorstore = FAISS.load_local(
            db_path, embeddings, allow_dangerous_deserialization=True
        )
    except Exception as e:
        return json.dumps({"error": f"Could not load vector store: {e}"}, indent=2)

    retriever = vectorstore.as_retriever(
        search_type="mmr",  # Maximal Marginal Relevance → diverse results
        search_kwargs={"k": RETRIEVAL_K, "fetch_k": RETRIEVAL_K * 3},
    )

    docs = retriever.invoke(search_query)

    if not docs:
        return json.dumps(
            {"message": f"No relevant passages found for: '{search_query}'."},
            indent=2,
        )

    # ── Step 5: Format and return ─────────────────────────────────────────────
    results = []
    for doc in docs:
        results.append(
            {
                "source": doc.metadata.get("title", "Unknown"),
                "type": doc.metadata.get("type", ""),
                "year": doc.metadata.get("year", ""),
                "page": doc.metadata.get("page", ""),
                "content": doc.page_content.strip(),
            }
        )

    return json.dumps(
        {
            "ticker": norm_ticker,
            "mode": "backtest" if backtest_year else "current",
            "backtest_year": backtest_year,
            "query": search_query,
            "results": results,
        },
        indent=2,
        ensure_ascii=False,
    )