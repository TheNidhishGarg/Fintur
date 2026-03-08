import os
import re
import json
import time
from typing import Optional, List, Dict, Tuple

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from app.tools.news import fetch_stock_news
from app.rag.query import search_company_documents

load_dotenv()

# ── LLM — lazy initialized to avoid import-time API key error ─────────────────
_llm = None

def _get_llm() -> ChatGoogleGenerativeAI:
    """Return LLM instance, creating it on first call after .env is loaded."""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            max_retries=3,
        )
    return _llm

# ── Regex patterns to extract monetary values ─────────────────────────────────
# Matches patterns like: ₹12,500 Cr / Rs. 8000 crore / INR 5.2 billion / USD 200 mn
_MONEY_PATTERNS = [
    r"(?:₹|rs\.?|inr)\s*([\d,]+(?:\.\d+)?)\s*(?:,000)?\s*(?:cr(?:ore)?s?|billion|mn|million|lakh)",
    r"([\d,]+(?:\.\d+)?)\s*(?:cr(?:ore)?s?|billion|mn|million)\s*(?:order|contract|book|backlog|pipeline)",
    r"order\s+book\s+(?:of|at|stands?\s+at|worth|valued?\s+at)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:cr(?:ore)?s?|billion|mn|million)",
    r"backlog\s+(?:of|at|stands?\s+at)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:cr(?:ore)?s?|billion|mn|million)",
    r"unexecuted\s+order[s]?\s+(?:of|worth|valued?\s+at)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:cr(?:ore)?s?|billion|mn|million)",
]

_REVENUE_PATTERNS = [
    r"revenue\s+(?:of|at|was|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:cr(?:ore)?s?|billion|mn|million)",
    r"(?:net\s+)?sales\s+(?:of|at|was|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:cr(?:ore)?s?|billion|mn|million)",
    r"turnover\s+(?:of|at|was|is|:)?\s*(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:cr(?:ore)?s?|billion|mn|million)",
]


def _parse_amount_cr(text: str, patterns: List[str]) -> Optional[float]:
    """
    Try each regex pattern on text; return first matched value normalised to ₹ Cr.
    Handles conversion: billion→Cr (*100), mn/million→Cr (/100), lakh→Cr (/100).
    """
    text_lower = text.lower()
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for raw in matches:
            try:
                val = float(raw.replace(",", ""))
                # Normalise unit
                context = text_lower[max(0, text_lower.find(raw)-5) : text_lower.find(raw)+len(raw)+20]
                if any(u in context for u in ["billion"]):
                    val = val * 100   # 1 billion ≈ 100 Cr (rough, for INR context)
                elif any(u in context for u in ["mn", "million"]):
                    val = val / 100   # 1 million ≈ 0.01 Cr — actually just keep as Cr signal
                    val = val * 10    # adjust: 1 mn = 10 lakh = 0.1 Cr → * 0.1
                elif any(u in context for u in ["lakh"]):
                    val = val / 100
                return round(val, 2)
            except (ValueError, TypeError):
                continue
    return None


# ── LLM query generation ───────────────────────────────────────────────────────
def _generate_rag_queries(ticker: str, sector_hint: str = "") -> List[str]:
    """
    Ask the LLM to generate the most relevant RAG queries to extract
    order book information from concalls and annual reports.
    """
    prompt = f"""
You are a financial analyst. Generate exactly 3 highly specific search queries
to extract ORDER BOOK information from a company's annual reports and concall transcripts.

Company ticker: {ticker}
Sector hint: {sector_hint or "Unknown — generate general queries"}

Rules:
- Queries must target order book SIZE, INFLOWS, and MANAGEMENT GUIDANCE.
- Focus on: current backlog value, order inflow this quarter/year, and book-to-bill ratio.
- Each query should be a SHORT natural-language phrase (5-12 words).
- Return ONLY a JSON array of 3 strings. No explanation, no markdown.

Example format: ["order book size current value crore", "order inflows quarterly FY25", "book to bill ratio"]
"""
    try:
        response = _get_llm().invoke(prompt)
        content = response.content.strip()
        # Strip markdown fences if present
        content = re.sub(r"```(?:json)?", "", content).strip().rstrip("```").strip()
        queries = json.loads(content)
        if isinstance(queries, list):
            return [str(q) for q in queries[:3]]
    except Exception:
        pass

    # Hardcoded fallback queries
    return [
        "current order book value backlog crore",
        "order inflows wins received this quarter year",
        "book to bill ratio revenue visibility",
    ]


