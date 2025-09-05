# app/main.py
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.agent import app_graph

app = FastAPI(title="AI Scheduling Agent API")

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Handles a conversation by invoking the graph and returning the final result."""
    config = {"configurable": {"thread_id": request.session_id}}
    inputs = {"messages": [HumanMessage(content=request.message)]}
    
    # Use ainvoke() to run the graph from start to finish and get the final state.
    final_state = await app_graph.ainvoke(inputs, config=config)
    
    # Extract the last AI message from the final state's message list.
    final_response = final_state["messages"][-1].content
    
    return ChatResponse(response=final_response, session_id=request.session_id)