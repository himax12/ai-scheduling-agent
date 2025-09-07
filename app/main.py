# app/main.py

import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.agent import app_graph

app = FastAPI(
    title="AI Scheduling Agent API",
    description="An API for the AI-powered medical appointment scheduling agent.",
)

# Pydantic models for request and response
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Handles a conversation turn by invoking the LangGraph agent."""
    config = {"configurable": {"thread_id": request.session_id}}
    inputs = {"messages": [HumanMessage(content=request.message)]}
    
    # Use ainvoke() to run the graph until it stops (at an interrupt)
    # and returns the final state.
    final_state = await app_graph.ainvoke(inputs, config=config)
    
    # Extract the content of the very last message from the final state
    final_response_message = final_state["messages"][-1].content
    
    if not final_response_message:
        final_response_message = "I'm sorry, I'm having trouble responding. Could you please try again?"

    return ChatResponse(response=final_response_message, session_id=request.session_id)

@app.get("/")
def read_root():
    return {"status": "AI Scheduling Agent API is running."}