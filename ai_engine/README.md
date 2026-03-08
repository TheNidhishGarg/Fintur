## Investment Advisor – Project Overview

### 1. What this project is

**Investment Advisor** is an India-focused research and planning toolkit built around two separate AI agents:

- **Agent A – “Arjun” Personal Portfolio Advisor + ETF SIP Backtester**
- **Agent B – “Indian Stock Analyst” Single-Stock Research Agent**

Both agents run in the terminal, use Google Gemini 2.5 Flash via LangChain/LangGraph, and share a common data/RAG layer (Screener, BSE, yfinance, Tavily, PDF embeddings).

For deeper docs:
- **Human overview**: `README_HUMAN.md`
- **AI/backend integration notes**: `README_AI.md`

---

### 2. Repository structure (key parts)

- `agent1advisor.py` – Arjun conversational advisor (multi-step planning, JSON allocation, profile memory).
- `backtester.py` – ETF SIP backtester driven by Arjun’s allocation JSON and `ETFS.json`.
- `main_app.py` – Single-stock “Indian Stock Analyst” ReAct agent.
- `app/tools/` – Shared tools:
  - `documents.py` – Screener + BSE filings/document index.
  - `fundamental.py` – Screener fundamentals + peers.
  - `technical.py` – yfinance OHLCV + indicators.
  - `news.py` – Tavily financial news search.
  - `orderbook.py` – Order book synthesis (RAG + news + BSE).
- `app/rag/` – RAG ingestion and search:
  - `ingest.py` – PDF download, chunking, parallel embeddings into FAISS.
  - `query.py` – Semantic search over annual reports & concalls.
  - `data/vector_stores/` – **Embeddings per ticker (e.g. HCL)** – commit this folder so others can re-use the vector DB.
- `ETFS.json` – Curated ETF catalogue by asset class.
- `requirements.txt` – Python dependencies.

---

### 3. Agent A – Arjun + Backtester (high level)

- **Arjun terminal chatbot (`agent1advisor.py`)**
  - Uses a long, rule-based system prompt to:
    - Detect financial literacy level.
    - Run through phases: warm opening → wellness check (emergency fund, insurance) → investment profiling → contradiction checks → summary → explicit confirmation.
  - After confirmation it produces:
    - A natural-language explanation of the plan.
    - A **JSON portfolio allocation** printed after:
      - `--- PORTFOLIO ALLOCATION (JSON) ---`
  - Stores/updates user context in `user_profile.json` for future sessions.

- **ETF SIP backtester (`backtester.py`)**
  - Input: Arjun’s allocation JSON (single or multi-tenure).
  - Steps:
    - Parse `_sip_plan` and `allocation` blocks.
    - Auto-select a **“best affordable” ETF** per asset class using `ETFS.json` and live prices from `fetch_technical_data`.
    - Fetch 5-year historical data, run a monthly SIP simulation with no fractional units.
    - Compute final value, gains, year-wise summary, and XIRR.
  - Output:
    - Pretty-printed report in the terminal.
    - Full JSON result (summary, yearly_summary, final_holdings, monthly_detail) which can be saved as `backtest_results.json`.

Arjun and the backtester are **loosely coupled**: Arjun is the conversation and allocation “brain”, and the backtester is a separate computation engine that only runs once a valid allocation JSON exists.

---

### 4. Agent B – Single-Stock Indian Stock Analyst

- Implemented in `main_app.py` using LangGraph’s `create_react_agent`.
- System prompt defines the agent as a **Senior Hedge Fund Analyst** focused on long-term value investing in NSE/BSE.
- Tools used:
  - `fetch_company_documents` → Screener + BSE docs + order-related filings.
  - `fetch_screener_fundamentals` → fundamentals and peers via Screener.
  - `fetch_technical_data` → OHLCV + EMA/SMA/RSI/MACD/Bollinger/ATR.
  - `fetch_stock_news` → Tavily-based curated financial news.
  - `fetch_order_book` → order book assessment (RAG + news + BSE, with optional revenue).
  - `search_company_documents` → semantic search over AR + concalls.
