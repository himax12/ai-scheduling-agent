# app/agent.py

import operator
import re
from typing import Annotated, Optional, TypedDict

# Imports have been cleaned up
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

# Import the tools we created
from app.tools import book_appointment, get_available_slots, search_patient_in_emr

# --- 1. Define the Agent's State (The Agent's Memory) ---
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    patient_status: Optional[str]
    doctor_name: Optional[str]
    available_slots: Optional[list[str]]

# --- 2. Setup Tools and LLM ---
tools = [search_patient_in_emr, get_available_slots, book_appointment]
tool_map = {t.name: t for t in tools}

# We use a current, powerful, and supported model from the Groq API
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0)

# --- This is the corrected setup ---
# This crucial line binds the tools to the LLM, creating the runnable agent
llm_with_tools = llm.bind_tools(tools)


# --- 3. Define the Agent's Nodes ---

def call_llm(state: AgentState):
    """The 'brain' of the agent. It decides the next action based on the current state."""
    print("---NODE: AGENT BRAIN---")
    
# In agent.py -> call_llm()

    system_prompt_content = f"""You are an autonomous and efficient medical scheduling assistant. Your goal is to book an appointment by following a strict, unchangeable sequence of tasks.

    **Your Current Task Status (Your Memory):**
    - Patient Status: {state.get("patient_status", "Unknown")}
    - Insurance Collected: {"Yes" if state.get("insurance_info") else "No"}
    - Doctor Chosen: {state.get("doctor_name", "Unknown")}
    - Slots Found: {"Yes" if state.get("available_slots") else "No"}

    **Instructions (You MUST follow this order):**
    1.  **Task 1: Identify Patient.** If Patient Status is 'Unknown', your only goal is to call the `search_patient_in_emr` tool. Do not proceed until this is done.
    2.  **Task 2: Collect Insurance.** If Patient Status is known BUT Insurance is 'No', your only goal is to call the `collect_insurance_details` tool. Do not proceed until this is done.
    3.  **Task 3: Determine Doctor.** If Patient is 'NEW', Doctor is 'Unknown', AND Insurance is 'Yes', your only goal is to ask the user for their doctor choice.
    4.  **Task 4: Find Slots.** If a Doctor is chosen AND Slots are 'No', your only goal is to call `get_available_slots`.
    5.  **Task 5: Get Confirmation.** If Slots are 'Yes', your only goal is to present a summary and ask for final confirmation (e.g., "Does this look correct?").
    6.  **Task 6: Book Appointment.** If the user has confirmed the summary, your only goal is to call the `book_appointment` tool.
    7.  **Task 7: Final Response.** If the appointment is booked, your ONLY job is to provide a single, clean confirmation message and nothing else.
    """.format(
        patient_status=state.get("patient_status", "Unknown"),
        doctor_name=state.get("doctor_name", "Unknown"),
        slots_found="Yes" if state.get("available_slots") else "No",
        insurance_info=state.get("insurance_info", "No")
    )    
    messages = [SystemMessage(content=system_prompt_content)] + state['messages']
    # This line now works correctly because llm_with_tools is defined
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

    if action['name'] == 'get_available_slots':
        slots_text = tool_output.split("SUCCESS: The following slots are available")[1]
        slots = [s.strip() for s in slots_text.split(":")[-1].split(",")]
        updates["available_slots"] = slots
    
    return {"messages": [ToolMessage(content=str(tool_output), tool_call_id=action['id'])], **updates}

# --- 4. Define Graph Logic ---
def should_continue(state: AgentState):
    """The 'manager' that decides whether to call a tool or end the conversation."""
    last_message = state['messages'][-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "call_tool"
    else:
        return END

# --- 5. Build the Final Graph ---
workflow = StateGraph(AgentState)

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