# ── News queries for order wins ────────────────────────────────────────────────
def _build_news_queries(ticker: str) -> List[str]:
    return [
        f"{ticker} order win contract awarded 2024 2025",
        f"{ticker} LOI letter of intent new project",
        f"{ticker} wins secures bags order crore",
        f"{ticker} order book backlog update management",
    ]


# ── BSE filing text extractor ──────────────────────────────────────────────────
def _extract_orderbook_from_bse_filings(bse_filings: List[Dict]) -> List[Dict]:
    """
    Parse BSE order-related filing headlines for order size mentions.
    Returns structured list of {date, headline, amount_cr}.
    """
    extracted = []
    for filing in bse_filings:
        if filing.get("error"):
            continue
        headline = filing.get("headline", "")
        date     = filing.get("date", "")
        amount   = _parse_amount_cr(headline, _MONEY_PATTERNS)
        extracted.append({
            "date":      date,
            "headline":  headline,
            "amount_cr": amount,
            "pdf_url":   filing.get("pdf_url"),
        })
    return extracted


# ── Main synthesis ─────────────────────────────────────────────────────────────
def _synthesize_orderbook(
    ticker: str,
    rag_results: str,
    news_results: List[Dict],
    bse_order_data: List[Dict],
    ltm_revenue_cr: Optional[float],
) -> Dict:
    """
    Ask the LLM to synthesize all sources into a structured order book assessment.
    """
    prompt = f"""
You are a Senior Equity Analyst specializing in Indian listed companies.

Synthesize the following data sources to produce a structured ORDER BOOK ASSESSMENT
for {ticker}.

## RAG Results (Annual Reports + Concalls):
{rag_results}

## Recent News (Order Wins + Contracts):
{json.dumps(news_results[:10], indent=2, ensure_ascii=False)}

## BSE Exchange Filings (Order/Contract Announcements, last 12 months):
{json.dumps(bse_order_data, indent=2, ensure_ascii=False)}

## LTM Revenue (if available): {f'₹{ltm_revenue_cr} Cr' if ltm_revenue_cr else 'Not provided'}

Your task — extract and return ONLY a JSON object with these exact keys:

{{
  "latest_order_book_cr": <float or null>,         // Most recently stated total order book in ₹ Cr
  "order_book_date": "<string or null>",           // When this figure was stated (e.g. "Q3 FY25")
  "order_inflow_annual_cr": <float or null>,       // Annual order inflow run-rate in ₹ Cr if mentioned
  "ltm_revenue_cr": <float or null>,               // LTM revenue used for B2B ratio
  "book_to_bill_ratio": <float or null>,           // order_book / ltm_revenue (calculate if both available)
  "order_book_trend": "<Growing | Stable | Declining | Unknown>",
  "key_order_wins": [                              // Top 3-5 recent order wins with amounts
    {{"description": "...", "amount_cr": <float or null>, "date": "..."}}
  ],
  "revenue_visibility_years": <float or null>,     // Approx years of revenue covered by order book
  "management_guidance": "<string>",               // Direct management quote/paraphrase on order book
  "data_confidence": "<High | Medium | Low>",      // How confident are you in the figures?
  "sources_used": ["RAG", "News", "BSE Filings"],  // Which sources had useful data
  "analyst_note": "<2-3 sentence commentary>"      // Your qualitative assessment
}}

Rules:
- Return ONLY the JSON object. No markdown, no explanation.
- If a value cannot be determined, use null.
- Calculate book_to_bill_ratio = latest_order_book_cr / ltm_revenue_cr if both are available.
- revenue_visibility_years = latest_order_book_cr / (ltm_revenue_cr / 1) if available.
"""
    try:
        response = _get_llm().invoke(prompt)
        content = response.content.strip()
        content = re.sub(r"```(?:json)?", "", content).strip().rstrip("```").strip()
        return json.loads(content)
    except Exception as e:
        return {
            "error": f"Synthesis failed: {str(e)}",
            "raw_rag_snippet": rag_results[:500],
        }


