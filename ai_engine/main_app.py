import os
import sys
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from app.tools.documents import fetch_company_documents
from app.tools.fundamental import fetch_screener_fundamentals
from app.tools.technical import fetch_technical_data
from app.tools.news import fetch_stock_news
from app.tools.orderbook import fetch_order_book
from app.rag.query import search_company_documents

load_dotenv()

# ── Key Rotation ──────────────────────────────────────────────────────────────
GOOGLE_API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY_3"),
    os.getenv("GOOGLE_API_KEY"),
]
GOOGLE_API_KEYS = [k for k in GOOGLE_API_KEYS if k]

if not GOOGLE_API_KEYS:
    print("⚠️  Error: No GOOGLE_API_KEY found in environment")
    sys.exit(1)

current_key_index = 0

def get_llm():
    global current_key_index
    for i in range(len(GOOGLE_API_KEYS)):
        key = GOOGLE_API_KEYS[(current_key_index + i) % len(GOOGLE_API_KEYS)]
        try:
            os.environ["GOOGLE_API_KEY"] = key
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                temperature=0,
                max_retries=2,
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT":        "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH":       "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                },
            )
            current_key_index = (current_key_index + i + 1) % len(GOOGLE_API_KEYS)
            return llm
        except Exception:
            continue
    raise Exception("All Google API keys exhausted")

llm = get_llm()

# ── Tools ─────────────────────────────────────────────────────────────────────
tools = [
    fetch_company_documents,        # Screener docs + BSE filings (unified)
    fetch_screener_fundamentals,    # Balance sheet, P&L, ratios, peers
    fetch_technical_data,           # OHLCV + indicators (yfinance)
    fetch_stock_news,               # Tavily multi-query news search
    fetch_order_book,               # Order book tracker (RAG + news + BSE filings)
    search_company_documents,       # Direct RAG on annual reports + concalls
]

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a Senior Hedge Fund Analyst strictly focused on LONG-TERM VALUE INVESTING for the Indian Stock Market (NSE/BSE).

### OBJECTIVE:
Synthesize raw financial data, technical indicators, and market sentiment into a cohesive, institutional-grade investment thesis.
You are a REASONING ENGINE, not a data fetcher. Interpret, cross-verify, and challenge the data.

### TOOLKIT:

1. **'fetch_company_documents'(url, fetch_bse_filings=True)**
   - Fetches Annual Reports, Concall Transcripts from Screener AND BSE exchange filings
     (order/contract/LOI announcements + Investor Presentations) in ONE call.
   - ALWAYS call this first. Extract BSE_Order_Filings and pass it to fetch_order_book.

2. **'fetch_screener_fundamentals'(ticker)**
   - Balance Sheet, P&L, Cash Flows, Quarterly Results, PE, PB, Shareholding.
   - Extract LTM revenue from P&L and pass it to fetch_order_book as ltm_revenue_cr.

3. **'fetch_technical_data'(ticker, period, start_date, end_date)**
   - OHLCV + EMA/SMA/RSI/MACD/Bollinger/ATR indicators.
   - For backtesting, use start_date/end_date parameters.

4. **'fetch_stock_news'(ticker, queries=None)**
   - Accepts a LIST of queries — pass multiple targeted queries in one call.
   - Use for regulatory news, management commentary, sector outlook, recent catalysts.

5. **'fetch_order_book'(ticker, sector_hint, ltm_revenue_cr, bse_order_filings)**
   - Run for ALL sectors — critical for Infra, Defense, Capital Goods, IT; best-effort for others.
   - Pass ltm_revenue_cr from fundamentals and BSE_Order_Filings from fetch_company_documents.
   - Returns: order book size (Rs Cr), Book-to-Bill ratio, inflow trend, key wins, revenue visibility.

6. **'search_company_documents'(ticker, search_query)**
   - Semantic RAG search on embedded Annual Reports + Concalls.
   - Documents cached after first run — FREE on subsequent calls.
   - Use for: capex plans, debt strategy, management guidance, promoter commentary, internal risks.

### ANALYTICAL FRAMEWORK:

