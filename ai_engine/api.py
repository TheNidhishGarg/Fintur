from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import uvicorn

from main_app import agent

app = FastAPI(title="Fintur AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StockQuery(BaseModel):
    query: str

class AdvisorMessage(BaseModel):
    session_id: str
    user_message: str
    existing_profile: dict = {}
    conversation_history: list = []

class BacktestRequest(BaseModel):
    allocation: dict
    years: int = 5

@app.get("/health")
def health():
    return {"status": "Fintur AI Engine running"}

@app.post("/analyze-stock")
async def analyze_stock(body: StockQuery):
    try:
        from main_app import get_llm, tools, SYSTEM_PROMPT
        from langgraph.prebuilt import create_react_agent
        current_llm = get_llm()
        current_agent = create_react_agent(
            model=current_llm,
            tools=tools,
            prompt=SYSTEM_PROMPT,
        )
        result = current_agent.invoke(
            {"messages": [HumanMessage(content=body.query)]}
        )
        output_message = result["messages"][-1]
        content = output_message.content
        if isinstance(content, list):
            text = "\n".join(
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            text = str(content)
        return {"analysis": text}
    except Exception as e:
        return {"error": str(e)}

@app.post("/advisor/message")
async def advisor_message(body: AdvisorMessage):
    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=body.user_message)]}
        )
        output_message = result["messages"][-1]
        content = output_message.content
        if isinstance(content, list):
            text = "\n".join(
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        else:
            text = str(content)
        return {"response": text}
    except Exception as e:
        return {"error": str(e)}

@app.post("/backtest")
async def backtest(body: BacktestRequest):
    return {"result": "Backtest coming soon", "allocation": body.allocation}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=False)