# ── Public tool ───────────────────────────────────────────────────────────────
@tool
def fetch_order_book(
    ticker: str,
    sector_hint: str = "",
    ltm_revenue_cr: Optional[float] = None,
    bse_order_filings: Optional[List[Dict]] = None,
) -> str:
    """
    Comprehensive order book tracker for Indian listed companies.

    Since order book data has no official API, this tool triangulates from:
    1. RAG search on Annual Reports & Concalls (LLM-generated targeted queries)
    2. Recent news via Tavily (order win announcements)
    3. BSE exchange filings (contract/LOI disclosures from last 12 months)

    Outputs latest order book size (₹ Cr), Book-to-Bill ratio, order inflow trend,
    key recent order wins, revenue visibility, and management guidance.

    Args:
        ticker (str): NSE ticker e.g. 'LT', 'HAL', 'LTTS'.
        sector_hint (str): Optional sector e.g. 'Infrastructure', 'Defense', 'IT Services'.
                           Improves LLM query generation quality.
        ltm_revenue_cr (float | None): Last twelve months revenue in ₹ Cr.
                                        Pass from fetch_screener_fundamentals for accurate B2B ratio.
        bse_order_filings (list | None): Pass the BSE_Order_Filings list from
                                          fetch_company_documents to avoid a redundant API call.

    Returns:
        JSON string with full order book assessment.
    """
    norm_ticker = ticker.upper().replace(".NS", "").strip()

    # ── Step 1: Generate targeted RAG queries via LLM ─────────────────────────
    print(f"🧠 Generating RAG queries for {norm_ticker} order book…")
    rag_queries = _generate_rag_queries(norm_ticker, sector_hint)

    # ── Step 2: Run RAG searches (batched, uses cached vector store) ──────────
    print(f"🔍 Running {len(rag_queries)} RAG searches…")
    all_rag_text = []
    for q in rag_queries:
        try:
            result_str = search_company_documents.invoke({
                "ticker": norm_ticker,
                "search_query": q,
            })
            result = json.loads(result_str)
            if "results" in result:
                for r in result["results"]:
                    snippet = f"[{r.get('source','')} | {r.get('year','')}] {r.get('content','')}"
                    all_rag_text.append(snippet)
            time.sleep(0.3)  # small pause between RAG calls
        except Exception:
            continue

    rag_combined = "\n\n".join(all_rag_text) if all_rag_text else "No RAG results available."

    # ── Step 3: News search for order wins ────────────────────────────────────
    print(f"📰 Fetching order-win news for {norm_ticker}…")
    news_queries = _build_news_queries(norm_ticker)
    try:
        news_results = fetch_stock_news.invoke({
            "ticker": norm_ticker,
            "queries": news_queries,
            "max_results_per_query": 3,
        })
    except Exception:
        news_results = []

    # ── Step 4: Process BSE filings ───────────────────────────────────────────
    bse_structured = []
    if bse_order_filings:
        bse_structured = _extract_orderbook_from_bse_filings(bse_order_filings)
        print(f"📋 Processed {len(bse_structured)} BSE order filings.")
    else:
        print("ℹ️  No BSE filings passed — pass bse_order_filings from fetch_company_documents for richer data.")

    # ── Step 5: Synthesize everything ─────────────────────────────────────────
    print(f"⚙️  Synthesizing order book assessment for {norm_ticker}…")
    assessment = _synthesize_orderbook(
        ticker=norm_ticker,
        rag_results=rag_combined,
        news_results=news_results if isinstance(news_results, list) else [],
        bse_order_data=bse_structured,
        ltm_revenue_cr=ltm_revenue_cr,
    )

    # Attach raw BSE order filings for agent reference
    assessment["bse_order_filings_raw"] = bse_structured[:10]  # top 10 for context

    return json.dumps(
        {
            "ticker": norm_ticker,
            "sector_hint": sector_hint or "Not specified",
            "order_book_assessment": assessment,
        },
        indent=2,
        ensure_ascii=False,
    )