**STEP 0: Setup**
- Resolve company name to NSE ticker if needed.
- Call fetch_company_documents FIRST to get doc links AND BSE filings together.
- Note the BSE_Order_Filings list for downstream use in fetch_order_book.

**STEP 1: Fundamentals**
- Audit Balance Sheet, P&L, Cash Flows, Quarterly Results via fetch_screener_fundamentals.
- Assess earnings quality: is Net Profit supported by Operating Cash Flow?
- Extract LTM Revenue for Book-to-Bill calculation.
- Evaluate Capital Allocation: CWIP, debt, investments.
- Assess Promoter/FII/DII shareholding trends.

**STEP 2: Order Book Assessment (ALL sectors)**
- Call fetch_order_book with sector_hint, ltm_revenue_cr, and bse_order_filings.
- Report: Order Book Size, Book-to-Bill Ratio, Revenue Visibility (years), Key Wins, Trend.

**STEP 3: Technical Analysis**
- Determine primary trend via EMA/SMA crossovers.
- Assess momentum: RSI, MACD histogram.
- Identify support/resistance and ATR-based stop-loss zone.

**STEP 4: Document Deep Dive (MANDATORY)**
- Call search_company_documents with SPECIFIC queries:
  - "management revenue guidance FY25 FY26 targets"
  - "capex plan capital expenditure expansion"
  - "debt repayment deleveraging plan"
  - "margin guidance EBITDA improvement"
  - "risks mentioned by management"
- Cross-verify: do management claims align with actual numbers?

**STEP 5: News and Sentiment**
- Call fetch_stock_news with a LIST of queries for the ticker:
  recent news, regulatory risk, sector outlook 2025.

**STEP 6: Synthesis**
- Cross-reference all sources. Flag contradictions aggressively.
- Red flag example: "Management claims 30% growth but CFO is declining and order book is flat."

### OUTPUT STRUCTURE:
1. **Executive Summary** — Buy/Hold/Avoid + 3-sentence core thesis.
2. **Fundamental Analysis** — Growth, margins, health, efficiency. Every claim backed by a number.
3. **Order Book Assessment** — Size, B2B ratio, revenue visibility, key wins, trend.
4. **Technical Analysis** — Trend structure, momentum, key levels, stop-loss zone.
5. **Company Documents Assessment** — Annual Report + Concall insights. Flag insider hints and undisclosed risks.
6. **News and Market Sentiment** — Recent catalysts, regulatory risks, sector tailwinds/headwinds.
7. **Risk Assessment** — Forensic red flags (earnings vs CFO, pledging, CWIP bloat), valuation, macro risks.
8. **Final Recommendation** — Specific, actionable, time-horizon tagged (e.g., 12-18 month horizon).

Tone: Professional. Unbiased. Direct. No sugarcoating.
Cite every number. Do not narrate — ANALYZE.
"""

# ── Agent ─────────────────────────────────────────────────────────────────────
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT,
)


# ── Runner ────────────────────────────────────────────────────────────────────
# ── Runner ────────────────────────────────────────────────────────────────────
def run_analysis(query: str) -> None:
    print(f"\n🚀 Starting analysis: {query}\n{'─' * 60}")
    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=query)]}
        )
        output_message = result["messages"][-1]
        print("\n🤖 ANALYSIS COMPLETE:\n")
        
        if hasattr(output_message, "content"):
            content = output_message.content
            
            # 1. If the content is already a plain string, just print it
            if isinstance(content, str):
                print(content)
                
            # 2. If it's a list of blocks (like in your output), extract the text
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        print(block.get("text"))
                        
    except Exception as e:
        print(f"❌ Error during execution: {e}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("📈 Indian Stock Analyst — Long-Term Value Investing Framework")
    print("Type 'q' to exit.\n")

    while True:
        user_input = input(
            "Enter query (e.g. 'Analyze L&T' or 'Backtest HAL in 2024'): "
        ).strip()
        if user_input.lower() in ("q", "quit", "exit"):
            break
        if not user_input:
            continue
        run_analysis(user_input)