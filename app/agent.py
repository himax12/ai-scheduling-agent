# app/agent.py

import operator
import re
from typing import Annotated, Optional, TypedDict, List

from langchain_core.messages import AIMessage, AnyMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

# Import ALL your tools, including skip_insurance
from app.tools import book_appointment, get_available_slots, search_patient_in_emr, collect_insurance_details, skip_insurance

# --- 1. Define the Agent's State (The Agent's Memory) ---
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    patient_status: Optional[str]
    doctor_name: Optional[str]
    available_slots: Optional[List[str]] # <-- Corrected syntax [str]
    insurance_info: Optional[str]

# --- 2. Setup Tools and LLM ---
tools = [search_patient_in_emr, get_available_slots, book_appointment, collect_insurance_details, skip_insurance]
tool_map = {t.name: t for t in tools}

# Using a current, powerful, and supported model from the Groq API
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

# --- This crucial line was missing/incorrectly placed in some versions ---
llm_with_tools = llm.bind_tools(tools)


# --- 3. Define the Agent's Nodes ---

def call_llm(state: AgentState):
    """The 'brain' of the agent. It decides the next action based on the current state."""
    print("---NODE: AGENT BRAIN---")
    
    system_prompt_content = f"""You are a friendly, empathetic, and efficient medical scheduling assistant. Your goal is to book an appointment by following a strict sequence of steps.

    **Your Current Task Status (Your Memory):**
    - Patient Status: {state.get("patient_status", "Unknown")}
    - Insurance Collected: {"Yes" if state.get("insurance_info") else "No"}
    - Doctor Chosen: {state.get("doctor_name", "Unknown")}
    - Slots Found: {"Yes" if state.get("available_slots") else "No"}

    **Instructions (Follow this sequence precisely):**
    1.  **If Patient Status is 'Unknown'**: Greet the user warmly, get their name/DOB from their message, and call the `search_patient_in_emr` tool.
    2.  **If Patient Status is known but Insurance is 'No'**: Your ONLY job is to politely ask for their insurance details. If the user says they do not have insurance, you MUST call the `skip_insurance` tool. Otherwise, call `collect_insurance_details` with the info they provide.
    3.  **If Patient is 'NEW', Doctor is 'Unknown', and Insurance is 'Yes'**: Your ONLY job is to ask the user to choose a doctor.
    4.  **If a Doctor is chosen (e.g., from the user's last message or state) and Slots are 'No'**: Your ONLY job is to IMMEDIATELY call the `get_available_slots` tool.
    5.  **If Slots are 'Yes' and the user has chosen one**: Your ONLY job is to provide a full summary of the appointment (Patient Name, Doctor, Time) and ask for a final "Yes" or "Confirm" before booking.
    6.  **If the user has confirmed the summary**: Your ONLY job is to call the `book_appointment` tool.
    7.  **If the appointment is booked**: Your ONLY job is to provide a final, friendly confirmation message.
    """
    
    messages = [SystemMessage(content=system_prompt_content)] + state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tool_and_update_state(state: AgentState):
    """The 'hands' of the agent. It executes tools and updates the agent's memory."""
    print("---NODE: CALLING TOOL & UPDATING STATE---")
    last_message = state['messages'][-1]
    action = last_message.tool_calls[0]
    tool_to_call = tool_map[action['name']]
    tool_output = tool_to_call.invoke(action['args'])

    updates = {}
    if action['name'] == 'search_patient_in_emr':
        if "new patient" in tool_output.lower():
            updates["patient_status"] = "NEW"
        elif "returning patient" in tool_output.lower():
            updates["patient_status"] = "RETURNING"
            match = re.search(r"last_visit_doctor': '(Dr\. \w+)'", tool_output)
            if match:
                updates["doctor_name"] = match.group(1)
    
    if action['name'] == 'skip_insurance':
        updates["insurance_info"] = "Not Provided"

    if action['name'] == 'collect_insurance_details':
        updates["insurance_info"] = tool_output

    if action['name'] == 'get_available_slots':
        if "SUCCESS: The following slots are available" in tool_output:
            slots_text = tool_output.split("SUCCESS: The following slots are available")[1]
            slots = [s.strip() for s in slots_text.split(":")[-1].split(",")]
            updates["available_slots"] = slots
        else:
            updates["available_slots"] = []
    
    return {"messages": [ToolMessage(content=str(tool_output), tool_call_id=action['id'])], **updates}

# --- 4. Define Graph Logic ---
def should_continue(state: AgentState):
    """The 'manager' that decides whether to call a tool or end the conversation."""
    last_message = state['messages'][-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "call_tool"
    else:
        return END
def ask_for_doctor(state: AgentState):
    """A simple node that asks a new patient to choose a doctor."""
    print("---NODE: ASK FOR DOCTOR---")
    message = AIMessage(content="I see you're a new patient. Welcome! Which doctor would you like to see? We have Dr. Adams (General Health) and Dr. Chen (Cardiology).")
    return {"messages": [message]}

# --- 5. Build the Final Graph ---
workflow = StateGraph(AgentState)
workflow.add_node("ask_for_doctor", ask_for_doctor)

workflow.add_node("agent", call_llm)
workflow.add_node("call_tool", call_tool_and_update_state)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "call_tool": "call_tool",
        END: END,
    },
)

workflow.add_edge("call_tool", "agent")

app_graph = workflow.compile(checkpointer=MemorySaver())