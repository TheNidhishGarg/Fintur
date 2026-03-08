import re
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from langchain.tools import tool


# ── Constants ─────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
}

BSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bseindia.com/",
    "Accept": "application/json, text/plain, */*",
}

# BSE filing category keywords that indicate order/contract/LOI disclosures
ORDER_KEYWORDS = [
    "order", "contract", "loi", "letter of intent", "award",
    "wins", "bagged", "secures", "receives", "project", "work order",
    "purchase order", "supply order", "epc", "bid", "tender",
]

# BSE subcategory codes for announcements (General + Investor Presentation)
BSE_ANNOUNCEMENT_CATS = ["Company Update", "Press Release", "Investor Presentation", "Others"]


# ── BSE scrip-code lookup ──────────────────────────────────────────────────────
def _get_bse_scrip_code(ticker: str) -> Optional[str]:
    """
    Resolve NSE ticker → BSE scrip code using BSE's own search API.
    Returns None if not found.
    """
    try:
        url = f"https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scripcode=&industry=&segment=Equity&status=Active&scrip={ticker}"
        resp = requests.get(url, headers=BSE_HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("Table", [])
        if items:
            return str(items[0].get("SCRIP_CD", ""))
    except Exception:
        pass

    # Fallback: try BSE search
    try:
        url2 = f"https://api.bseindia.com/BseIndiaAPI/api/fetchCompanyList/w?mktcap=&industry=&turn=&evalDate=&scripcode=&cname={ticker}&sector=&index=&igroup=&isubgroup=&srcappid=3&Type=EQ"
        resp2 = requests.get(url2, headers=BSE_HEADERS, timeout=10)
        resp2.raise_for_status()
        data2 = resp2.json()
        items2 = data2.get("Table", [])
        if items2:
            return str(items2[0].get("SCRIP_CD", ""))
    except Exception:
        pass

    return None


# ── BSE filings fetcher ────────────────────────────────────────────────────────
def _fetch_bse_filings(scrip_code: str, months_back: int = 12) -> List[Dict]:
    """
    Fetch exchange announcements from BSE for the given scrip code
    covering the last `months_back` months.

    Returns a list of filing dicts filtered to order/contract/LOI relevant ones.
    """
    end_date   = datetime.today()
    start_date = end_date - timedelta(days=30 * months_back)

    from_str = start_date.strftime("%Y%m%d")
    to_str   = end_date.strftime("%Y%m%d")

    url = (
        f"https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
        f"?strCat=-1&strType=C&strScrip={scrip_code}"
        f"&strSearch=P&strToDate={to_str}&strFromDate={from_str}&myDelay=1"
    )

    try:
        resp = requests.get(url, headers=BSE_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return [{"error": f"BSE filings fetch failed: {str(e)}"}]

    filings = data.get("Table", []) or []
    results = []

    for f in filings:
        headline   = f.get("NEWSSUB", "") or ""
        news_body  = f.get("NEWSBODY", "") or ""
        attachment = f.get("ATTACHMENTNAME", "") or ""
        news_dt    = f.get("NEWS_DT", "") or ""
        news_id    = f.get("NEWSID", "") or ""

        combined_text = (headline + " " + news_body).lower()

        # Filter: only keep order/contract/LOI related filings
        is_relevant = any(kw in combined_text for kw in ORDER_KEYWORDS)
        # Also keep investor presentations regardless of keywords
        is_presentation = "presentation" in combined_text or attachment.lower().endswith(".pdf")

        if not (is_relevant or is_presentation):
            continue

        # Build PDF URL if attachment exists
        pdf_url = None
        if attachment:
            pdf_url = f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{attachment}"

        results.append({
            "headline":  headline.strip(),
            "date":      news_dt,
            "news_id":   news_id,
            "pdf_url":   pdf_url,
            "is_order_related": is_relevant,
            "is_presentation":  is_presentation,
        })

    return results


# ── Screener scraper ───────────────────────────────────────────────────────────
def _fetch_screener_documents(url: str) -> Dict:
    """Scrape Annual Reports, Concall Transcripts, and Investor PPTs from Screener."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        docs = {
            "Annual_Reports":         [],
            "Concall_Transcripts":    [],
            "Investor_Presentations": [],
        }

        # Annual Reports
        ar_container = soup.select_one(".documents.annual-reports")
        if ar_container:
            for link in ar_container.find_all("a"):
                href = link.get("href", "")
                if href.lower().endswith(".pdf"):
                    docs["Annual_Reports"].append({
                        "title": link.text.strip().split("\n")[0].strip(),
                        "url":   href,
                    })

        # Concalls & PPTs
        cc_container = soup.select_one(".documents.concalls")
        if cc_container:
            for li in cc_container.find_all("li"):
                date_el     = li.find("div", class_="ink-600")
                period_date = date_el.text.strip() if date_el else "Unknown"

                for link in li.find_all("a", class_="concall-link"):
                    href     = link.get("href", "")
                    doc_type = link.text.strip()
                    if not href.lower().endswith(".pdf"):
                        continue
                    entry = {"period": period_date, "url": href}
                    if doc_type == "Transcript":
                        docs["Concall_Transcripts"].append(entry)
                    elif doc_type == "PPT":
                        docs["Investor_Presentations"].append(entry)

        return docs

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error fetching Screener: {str(e)}"}
    except Exception as e:
        return {"error": f"Screener scrape failed: {str(e)}"}


# ── Public tool ───────────────────────────────────────────────────────────────
@tool
def fetch_company_documents(url: str, fetch_bse_filings: bool = True) -> Dict:
    """
    Fetches ALL high-value company documents in a single call:

    1. Screener.in  → Annual Reports, Concall Transcripts, Investor PPTs
    2. BSE Exchange → Order/contract/LOI announcements + Investor Presentations
                      filed in the last 12 months (auto-resolved from ticker)

    Args:
        url (str): Full Screener.in company URL,
                   e.g. 'https://www.screener.in/company/RELIANCE/consolidated/'
        fetch_bse_filings (bool): Set False to skip BSE lookup (faster, fewer requests).

    Returns:
        dict with keys:
            Annual_Reports, Concall_Transcripts, Investor_Presentations  ← from Screener
            BSE_Order_Filings, BSE_Presentations                         ← from BSE
            bse_scrip_code                                               ← for reference
    """
    # Extract ticker from URL
    ticker_match = re.search(r"/company/([^/]+)/", url)
    ticker = ticker_match.group(1).upper() if ticker_match else ""

    # ── 1. Screener docs ──────────────────────────────────────────────────────
    screener_docs = _fetch_screener_documents(url)
    if "error" in screener_docs:
        return screener_docs  # Hard failure — Screener is primary

    result = dict(screener_docs)
    result["BSE_Order_Filings"]  = []
    result["BSE_Presentations"]  = []
    result["bse_scrip_code"]     = None

    if not fetch_bse_filings or not ticker:
        if not any(screener_docs.values()):
            return {"error": "No documents found on Screener and BSE lookup skipped."}
        return result

    # ── 2. BSE scrip code lookup ───────────────────────────────────────────────
    scrip_code = _get_bse_scrip_code(ticker)
    result["bse_scrip_code"] = scrip_code

    if not scrip_code:
        # Non-fatal — return what we have from Screener
        result["bse_note"] = f"Could not resolve BSE scrip code for {ticker}. BSE filings skipped."
        return result

    # ── 3. BSE filings ─────────────────────────────────────────────────────────
    time.sleep(0.5)  # polite delay between Screener and BSE requests
    bse_filings = _fetch_bse_filings(scrip_code, months_back=12)

    for filing in bse_filings:
        if filing.get("error"):
            result["bse_note"] = filing["error"]
            continue
        if filing.get("is_order_related"):
            result["BSE_Order_Filings"].append(filing)
        if filing.get("is_presentation") and filing.get("pdf_url"):
            result["BSE_Presentations"].append(filing)

    if not any(result[k] for k in ["Annual_Reports", "Concall_Transcripts",
                                    "BSE_Order_Filings", "BSE_Presentations"]):
        return {"error": "No valid documents found from Screener or BSE."}

    return result