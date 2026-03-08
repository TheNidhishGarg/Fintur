## Investment Advisor – AI Integration Notes

This document is for an AI or backend service that will expose this project via APIs (e.g., FastAPI) and connect it to a frontend.

---

### 1. Runtime & Configuration

- **Python environment**
  - Install dependencies from `requirements.txt`.
- **Required environment variables**
  - `GOOGLE_API_KEY` – used by `main_app.py` and most LangChain tools.
  - `GOOGLE_API_KEY_1`, `GOOGLE_API_KEY_2`, `GOOGLE_API_KEY_3` (optional) – used by `app/rag/ingest.py` for parallel embeddings; falls back to `GOOGLE_API_KEY` if absent.
  - `TAVILY_API_KEY` – required by `app/tools/news.py` for Tavily search.
- **Important local files**
  - `ETFS.json` – ETF catalogue used by `backtester.py`.
  - `user_profile.json` – created/updated by `agent1advisor.py`.
  - `backtest_results.json` – written by `run_backtest_flow` / `backtester.py`.
  - `app/rag/data/vector_stores/faiss_{TICKER}` – FAISS indices per ticker.

---

### 2. High-Level Services to Expose

Treat the project as three logical services that can be surfaced as API endpoints.

#### 2.1 Stock Analysis Service (Agent B – `main_app.py`)

- **Purpose**
  - Given a natural-language query (typically including a ticker), return an institutional-style value-investing report.
- **Current implementation**
  - `main_app.py`:
    - Creates a `ChatGoogleGenerativeAI` model.
    - Wraps it in a ReAct agent via `create_react_agent(model=llm, tools=tools, prompt=SYSTEM_PROMPT)`.
    - Calls:
      - `result = agent.invoke({"messages": [HumanMessage(content=query)]})`
      - Final answer is `result["messages"][-1].content`.
- **Suggested API contract**
  - **POST /analyze-stock**
    - Input:
      ```json
      { "query": "Analyze L&T for long-term investment" }
      ```
    - Output:
      ```json
      { "analysis": "full final LLM reply as string" }
      ```

#### 2.2 Advisor Conversation Service (Agent A – `agent1advisor.py`, without backtest)

- **Purpose**
  - Maintain a stateful conversation that ends with a portfolio allocation JSON.
- **Core logic**
  - Build `system_prompt = build_system_prompt(existing_profile)` where `existing_profile` comes from `user_profile.json`.
  - Maintain `conversation_history: list[(role, content)]`.
  - For each user message:
    - Build:
      - `messages = [SystemMessage(system_prompt), ...history..., HumanMessage(user_input)]`
    - Call:
      - `response = llm.invoke(messages)`
    - Append `("assistant", response.content)` to history.
  - If `response.content` contains:
    - `"--- PORTFOLIO ALLOCATION (JSON) ---"`:
      - Split at that marker:
        - Part 1: conversational explanation.
        - Part 2: raw JSON string (may include ```json``` fences).
      - Clean and parse JSON:
        - `cleaned_json = re.sub(r"```json|```", "", json_part).strip()`
        - `parsed = json.loads(cleaned_json)`
      - Validate each block via `validate_allocation(parsed)` (sums must be 100).
      - Persist profile via `save_session_profile`.
- **Recommended API shape**
  - You should externalize `conversation_history` and `existing_profile` into your own storage keyed by `session_id`.
  - **POST /advisor/message**
    - Input:
      ```json
      {
        "session_id": "string",
        "user_message": "string"
      }
      ```
    - Output:
      ```json
      {
        "assistant_message": "string",
        "allocation_json": { ... } | null,
        "allocation_totals": { "label": 100, "...": 100 } | null
      }
      ```
    - When `allocation_json` is not null, the frontend can present the plan and optionally call the backtest service.

#### 2.3 ETF SIP Backtest Service (`backtester.py`)

- **Purpose**
  - Given a portfolio allocation JSON (same structure that Arjun emits), simulate a 5-year monthly SIP using ETFs and return performance metrics.
- **Core entrypoint**
  - `run_backtest_from_arjun(arjun_json: dict, years: int = 5) -> dict`
    - Calls:
      - `parse_arjun_allocation(arjun_json)` → returns `(allocation_dict, monthly_sip, label)`.
      - `auto_select_etfs(allocation, monthly_sip)` → picks best affordable ETF per asset class from `ETFS.json` using `fetch_technical_data.func` for live prices.
      - `run_backtest(allocation, etf_selections, monthly_sip, years)` → uses historical prices from `fetch_technical_data.func`.