- For each user query (e.g. “Analyze HCL Tech for 5+ years”):
  - The ReAct agent decides which tools to call, in what order.
  - Synthesizes a structured report:
    - Executive Summary (Buy/Hold/Avoid).
    - Fundamental analysis.
    - Order book and revenue visibility.
    - Technical analysis.
    - Document-based insights (AR + concalls).
    - News and sentiment.
    - Risk assessment and final recommendation.

This agent is **ticker-centric** and stateless between runs (no profile JSON).

---

### 5. RAG and data layer

- **Document indexing (`app/tools/documents.py`)**
  - Scrapes Screener company pages for:
    - Annual reports, concall transcripts, investor presentations.
  - Resolves NSE ticker → BSE scrip code.
  - Collects 12 months of BSE filings, filtering for order/contract/LOI and presentations.

- **PDF ingestion and embeddings (`app/rag/ingest.py`)**
  - Downloads PDFs using requests + PyMuPDF.
  - Splits text with `RecursiveCharacterTextSplitter`.
  - Filters boilerplate (auditor reports, statutory legal sections).
  - Embeds chunks into FAISS using `GoogleGenerativeAIEmbeddings`:
    - Uses `GOOGLE_API_KEY_1..3` in parallel if available for faster embedding.
  - Saves one FAISS index per ticker under `app/data/vector_stores/`.
  - `ingest_manifest.json` tracks which URLs are already ingested.

- **RAG queries (`app/rag/query.py`)**
  - `search_company_documents(ticker, search_query)`:
    - Chooses which AR + concalls to ingest.
    - Ensures embeddings exist.
    - Runs semantic retrieval with Maximal Marginal Relevance.
    - Returns JSON with metadata and snippets.

> **Note:** The `app/data/vector_stores/` folder (including the HCL FAISS index) is meant to be stored in Git so that others can run the project without re-embedding from scratch.

---

### 6. Setup & environment

- **Python version**
  - Recommended: Python 3.10+.
- **Install dependencies**
  - From inside the `investment advisor` folder:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    ```
- **Environment variables** (via `.env` or system env):
  - `GOOGLE_API_KEY` – main Gemini key.
  - `GOOGLE_API_KEY_1`, `GOOGLE_API_KEY_2`, `GOOGLE_API_KEY_3` – optional extra keys for faster embeddings.
  - `TAVILY_API_KEY` – Tavily search key.

Place `.env` in the `investment advisor` folder; it is ignored by Git via `.gitignore`.

---

### 7. How to run

- **Run Arjun advisor**
  ```bash
  python agent1advisor.py
  ```
  - Chat in the terminal until Arjun summarizes your situation and you confirm.
  - When allocation JSON is generated, Arjun:
    - Saves your profile to `user_profile.json`.
    - Optionally runs the ETF backtester and saves `backtest_results.json`.

- **Run ETF backtester directly (optional)**
  ```bash
  python backtester.py
  ```
  - Uses a sample allocation embedded in the file.
  - Useful for quick testing without running the full Arjun conversation.

- **Run Indian Stock Analyst**
  ```bash
  python main_app.py
  ```
  - Type queries like:
    - `Analyze HCLTECH for long-term`
    - `Backtest HAL in 2024`
  - The agent will fetch documents, data, and news, then print a structured thesis.

---

### 8. GitHub and data considerations

- This repository is designed to be **GitHub-ready**:
  - `requirements.txt` lists all Python dependencies.
  - `.gitignore` (in this folder) ignores:
    - Virtual environments, caches, `.env`, editor files, and runtime JSON like `user_profile.json` / `backtest_results.json`.
  - The **RAG vector store** under `app/data/vector_stores/` is intentionally **not** ignored so that:
    - Pre-computed indices (e.g. for HCL) can be reused by others.
    - New users can clone and immediately run analyses and backtests without paying embedding costs again.

For more detail, see `README_HUMAN.md` (narrative explanation) and `README_AI.md` (API/integration guide).

