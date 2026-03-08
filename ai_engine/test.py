import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('GOOGLE_API_KEY_1') or os.getenv('GOOGLE_API_KEY')
print(f"Using key: {key[:15]}...")

# ── Test 1: New google-genai SDK (used by langchain-google-genai 4.x) ─────────
print("\n--- Testing via new google-genai SDK ---")
try:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)

    models_to_try = [
        "text-embedding-004",
        "gemini-embedding-001",
        "models/text-embedding-004",
        "models/embedding-001",
    ]

    for model_name in models_to_try:
        try:
            result = client.models.embed_content(
                model=model_name,
                contents="test sentence",
            )
            print(f"✅ WORKS: {model_name} — vector length: {len(result.embeddings[0].values)}")
        except Exception as e:
            print(f"❌ FAILS: {model_name} — {str(e)[:100]}")

except ImportError as ie:
    print(f"google-genai not installed: {ie}")

# ── Test 2: List available embedding models ───────────────────────────────────
print("\n--- Available embedding models on your key ---")
try:
    from google import genai
    client = genai.Client(api_key=key)
    found = False
    for m in client.models.list():
        if "embed" in m.name.lower():
            print(f"  ✅ {m.name}")
            found = True
    if not found:
        print("  ❌ No embedding models found")
except Exception as e:
    print(f"❌ Could not list models: {e}")

# ── Test 3: LangChain wrapper ─────────────────────────────────────────────────
print("\n--- Testing via LangChain wrapper ---")
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    for model in ["text-embedding-004", "gemini-embedding-001", "models/text-embedding-004", "models/embedding-001"]:
        try:
            e = GoogleGenerativeAIEmbeddings(model=model, google_api_key=key)
            result = e.embed_query("test")
            print(f"✅ WORKS (langchain): {model} — length: {len(result)}")
        except Exception as ex:
            print(f"❌ FAILS (langchain): {model} — {str(ex)[:100]}")
except ImportError:
    print("langchain-google-genai not installed")