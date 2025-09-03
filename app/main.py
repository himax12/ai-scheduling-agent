from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import app_graph # Import our compiled agent graph
from langchain_core.messages import HumanMessage
import uuid

app = FastAPI(title="AI Scheduling Agent API")

# Pydantic models for structured request and response
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend API is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Endpoint to handle chat conversations with the agent."""
    session_id = request.session_id
    config = {"configurable": {"thread_id": session_id}}

    # Prepare the input for the graph
    inputs = [HumanMessage(content=request.message)]

    # Stream the response from the agent
    final_response = None
    async for event in app_graph.astream_events(inputs, config=config, version="v1"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            # We are streaming the final response, so collect the chunks
            content = event["data"]["chunk"].content
            if final_response is None:
                final_response = content
            else:
                final_response += content
        elif kind == "on_tool_end":
            # We can optionally see tool outputs here if we want
            pass

    if final_response is None:
        final_response = "Sorry, I encountered an issue. Could you please try again?"

    return ChatResponse(response=final_response, session_id=session_id)