- **Expected input JSON (conceptual)**
  - Single-tenure form:
    ```json
    {
      "_sip_plan": {
        "monthly_sip": 10000,
        "investment_vehicle": "ETFs"
      },
      "allocation": {
        "Large Cap": { "percentage": 30, "_comment": "reason..." },
        "Mid Cap":   { "percentage": 20, "_comment": "..." }
      }
    }
    ```
  - Multi-tenure form:
    ```json
    {
      "tenure_5yr_goalname": {
        "_sip_plan": { ... },
        "allocation": { ... }
      },
      "tenure_10yr_goalname": {
        "_sip_plan": { ... },
        "allocation": { ... }
      }
    }
    ```
- **Suggested API contract**
  - **POST /backtest**
    - Input:
      ```json
      {
        "allocation": { "...": "full Arjun JSON here" },
        "years": 5
      }
      ```
    - Output (simplified view of the Python dict):
      ```json
      {
        "summary": {
          "backtest_period": "string",
          "years": 5,
          "monthly_sip": 10000,
          "total_invested": 600000,
          "final_portfolio_value": 900000,
          "total_gains": 300000,
          "absolute_return_pct": 50.0,
          "xirr_pct": 15.0,
          "total_months": 60
        },
        "yearly_summary": {
          "2022": { "total_invested": 120000, "portfolio_value": 130000, "gains": 10000, "absolute_return_pct": 8.3 }
        },
        "final_holdings": {
          "Large Cap": {
            "ticker": "ETF1",
            "name": "Example ETF",
            "units_held": 100,
            "current_price": 100.0,
            "current_value": 10000.0,
            "allocation_pct": 30.0
          }
        },
        "monthly_detail": [ { "date": "YYYY-MM", "total_invested": ..., "portfolio_value": ..., "gains": ... } ]
      }
      ```

---

### 3. Tool Layer (Direct Use)

If you prefer to call tools directly from your backend instead of via LLM agents, these are the key contracts:

- **`fetch_company_documents(url: str, fetch_bse_filings: bool = True) -> dict`**
  - Input: Screener company URL like `https://www.screener.in/company/RELIANCE/consolidated/`.
  - Output keys:
    - `Annual_Reports`, `Concall_Transcripts`, `Investor_Presentations`,
    - `BSE_Order_Filings`, `BSE_Presentations`, `bse_scrip_code`,
    - optional `bse_note` or `error`.

- **`fetch_screener_fundamentals(ticker: str) -> dict`**
  - Input: NSE ticker symbol, normalized internally.
  - Output: mapping of table name → `pandas.DataFrame` (convert to JSON as needed).

- **`fetch_technical_data(ticker, period="5y", start_date=None, end_date=None) -> dict`**
  - Output:
    - `Daily_Data`: list of dicts (Date, OHLCV, EMA20, EMA50, SMA200, RSI, MACD, Bollinger, ATR).
    - `Weekly_Data_Full_History`: same structure, resampled weekly.

- **`search_company_documents(ticker, search_query) -> str (JSON)`**
  - Automatically handles embedding and caching of PDFs in FAISS.
  - Output JSON string with:
    - `ticker`, `mode` ("current" or "backtest"), `backtest_year`, `query`,
    - `results`: list of `{ source, type, year, page, content }`.

- **`fetch_stock_news(ticker, queries=None, max_results_per_query=5) -> list[dict]`**
  - Input:
    - `ticker`: NSE symbol.
    - `queries`: `None` (default broad query), `str` (single query), or `list[str]` (multi-query).
  - Output:
    - List of `{ title, source, date, content, query }` (de-duplicated by URL).

- **`fetch_order_book(ticker, sector_hint="", ltm_revenue_cr=None, bse_order_filings=None) -> str (JSON)`**
  - Uses:
    - LLM-generated RAG queries → `search_company_documents`.
    - Multi-query Tavily news → `fetch_stock_news`.
    - Optional `bse_order_filings` list (from `fetch_company_documents`).
  - Output JSON string with:
    - `ticker`, `sector_hint`,
    - `order_book_assessment`: object containing:
      - `latest_order_book_cr`, `order_book_date`,
      - `order_inflow_annual_cr`, `ltm_revenue_cr`,
      - `book_to_bill_ratio`, `order_book_trend`,
      - `key_order_wins`, `revenue_visibility_years`,
      - `management_guidance`, `data_confidence`,
      - `sources_used`, `analyst_note`,
      - plus `bse_order_filings_raw` (top 10 structured filings).

---

### 4. Design Notes for the Integrating AI

- Keep **Agent A (advisor)** and **Agent B (stock analyst)** logically separate:
  - Advisor: stateful, user-centric, produces allocation JSON.
  - Stock analyst: stateless per request, ticker-centric report.
- Use **three main endpoints**:
  - `/advisor/message` → stateful conversation.
  - `/backtest` → pure computation on allocation JSON.
  - `/analyze-stock` → single call per analysis.
- Replace file-based persistence (`user_profile.json`, `backtest_results.json`, FAISS directories) with your own storage layer if deploying in a multi-instance environment. Ensure paths and loading logic are updated consistently.

