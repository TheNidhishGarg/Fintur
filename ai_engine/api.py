from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

sys.path.append(os.path.dirname(__file__))

app = FastAPI(title="Fintur AI Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ──────────────────────────────────────────
class AdvisorMessage(BaseModel):
    session_id: str
    user_message: str
    existing_profile: Optional[dict] = None
    conversation_history: Optional[list] = []

class BacktestRequest(BaseModel):
    allocation: dict
    years: Optional[int] = 5

class StockAnalysisRequest(BaseModel):
    query: str

# ── In-memory session store ──────────────────────────────────
sessions = {}

# ── Routes ──────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "Fintur AI Engine running"}

@app.post("/advisor/message")
async def advisor_message(req: AdvisorMessage):
    try:
        from agent1advisor import build_system_prompt, save_session_profile
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        if req.session_id not in sessions:
            sessions[req.session_id] = {
                "history": [],
                "profile": req.existing_profile or {}
            }

        session = sessions[req.session_id]
        system_prompt = build_system_prompt(session["profile"])

        messages = [SystemMessage(content=system_prompt)]
        for role, content in session["history"]:
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=req.user_message))

        response = llm.invoke(messages)
        reply = response.content

        session["history"].append(("user", req.user_message))
        session["history"].append(("assistant", reply))

        allocation_json = None
        assistant_message = reply

        if "--- PORTFOLIO ALLOCATION (JSON) ---" in reply:
            import re, json
            parts = reply.split("--- PORTFOLIO ALLOCATION (JSON) ---")
            assistant_message = parts[0].strip()
            json_part = parts[1].strip()
            cleaned = re.sub(r"```json|```", "", json_part).strip()
            allocation_json = json.loads(cleaned)

        return {
            "assistant_message": assistant_message,
            "allocation_json": allocation_json,
            "session_id": req.session_id
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/backtest")
async def run_backtest(req: BacktestRequest):
    try:
        from backtester import run_backtest_from_arjun
        result = run_backtest_from_arjun(req.allocation, years=req.years)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze-stock")
async def analyze_stock(req: StockAnalysisRequest):
    try:
        from main_app import create_agent
        from langchain_core.messages import HumanMessage
        agent = create_agent()
        result = agent.invoke({"messages": [HumanMessage(content=req.query)]})
        return {"analysis": result["messages"][-1].content}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
