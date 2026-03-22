from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import uvicorn
import json
import re
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
        import os
        import re
        import json
        from agent1advisor import (
            build_system_prompt,
            fetch_top_etf_options,
            run_portfolio_backtest,
        )
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import (
            SystemMessage, HumanMessage, AIMessage, ToolMessage
        )

        api_key = os.environ.get("GOOGLE_API_KEY")
        llm_base = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=8192,
        )
        llm = llm_base.bind_tools([
            fetch_top_etf_options,
            run_portfolio_backtest,
        ])

        system_prompt = build_system_prompt(
            body.existing_profile or {}
        )

        messages = [SystemMessage(content=system_prompt)]

        for turn in body.conversation_history:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role == "user":
                messages.append(
                    HumanMessage(content=content)
                )
            elif role == "assistant":
                messages.append(
                    AIMessage(content=content)
                )

        messages.append(
            HumanMessage(content=body.user_message)
        )

        # Tool map for execution
        tool_map = {
            "fetch_top_etf_options": fetch_top_etf_options,
            "run_portfolio_backtest": run_portfolio_backtest,
        }

        # Tool-call loop: invoke → execute tools → feed back → repeat
        while True:
            response = llm.invoke(messages)

            if hasattr(response, 'tool_calls') and response.tool_calls:
                messages.append(response)
                for tc in response.tool_calls:
                    func = tool_map.get(tc["name"])
                    if func:
                        try:
                            result = func.invoke(tc["args"])
                        except Exception as e:
                            result = f"Tool error: {str(e)}"
                    else:
                        result = f"Unknown tool: {tc['name']}"
                    messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tc["id"]
                        )
                    )
                continue
            else:
                break

        reply = response.content or ""

        allocation_json = None
        arjun_text = reply

        if "--- PORTFOLIO ALLOCATION (JSON) ---" in reply:
            parts = reply.split(
                "--- PORTFOLIO ALLOCATION (JSON) ---"
            )
            arjun_text = parts[0].strip()
            json_part = parts[1].strip() \
                if len(parts) > 1 else ""
            try:
                cleaned = re.sub(
                    r"```json|```", "", json_part
                ).strip()
                allocation_json = json.loads(cleaned)
            except Exception:
                allocation_json = None

        # Detect [PORTFOLIO_FINALISED] tag from Arjun
        finalise_confirmed = False
        if "[PORTFOLIO_FINALISED]" in arjun_text:
            finalise_confirmed = True
            arjun_text = arjun_text.replace(
                "[PORTFOLIO_FINALISED]", ""
            ).strip()

        return {
            "response": arjun_text,
            "allocation_json": allocation_json,
            "backtest_results": None,
            "done": allocation_json is not None,
            "finalise_confirmed": finalise_confirmed,
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/backtest")
async def backtest(body: BacktestRequest):
    try:
        import sys
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        TOOLS_DIR = os.path.join(BASE_DIR, "app", "tools")
        if TOOLS_DIR not in sys.path:
            sys.path.insert(0, TOOLS_DIR)

        from backtester import (
            auto_select_etfs,
            run_backtest,
            load_etf_catalogue,
        )

        allocation_data = body.allocation

        # Handle both single and multi-tenure formats
        if "_sip_plan" in allocation_data:
            block = allocation_data
        else:
            tenure_keys = [
                k for k in allocation_data 
                if k.startswith("tenure_")
            ]
            block = allocation_data[tenure_keys[0]] \
                if tenure_keys else allocation_data

        monthly_sip = float(
            (block.get("_sip_plan") or {})
            .get("monthly_sip") or 10000
        )

        allocation = {
            k: v.get("percentage", 0)
            for k, v in block.get("allocation", {}).items()
            if isinstance(v, dict) 
            and v.get("percentage", 0) > 0
        }

        if not allocation:
            return {
                "success": False,
                "error": "Could not parse allocation"
            }

        etf_selections = auto_select_etfs(
            allocation, monthly_sip
        )

        if not etf_selections:
            return {
                "success": False,
                "error": "No ETFs could be selected"
            }

        results = run_backtest(
            allocation,
            etf_selections,
            monthly_sip,
            years=body.years
        )

        if "error" in results:
            return {"success": False, "error": results["error"]}

        # Remove monthly_detail to keep response small
        results_clean = {
            k: v for k, v in results.items()
            if k != "monthly_detail"
        }
        results_clean["monthly_detail"] = \
            results.get("monthly_detail", [])

        return {"success": True, "results": results_clean}

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=False)
