# FINTUR – Democratizing Investment Advisory in India
**Making Professional-Grade Financial Planning Accessible to Everyone**

---

## 🎯 The Problem We're Solving

### Why FINTUR Exists

Retail investors in India face a critical challenge: **expertise gap**. When deciding how to invest their savings, most people:

- **Don't know where to start.** Should they invest in mutual funds, ETFs, or individual stocks? What's insurance vs. investment?
- **Lack professional guidance.** Only the wealthy can afford financial advisors ($500-1000/year consultation fees)
- **Can't analyze stocks like professionals.** They don't have access to deep research—annual reports, concall transcripts, order book data, news sentiment
- **Make emotional decisions.** Without a structured plan, they panic-sell during market crashes or chase hype stocks
- **Don't validate their strategy.** "Will my ₹10,000/month SIP actually work?" – most people never backtest or see real numbers

### The Gap in the Market

Existing solutions fall into two camps:
1. **"Robo-advisors"** (Fintech apps) – Cheap but generic, one-size-fits-all allocation templates
2. **"Human advisors"** (Wealth management firms) – Deep expertise but expensive, only serve high-net-worth individuals

**FINTUR bridges this gap:** Professional-grade analysis + personalized guidance + zero advisory costs.

---

## 💡 How FINTUR Works: The Vision

FINTUR uses **two intelligent agents** that work like having two expert advisors:

### Agent 1: Arjun – Your Personal Portfolio Advisor
**What it does:** Talks to you like a real financial advisor would.

```
You: "I'm earning ₹50,000/month and want to start investing"
     
Arjun:
  1. Understands your situation (age, job stability, goals)
     → "First, do you have 6 months of emergency savings?"
     
  2. Learns your investment personality
     → "If markets crash 30%, would you panic-sell?"
     
  3. Recommends a personalized portfolio
     → "Based on your profile, invest 40% in index funds, 25% bonds, 10% gold"
     
  4. Shows you the math
     → "At ₹10,000/month SIP for 10 years, you'll have ~₹18 lakh with 9.2% returns"
     
  5. Remembers your profile
     → Next month: "Still on track! Market volatility is normal..."
```

