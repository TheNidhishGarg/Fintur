## Investment Advisor – Human Overview

### 1. Project Goal

Build an India-focused investment assistant with:
- **Agent A – “Arjun” Personal Portfolio Advisor + ETF SIP Backtester**
- **Agent B – “Indian Stock Analyst” Single-Stock Research Agent**

Both agents run in the terminal and share a common data/tooling layer (Screener, BSE, yfinance, Tavily, RAG on PDFs).

---

### 2. Agent A – Arjun Portfolio Advisor (`agent1advisor.py` + `backtester.py`)

- **What Arjun does**
  - Talks to the user like a human advisor.
  - Understands age, income, SIP comfort, goals, tenures, risk, emergency fund, insurance, and preferences.
  - Enforces a strict conversation flow (warm intro → wellness check → profiling → contradiction checks → summary → explicit confirmation).
  - After the user confirms, Arjun:
    - Explains the plan in plain language.
    - Outputs a **machine-usable JSON portfolio allocation** right after the marker:
      - `--- PORTFOLIO ALLOCATION (JSON) ---`

- **What the allocation JSON looks like (conceptually)**
  - Either:
    - A single block with `_sip_plan` and `allocation`.
  - Or:
    - Multiple blocks like `tenure_5yr_retirement`, each with its own `_sip_plan` and `allocation`.
  - Each `allocation` block maps **asset class → { percentage, _comment }` and must sum to **exactly 100%**.

- **Persistent memory**
  - `user_profile.json` stores the key profile fields:
    - Name, age, risk index, monthly SIP, goals/tenures, emergency corpus details, insurance status, and last session date.
  - Arjun loads this on startup and continues from the last state.

---

### 3. ETF SIP Backtester (`backtester.py`)

- **Input**
  - The **JSON allocation** produced by Arjun.
  - Internally parses:
    - Monthly SIP amount.
    - Asset-class percentage weights.
    - Optional multiple tenures (user chooses one in the CLI version).

- **Data sources**
  - `ETFS.json`: curated catalogue of Indian ETFs by asset class.
  - `fetch_technical_data` (from `app/tools/technical.py`):
    - For live prices (to choose affordable ETFs).
    - For 5-year historical prices (for backtesting).

- **What it does**
  - For each asset class:
    - Picks the **“best affordable” ETF** using rank, liquidity and current price.
    - Ensures the monthly allocation can buy at least 1 unit; if not, picks the cheapest ETF and warns.
  - Runs a **5-year SIP backtest**:
    - Monthly investing with no fractional units (realistic SIP behaviour).
    - Tracks total invested, portfolio value, gains, and XIRR.
  - Prints a detailed table:
    - Year-wise invested vs value.
    - Final ETF holdings with units and current value.
  - Returns a result dict which is also saved as `backtest_results.json`.

- **How Arjun and the backtester connect**
  - Arjun is the **conversation and planning brain**.
  - The backtester is a **separate engine** called via `run_backtest_flow(parsed_json)` inside `agent1advisor.py`:
    - For **ETF portfolios** it runs automatically.
    - For **Mutual Fund portfolios** it asks the user whether to run an ETF-equivalent backtest.

---

### 4. Agent B – Indian Stock Analyst (`main_app.py`)

- **What it does**
  - Provides a deep-dive analysis for a **single stock / ticker**.
  - Focused on **long-term value investing** in India (NSE/BSE).
  - Uses a ReAct-style agent (LangGraph) with Gemini 2.5 Flash and a detailed system prompt.

- **How it works at a high level**
  - User runs `python main_app.py` and types a query like:
    - “Analyze L&T for long term”
    - “Backtest HAL in 2024”
  - The agent then:
    - Calls tools to fetch:
      - Company documents and BSE filings.
      - Fundamentals and peer data.
      - Technical indicators from yfinance.
      - Recent financial news.
      - Order book assessment using RAG + news + filings.
    - Synthesizes a report with this structure:
      - Executive Summary (buy/hold/avoid + core thesis).
      - Fundamental Analysis.
      - Order Book Assessment.
      - Technical Analysis.
      - Company Documents Assessment (AR + concalls).
      - News and Sentiment.
      - Risk Assessment.
      - Final Recommendation with time horizon.

- **Separation from Arjun**
  - This agent is **ticker-centric**, not user-centric.
  - Each query is independent and does not use `user_profile.json`.
  - It shares the same tools and data layer as Arjun but solves a different task:
    - Arjun = “What should *my* portfolio look like?”
    - Stock Analyst = “Is this specific company a good long-term idea?”

---

### 5. Shared Tools and RAG Layer (High Level)

- **Documents & Filings (`app/tools/documents.py`)**
  - Scrapes Screener for:
    - Annual reports, concall transcripts, investor presentations.
  - Uses BSE APIs to fetch 12 months of:
    - Order/contract/LOI-related filings.
    - Investor presentations.

- **RAG Ingestion & Search (`app/rag/ingest.py`, `app/rag/query.py`)**
  - Downloads company PDFs, splits into chunks, filters boilerplate, and stores them in FAISS vector stores per ticker.
  - Uses multiple Google embedding keys in parallel for speed.
  - `search_company_documents` runs semantic search across these PDFs and returns the most relevant passages.

- **News, Fundamentals, Technicals**
  - `fetch_stock_news`: Tavily-based news search focused on Indian finance websites.
  - `fetch_screener_fundamentals`: parses Screener financial tables and peers.
  - `fetch_technical_data`: yfinance OHLCV + indicators (EMA/SMA/RSI/MACD/Bollinger/ATR).

---

### 6. How this maps to a future backend/frontend

- You can think of three main services behind an API:
  - **Advisor service** – wraps Arjun’s conversation and JSON allocation.
  - **Backtest service** – takes an allocation JSON and returns SIP backtest results.
  - **Stock analysis service** – takes a ticker/question and returns a single-stock research report.
- The common tool/RAG layer (Screener, BSE, yfinance, Tavily, embeddings) provides the **data foundation** for all of them.

