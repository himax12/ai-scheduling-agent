import os
from typing import TypedDict, Annotated
import operator
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.tools import search_patient_in_emr, get_available_slots, book_appointment

# Load environment variables from .env file
load_dotenv()
if os.getenv("GOOGLE_API_KEY") is None:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# 1. Define the State: The agent's memory
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# 2. Define the Tools: Gather all our functions into a list
tools = [search_patient_in_emr, get_available_slots, book_appointment]

# 3. Define the LLM and bind the tools to it
# This tells the LLM what functions it's allowed to call.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0, convert_system_message_to_human=True)
llm_with_tools = llm.bind_tools(tools)

# 4. Define the Nodes for our graph

# This node calls the AI model
def call_model(state: AgentState):
    """The primary node for the agent. Calls the LLM with the current state."""
    print("🧠 Node: Calling Model")
    # The first message is always the system prompt
    system_prompt = SystemMessage(
        content="""
        You are a helpful and friendly medical appointment scheduling assistant.
        Your tasks are:
        1.  Greet the user and ask for their full name and date of birth to begin.
        2.  Use the `search_patient_in_emr` tool to check if they are a new or returning patient.
        3.  Based on their status, use the `get_available_slots` tool to find appointments. Clearly state the appointment duration (60 mins for new, 30 for returning).
        4.  Ask the user to confirm their desired slot.
        5.  Once confirmed, use the `book_appointment` tool to finalize the booking.
        6.  After booking, confirm everything with the user and end the conversation.

        Be polite and clear in all your communications. Do not ask for insurance information.
        """
    )
    messages_with_prompt = [system_prompt] + state['messages']
    response = llm_with_tools.invoke(messages_with_prompt)
    return {"messages": [response]}

# This node executes the tools
def call_tool(state: AgentState):
    """This node executes the tools called by the LLM."""
    print("🛠️ Node: Calling Tool")
    # The last message from the model will be a tool call
    last_message = state['messages'][-1]

    # We find the tool to call and its arguments
    tool_name = last_message.tool_calls[0]['name']
    args = last_message.tool_calls[0]['args']

    # Look for the actual function in our tools list
    action = None
    for tool in tools:
        if tool.name == tool_name:
            action = tool
            break

    if action is None:
        raise ValueError(f"Tool {tool_name} not found.")

    # Execute the tool and get the result
    result = action.invoke(args)

    # Return the result as a ToolMessage
    tool_message = ToolMessage(content=str(result), tool_call_id=last_message.tool_calls[0]['id'])
    return {"messages": [tool_message]}

# 5. Define the Edges: The conditional logic
def should_continue(state: AgentState):
    """Determines the next step: call a tool or end the conversation."""
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        # If the model made a tool call, we should execute it
        return "call_tool"
    else:
        # Otherwise, the conversation is finished
        return END

# 6. Build and Compile the Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("call_tool", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "call_tool": "call_tool",
        END: END
    }
)
workflow.add_edge("call_tool", "agent")

# This creates the final, runnable agent
app_graph = workflow.compile(checkpointer=MemorySaver())