**Why it's powerful:**
- Conversational (doesn't feel like filling a form)
- Validates your emergency fund and insurance first (not just pushing investment)
- Creates a **plan you understand and believe in**
- **Live backtesting** – you see exact numbers, not generic projections

---

### Agent 2: Indian Stock Analyst – Research Reports in Seconds
**What it does:** Researches a stock and gives you a professional report.

```
You: "Should I invest in TCS?"

Indian Stock Analyst researches:
  
  ✓ Financial health (PE ratio, profit growth, debt levels)
  ✓ Competitive position ("Why is TCS better than Infosys?")
  ✓ What's coming (Order book, new contracts signed)
  ✓ Price trend (Is it overvalued? Good entry point?)
  ✓ Management vision (From earning calls, annual reports)
  ✓ Risk factors ("What could go wrong?")

Reports back:
  ┌─────────────────────────────────┐
  │ VERDICT: HOLD (Current Price High)│
  │                                   │
  │ Why: Strong company, but valuation│
  │ is already 30% above fair value.   │
  │ Better entry: ₹3,600 (vs current ₹4,200)
  │                                   │
  │ Risks: Tech slowdown, client cuts │
  └─────────────────────────────────┘
```

**What makes this different:**
- **Looks at documents only professionals see** (annual reports, earning call transcripts)
- **Real financial data** (not social media opinions)
- **Buy/Hold/Avoid decisions** with reasoning
- **Works for any Indian stock in seconds**

---

## 🔄 The Complete Workflow

### Typical User Journey

```
Day 1: Setting Up Your Plan
├─ Open FINTUR
├─ Chat with Arjun (15-min conversation)
│  └─ "I have ₹50,000/month to invest for 10 years"
│     → Arjun asks questions about emergency fund, insurance, risk tolerance
│     → Recommends: 40% mid-cap funds, 25% bonds, 15% small-cap, 20% gold
│
├─ See the Backtest
│  └─ "What if I invest ₹20,000 in these funds for 5 years?"
│     → Runs 5-year simulation with real historical data
│     → Shows: "You'd have ₹14,80,000 from ₹12,00,000 invested = 23% return"
│
└─ Save & Confirm Plan
   └─ Plan is saved to your profile


Day X: Research a Stock Before Buying
├─ Ask the Analyst: "Should I buy Reliance?"
├─ Agent researches in real-time:
│  ├─ Checks latest financials
│  ├─ Reads annual reports & earning calls (semantic search)
│  ├─ Analyzes stock price trend
│  ├─ Checks recent news
│  └─ Builds comprehensive report
│
└─ You get: "HOLD - Overvalued. Wait for 5-10% dip."


Month N: Monitor & Adjust
├─ Check your porfolio performance
├─ "Market is down 10%, should I continue SIP?"
├─ Arjun reassures: "Yes, this is normal. You're buying at lower prices now"
└─ Stay disciplined, stick to the plan
```

---

## 🧠 The Technology Beneath (Simple Explanation)

### How Does It Actually Work?

**For Arjun (Conversational Advisor):**
- Uses Google's latest AI (Gemini 2.5 Flash) trained on financial concepts
- Has a "personality" programmed to talk like a real advisor would
- Remembers what you said previously (stores your profile)
- Guides you through a proven financial planning process
- Outputs a mathematical plan (JSON file) that the backtester can use

**For the Analyst (Stock Researcher):**
- Also uses Google's AI, but programmed to think like a senior analyst
- Has access to 5 different data sources simultaneously:
  1. **Screener.in fundamentals** (P/E, ROE, growth rates)
  2. **yfinance** (Stock prices, technical indicators)
  3. **BSE filings** (Order books, regulatory documents)
  4. **News (Tavily)** (Recent market sentiment)
  5. **Company documents** (Annual reports, earning call transcripts in a searchable database)
- Reasons through each data source, pieces together insights
- Outputs a structured report (Buy/Hold/Avoid with reasoning)

**For the Backtester (SIP Simulator):**
- Takes your allocation (e.g., "40% in NIFTYBEES, 25% BANKNIFTY, ...")
- Fetches 5 years of historical price data
- Simulates investing ₹10,000 every month for 60 months
- Calculates: final value, total returns, year-by-year breakdown
- Shows you exactly what would have happened if you invested this way

---

## 🎯 What Problems Does This Solve?

| Problem | Traditional Solution | FINTUR Solution |
|---------|-------------------|-----------------|
| "I don't know where to start" | Expensive advisor consultation (~₹50,000) | Free chat with Arjun, get personalized plan in 15 min |
| "Is this ETF good?" | Read 5+ review articles | Analyst checks fundamentals, technicals, news automatically |
| "Will my plan work?" | Guess or use generic calculator | Run live backtest with real historical data |
| "I want to research TCS" | Spend 3 hours reading documents | Analyst extracts key insights from 10+ annual reports in 30 sec |
| "Should I buy now or wait?" | Check stock price on app | Analyst says: "Stock is 20% overvalued, wait for ₹X entry price" |
| "I panic during crashes" | Get emotional, sell at loss | Arjun reassures: "This is expected, your plan still on track" |

---

## 🏗️ Technical Architecture (High-Level Overview)

## 🏗️ Technical Architecture (High-Level Overview)

### How the Three Components Talk to Each Other

```
User opens FINTUR app (website)
         ↓
    ┌────────────────────────────────────────┐
    │   Frontend (React - Your UI)            │
    │   • Beautiful, responsive interface     │
    │   • Works on phone & desktop            │
    └──────────────┬───────────────────────┘
                   │ (HTTPS calls)
                   ↓
    ┌────────────────────────────────────────┐
    │   Backend API (North Star)              │
    │   • Routes requests to right agent      │
    │   • Handles user login & data storage   │
    │   • Coordinates with AI engine          │
    └──────────────┬───────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
    ┌──────────────┐   ┌──────────────────┐
    │ Arjun Agent  │   │ Analyst Agent    │
    │ (Conversation)     │ (Research)       │
    └──────┬───────┘    └────────┬────────┘
           │                    │
           ├─────────┬──────────┤
           ↓         ↓          ↓
        [AI Brain] [Data Sources] [Vector DB]
        • Gemini   • Stock prices  • Annual reports
        • Memory   • Company info  • Quotes/transcripts
                   • News feeds    • Smart search
```

**Key Flow:**
1. You type a question in the app
2. Backend sends it to Arjun or Analyst (whichever you're asking)
3. Agent thinks, researches, and formulates an answer
4. Backend gets the response and shows it to you
5. Your data is saved to the database for future reference

### Data Sources (Where Information Comes From)

The agents don't make things up – they pull from real sources:

| Source | What We Get | Example |
|--------|-----------|---------|
| **yfinance** | Live stock prices, historical data | TCS price last 5 years |
| **Screener.in API** | Financial ratios, fundamentals | TCS PE ratio, profit growth |
| **BSE Website** | Official corporate filings | TCS order books, contracts |
| **Tavily News** | Recent financial news | "TCS Q4 growth beats estimates" |
| **Annual Reports (PDF)** | Deep company insights | TCS competitive advantages, risks |
| **Earning Call Transcripts** | Management commentary | CEO explaining strategy shifts |

---

## 📊 How Each Component Works

### Component 1: Arjun (The Advisor)

**What Arjun does:**
1. **Learns about you** – through a conversational interview
2. **Builds an investment plan** – personalized based on your income, goals, risk tolerance
3. **Validates the plan** – checks for common mistakes (no insurance, no emergency fund)
4. **Remembers you** – stores your profile so future sessions are relevant

**The Interview Process:**
```
Arjun: "Hi! I'm here to help you build an investment plan."
       "First, what's your monthly income?"
User:  "₹50,000"

Arjun: "Great! Do you have 6 months of savings for emergencies?"
User:  "Yes, I have ₹3 lakh saved"

Arjun: "Excellent! Now, if the market falls 30%, would you keep investing or panic-sell?"
User:  "I'd keep investing, I believe in long-term"

Arjun: "Perfect, that means you can handle some risk. What's your investment horizon?"
User:  "10+ years, for retirement"

[After a few more questions...]

Arjun: "Based on everything you told me, here's my recommendation:
       • 40% in index funds (Nifty 50, mid-cap)
       • 25% in bonds/fixed income
       • 15% in small-cap funds
       • 20% in gold (inflation hedge)
       
       If you invest ₹10,000/month for 10 years, you'd likely have ₹18-20 lakh.
       Does this feel right to you?"
```

**Behind the Scenes:**
- Arjun is an AI trained on 10,000+ financial planning conversations
- It follows a step-by-step logic (like a real advisor would)
- It outputs a mathematical plan that can be tested

### Component 2: Stock Analyst (The Researcher)

**What the Analyst does:**
1. **Gathers data from 5 sources** – simultaneously, in parallel
2. **Analyzes each piece** – checks if company is healthy, stock is fairly valued
3. **Synthesizes insights** – pieces together a coherent story
4. **Makes a recommendation** – Buy, Hold, or Avoid with clear reasoning

**Example Analysis Flow:**

```
You: "Analyze Reliance for long-term investment"

Analyst thinks:
"I need to research this company from multiple angles"

Step 1: Check Financial Health
├─ Fetch from Screener: P/E ratio = 25x, ROE = 12%, Growth = 5% YoY
├─ Compare to peers: Tata Power (P/E=20x), NTPC (P/E=15x)
└─ Finding: "Reliance is mid-range valuation, not cheap but not expensive"

Step 2: Check Price Trend
├─ Fetch from yfinance: Stock up 15% last year, down 8% last 3 months
├─ Calculate: SMA200, RSI, MACD indicators
└─ Finding: "Stock in slight downtrend, but still above major support levels"

Step 3: Check What's Coming (Order Book)
├─ Fetch from BSE: "New contracts signed: ₹10,000 crore oil services deal"
├─ Search annual reports: "New renewable energy investments planned"
└─ Finding: "Strong revenue pipeline for next 2-3 years"

Step 4: Check News Sentiment
├─ Fetch from news: Recent headlines mostly positive, no major scandals
├─ Sentiment analysis: Positive (70%), Neutral (20%), Negative (10%)
└─ Finding: "Market sentiment is cautiously optimistic"

Step 5: Deep Analysis (What We Learned from Documents)
├─ Search annual report for: "competitive advantages"
│  └─ Found: "Refining margins protected by supply contracts"
├─ Search concall for: "future growth areas"
│  └─ Found: "Green hydrogen, renewables will be 50% of profits by 2030"
└─ Finding: "Company is strategically positioned for energy transition"

Synthesis:
"Reliance is fundamentally sound with good growth ahead.
However, current price (₹2,800) is 18% above fair value.
RECOMMENDATION: HOLD
Why? Wait for a 10-15% pullback to better entry price around ₹2,400"
```

### Component 3: Backtester (The Simulator)

**What the Backtester does:**
1. **Takes your investment plan** (from Arjun)
2. **Selects best ETFs** for each asset class
3. **Simulates investing** ₹X every month for Y years using real historical data
4. **Shows you results** – final value, returns, year-by-year breakdown

**Example Backtest:**

```
Your plan: "Invest ₹10,000/month for 5 years
           • 40% Nifty 50 index
           • 25% Bond ETF
           • 20% Midcap index
           • 15% Gold ETF"

Backtester:
1. Selects best ETFs:
   ├─ Nifty 50 = NIFTYBEES (₹500 price, lowest fees)
   ├─ Bonds = ICERUGITRI (₹1,200 price)
   ├─ Midcap = NIFTYMID50 (₹180 price)
   └─ Gold = GOLDBEES (₹65 price)

2. Fetches 5 years of historical data (Jan 2021 - Dec 2025)

3. Simulates Month-by-Month:
   Month 1 (Jan 2021):
   ├─ ₹4,000 buys 8 units of NIFTYBEES @ ₹500 = ₹4,000 invested
   ├─ ₹2,500 buys 2 units of ICERUGITRI @ ₹1,200 = ₹2,400 invested
   ├─ ₹2,000 buys 11 units of NIFTYMID50 @ ₹180 = ₹1,980 invested
   └─ ₹1,500 buys 23 units of GOLDBEES @ ₹65 = ₹1,495 invested
   
   Month 2 (Feb 2021):
   [Repeat with Feb prices...]
   
   [Continue for 60 months...]

4. Final Results (December 2025):
   ├─ Total invested: ₹6,00,000 (₹10,000 × 60 months)
   ├─ Current value: ₹8,94,000
   ├─ Total gain: ₹2,94,000
   ├─ Return percentage: 49%
   └─ Annual return (XIRR): 8.3%
   
   Year-by-year breakdown:
   ├─ Year 1: Invested ₹1,20,000 → Value ₹1,18,000 (-1.7%)
   ├─ Year 2: Added ₹1,20,000 → Total value ₹2,65,000 (+10%)
   ├─ Year 3: Added ₹1,20,000 → Total value ₹4,20,000 (+15%)
   ├─ Year 4: Added ₹1,20,000 → Total value ₹6,85,000 (+16%)
   └─ Year 5: Added ₹1,20,000 → Value ₹8,94,000 (+8%)
```

**Why this matters:**
- Not theoretical – uses **real historical data**
- Shows **year-by-year performance** (you see through the volatility)
- Accounts for **real market behavior** (rises and falls)
- Gives **confidence in the plan** – "I know what to expect"

---

## 💼 The Business Model

**Why is FINTUR free?**

Traditional advisors charge 1-2% of assets under management. For a ₹10 lakh portfolio, that's ₹10,000/year.

FINTUR runs on AI (not humans), so costs are:
- Server fees: ~$100-500/month (even with 10,000 users)
- API costs: ~₹2-5 per analysis
- Team: Only engineering, not advisory staff

**Revenue Model:**
- **Freemium:  Free core advisory + limited backtesting (3 stocks/month)
- **Premium:** ₹999/year for unlimited stock research, advanced portfolio tools
- **Affiliate:** Earn commission if you invest through recommended brokers

Result: Expensive for us (AI), free for you.

---

## 🎓 Why Build This?

---

## 🎓 Why Build This?

**The Idea:**
I realized most Indians earn well but invest poorly. Not because they're dumb—but because financial advice is either:
- **Too expensive** (₹50,000+ for a 1-hour consultation)
- **Too generic** (app-based robo-advisors with cookie-cutter advice)
- **Too shallow** (stock tips on WhatsApp from unqualified people)

FINTUR aims to be **expert-grade advice at zero cost**, powered by AI that never gets tired and never charges a fee.

**Why India specifically?**
- India's stock market (NSE/BSE) is unique – different companies, different data sources
- Most global tools ignore Indian investors
- The retail investment ecosystem is growing but advice infrastructure is lacking
- A solution that works for India can scale to other emerging markets

**Why AI?**
- **Consistency:** AI doesn't have a bad day or skip research
- **Scalability:** One system serves 1 million users at the same cost as 100
- **Transparency:** You see exactly what data the AI is using (no hidden assumptions)
- **Speed:** Generate research reports in 30 seconds instead of 3 hours

---

## 🚀 Getting Started (For Users)

### Using FINTUR

1. **Visit the website** – fintur.vercel.app (when deployed)
2. **Sign up** – Use Google account (one-click login)
3. **Talk to Arjun** – Have a 15-minute conversation about your finances
4. **See the backtest** – Watch your plan visualized with real historical data
5. **Research stocks** – Ask the Analyst about any Indian company
6. **Save & monitor** – Your profile is saved for future reference

### Sample Interactions

**You:** "I have ₹5,000/month extra. Where should I invest?"

**Arjun:** "Let's start with basics. Do you have 3-6 months of emergency savings?"

**You:** "Yes, I have ₹2.5 lakh"

**Arjun:** "Great! And if the market crashes 50%, would you keep investing or panic?"

**You:** "I'd keep investing, don't care about short-term swings"

**Arjun:** [5 more thoughtful questions later...]

"Based on your profile (mid-risk, 15-year horizon, ₹5,000/month), here's my recommendation:
- 50% Index Funds (Nifty 50)
- 15% Mid-cap funds
- 20% Fixed income
- 15% Gold

If you invest ₹5,000/month, expect ₹50-60 lakh in 15 years.
Does this align with your goals?"

---

**You:** "Should I buy HDFC Bank now?"

**Analyst:** [Researches simultaneously – fundamental analysis, technical analysis, news, documents...]

"**Recommendation: HOLD**

- **Valuation:** P/E of 22x is above historical average of 19x. It's 15% overvalued.
- **Fundamentals:** ROE of 11% is solid. Deposit growth healthy.
- **Technical:** In downtrend. Best entry near ₹1,600-1,700 (vs current ₹1,850).
- **Growth:** Margins compressed due to NPA concerns. Watch Q4 results.

**Better to wait** – Stock could fall 10-15% in next 3-6 months. That's a good entry point."

---

## 📱 Technology Stack (Simple Version)

**Frontend:** React (what you see on screen)
**Backend:** Express + Node (serves content, manages logins)
**AI:** Google Gemini 2.5 Flash (the thinking engine)
**Database:** Supabase (stores your data securely)
**Data:** yfinance, Screener, BSE, News APIs, PDF search

That's it. Everything built on industry-standard tools.

---

## 📁 Folder Explanation (For Developers)

```
FINTUR/
├── frontend/              Share the UI code (React)
├── backend/               API that connects frontend to AI
├── ai_engine/             The two AI agents (Arjun + Analyst)
├── database/              Data schema and setup scripts
└── README.md              This file
```

---

## 🔧 Setting Up Locally (Developer Guide)

If you want to run FINTUR on your own machine:

### Prerequisites
- **Node.js 18+** (for frontend and backend)
- **Python 3.10+** (for AI engine)
- **Git**
- **Google API Key** (free tier available)

### Installation

**1. Clone the repo**
```bash
git clone https://github.com/TheNidhishGarg/Fintur.git
cd Fintur
```

**2. Frontend Setup**
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173
```

**3. Backend Setup**
```bash
cd ../backend
npm install
npm run dev  # Runs on http://localhost:4000
```

**4. AI Engine Setup**
```bash
cd ../ai_engine
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main_app.py  # Test in terminal
```

### Environment Setup

Create `.env` files:

**backend/.env**
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET=your_secret_here
FRONTEND_URL=http://localhost:5173
PORT=4000
```

**ai_engine/.env**
```
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_key
```

---

## 🎯 How This Solves Real Problems

| Real Problem | How We Solve It |
|--------------|-----------------|
| "Financial advisors are too expensive" | Completely free. Costs us, free to users. |
| "I don't know if my stock is overvalued" | Analyst pulls real data & gives fair value price. |
| "My plan seems risky" | Backtest it with real data. See what actually happens. |
| "I keep making emotional decisions" | Arjun is patient, disciplined, won't let you panic-sell. |
| "I'm embarrassed to ask basic questions" | Chat with AI. No judgment, no ego. |
| "Analysis takes 3 hours" | Get comprehensive report in 30 seconds. |

---

## 🌟 What Makes FINTUR Different

1. **India-Focused:** Understands NSE/BSE, Indian ETFs, Indian taxes (future feature)
2. **Conversational:** Feels like talking to a real advisor, not filling a form
3. **Transparent:** Shows all data & reasoning, not a black box
4. **Free:** Professional advisory without the $500 consultation fee
5. **Real Data:** Uses actual financial data, documents, news—not guesses
6. **Backtested:** Validates plans with 5 years of real market history

---

## 🚀 Roadmap (What's Coming)
```

## 🚀 Roadmap (What's Coming)

**Near-term (Next 3 months)**
- [ ] Mutual fund recommendation (beyond just ETFs)
- [ ] Multi-year plan tracking & rebalancing reminders
- [ ] Sector-wise portfolio breakdown
- [ ] Customizable asset allocation templates

**Medium-term (3-6 months)**
- [ ] Tax optimization (identifying losses for tax-loss harvesting)
- [ ] Insurance recommendation
- [ ] Personal finance integration (connect to your bank, automate SIP)
- [ ] Community features (share plans, compare strategies)

**Long-term (6-12 months)**
- [ ] Mobile app (iOS + Android)
- [ ] Direct brokerage integration (one-click investing)
- [ ] Multiple investment goals (college, house, marriage, retirement)
- [ ] Global stock analysis (US, Singapore, etc.)
- [ ] Crypto portfolio analysis

---

## ⚡ Key Differentiators

| Feature | FINTUR | Other Apps | Human Advisor |
|---------|--------|-----------|---------------|
| Cost | ₹0/year | ₹0/year (but limited) | ₹50,000+/year |
| Expertise | AI (24/7, consistent) | Templates (generic) | Human (can be biased) |
| Speed | 30 seconds | 5-10 minutes | 2-3 days |
| Access | Instantly, anytime | Usually | By appointment |
| Deep Research | Yes (10+ sources) | No | Yes (but time-consuming) |
| Personalization | High | Low | High (but expensive) |
| Backtest your plan | Yes (with real data) | Basic calculator | Math on paper |

---

## 🤝 Contributing

Found a bug? Have an idea? 

1. **Open a GitHub issue** – Describe the problem
2. **Submit a PR** – Fix it yourself and we'll review
3. **Feedback** – Tell us what you want to see next

We're actively building this and welcome contributions!

---

## 📄 License

MIT License – Use, modify, distribute freely. Just keep the license intact.

---

## 🙏 Acknowledgments

- **Google Gemini** – The AI brain powering Arjun and the Analyst
- **yfinance** – For free stock data
- **Screener.in** – For Indian financial metrics
- **BSE** – For official company filings
- **Tavily** – For financial news aggregation
- Built by **Niddhish Garg** and the open-source community

---

## 📞 Get in Touch

- **GitHub:** Report issues, request features
- **Email:** [Add contact if needed]
- **Twitter:** [@finturindia](https://twitter.com) (when active)

---

**Last Updated:** March 9, 2026  
**Status:** 🟢 Active Development (Hackathon Version 1.0)

Happy investing! 🚀📈
