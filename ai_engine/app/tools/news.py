import os
import time
from typing import Union, List, Dict
from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")
if not api_key:
    raise ValueError("CRITICAL ERROR: 'TAVILY_API_KEY' not found in .env file.")

tavily_client = TavilyClient(api_key=api_key)

FINANCIAL_DOMAINS = [
    "moneycontrol.com",
    "economictimes.indiatimes.com",
    "livemint.com",
    "cnbctv18.com",
    "business-standard.com",
    "bseindia.com",
    "nseindia.com",
    "financialexpress.com",
]

DELAY_BETWEEN_SEARCHES = 1.0  # seconds — avoids Tavily rate limits on multi-query calls


def _single_search(query: str, max_results: int = 5) -> List[Dict]:
    """Run one Tavily search and return cleaned results."""
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_domains=FINANCIAL_DOMAINS,
        )
        results = []
        for r in response.get("results", []):
            results.append({
                "title":   r.get("title"),
                "source":  r.get("url"),
                "date":    r.get("published_date", "Recent"),
                "content": r.get("content"),
                "query":   query,   # tag so caller knows which query produced this
            })
        return results
    except Exception as e:
        return [{"error": f"Tavily search failed for query '{query}': {str(e)}", "query": query}]


@tool
def fetch_stock_news(
    ticker: str,
    queries: Union[str, List[str], None] = None,
    max_results_per_query: int = 5,
) -> List[Dict]:
    """
    Fetches deep financial news and market intelligence using Tavily AI.

    Supports a SINGLE default query (backwards compatible) OR a LIST of targeted
    queries — enabling the order-book tool and the LLM to run multiple focused
    searches in one tool call.

    Args:
        ticker (str): NSE stock symbol e.g. 'RELIANCE', 'L&T', 'TATASTEEL'.
        queries (str | list[str] | None):
            - None  → runs the default broad financial news query for the ticker.
            - str   → runs that single custom query.
            - list  → runs each query in the list and merges de-duplicated results.
        max_results_per_query (int): Tavily results per query (default 5).

    Returns:
        list[dict]: De-duplicated news items with title, source, date, content, query.
    """
    clean_ticker = ticker.upper().replace(".NS", "").strip()

    # ── Build query list ──────────────────────────────────────────────────────
    if queries is None:
        query_list = [
            f"{clean_ticker} India stock news analysis quarterly results "
            f"future growth targets capex plans government policy sector outlook"
        ]
    elif isinstance(queries, str):
        query_list = [queries]
    else:
        query_list = list(queries)

    # ── Run searches ──────────────────────────────────────────────────────────
    all_results: List[Dict] = []
    seen_urls = set()

    for i, query in enumerate(query_list):
        results = _single_search(query, max_results=max_results_per_query)
        for r in results:
            url = r.get("source", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(r)
        # Pause between queries to respect rate limits
        if i < len(query_list) - 1:
            time.sleep(DELAY_BETWEEN_SEARCHES)

    if not all_results:
        return [{"error": f"No significant news found for {clean_ticker}."}]

    return all_results