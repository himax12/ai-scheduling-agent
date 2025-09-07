# app/agent.py

import operator
import re
import json
from typing import Annotated, Optional, TypedDict, List, Dict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage, ToolCall # <-- CORRECTED IMPORT
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langchain_groq import ChatGroq

# Import ALL tools
from app.tools import (
    book_appointment,
    get_available_slots,
    search_patient_in_emr,
    collect_insurance_details,
    skip_insurance,
    get_doctor_list,
    send_intake_forms,
    schedule_reminders,
)

# --- 1. Define the Agent's State ---
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    patient_status: Optional[str]
    patient_info: Optional[Dict[str, str]]
    insurance_info: Optional[str]
    doctor_list: Optional[List[Dict[str, str]]]
    doctor_name: Optional[str]
    available_slots: Optional[List[str]]
    confirmed_time: Optional[str]

# --- 2. Setup Tools and LLM ---
tools = [
    search_patient_in_emr,
    get_available_slots,
    book_appointment,
    collect_insurance_details,
    skip_insurance,
    get_doctor_list,
    send_intake_forms,
    schedule_reminders,
]
tool_map = {t.name: t for t in tools}

llm = ChatGroq(model_name="openai/gpt-oss-20b", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# --- 3. Define the Agent's Nodes ---

def agent_brain(state: AgentState):
    """The 'brain'. Decides which tool to call based on the user's last message."""
    print("---NODE: AGENT BRAIN---")
    system_prompt = "You are an autonomous medical scheduling assistant. Based on the user's last message, decide which tool to call. Do not respond conversationally."
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tool_and_update_state(state: AgentState):
    """The 'hands'. Executes tools and updates the agent's state."""
    print("---NODE: CALLING TOOL & UPDATING STATE---")
    last_message = state["messages"][-1]
    
    updates = {}
    for tool_call in last_message.tool_calls:
        tool_to_call = tool_map[tool_call["name"]]
        tool_output = tool_to_call.invoke(tool_call["args"])
        
        if tool_call["name"] == "search_patient_in_emr":
            if "new patient" in tool_output.lower():
                updates["patient_status"] = "NEW"
                updates["patient_info"] = tool_call.get("args", {})
            elif "returning patient" in tool_output.lower():
                updates["patient_status"] = "RETURNING"
                match = re.search(r"({.*})", tool_output.replace("'", '"'))
                if match:
                    patient_details = json.loads(match.group(1))
                    updates["patient_info"] = patient_details
                    updates["doctor_name"] = patient_details.get("last_visit_doctor")
        elif tool_call["name"] == "skip_insurance":
            updates["insurance_info"] = "Not Provided"
        elif tool_call["name"] == "collect_insurance_details":
            updates["insurance_info"] = tool_output
        elif tool_call["name"] == "get_doctor_list":
            match = re.search(r"(\[.*\])", tool_output)
            if match:
                valid_json_string = match.group(1).replace("'", '"')
                updates["doctor_list"] = json.loads(valid_json_string)
        elif tool_call["name"] == "get_available_slots":
            if "SUCCESS: The following slots are available" in tool_output:
                slots_text = tool_output.split("SUCCESS: The following slots are available")[1]
                updates["available_slots"] = [s.strip() for s in slots_text.split(":")[-1].split(",")]
        
        updates.setdefault("messages", []).append(
            ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
        )
    return updates

def extract_user_choice(state: AgentState):
    """Parses the user's last message to update the state."""
    print("---NODE: EXTRACTING USER CHOICE---")
    last_message = state["messages"][-1].content
    updates = {}

    if state.get("patient_status") == "RETURNING" and not state.get("insurance_info"):
        if "different" in last_message.lower() or "choose" in last_message.lower():
            updates["doctor_name"] = None
            updates["doctor_list"] = None
        else: # Assumes confirmation
            updates["insurance_info"] = "Confirmed"

    if state.get("doctor_list") and not state.get("doctor_name"):
        for doctor in state["doctor_list"]:
            if doctor["name"].lower() in last_message.lower():
                updates["doctor_name"] = doctor["name"]
                break
    
    if state.get("available_slots") and not state.get("confirmed_time"):
        for slot in state["available_slots"]:
            time_part = slot.split(" at ")[-1]
            if time_part.lower() in last_message.lower():
                updates["confirmed_time"] = slot
                break
    return updates
    
# --- Nodes for reliable, hardcoded tasks ---
def ask_for_insurance(state: AgentState):
    print("---NODE: ASK FOR INSURANCE---")
    return {"messages": [AIMessage(content="To proceed, could you please provide your insurance carrier, member ID, and group number? If you don't have insurance, just let me know.")]}

def ask_or_confirm_doctor(state: AgentState):
    print("---NODE: ASK/CONFIRM DOCTOR---")
    if state.get("patient_status") == "RETURNING":
        doctor_name = state.get("doctor_name")
        return {"messages": [AIMessage(content=f"Welcome back! Your last visit was with {doctor_name}. Would you like to schedule with them again or see a different doctor?")]}
    else:
        doctor_options = "\n".join([f"- {d['name']} ({d['specialty']})" for d in state.get("doctor_list", [])])
        return {"messages": [AIMessage(content=f"Thank you. Here are our available doctors. Please choose one:\n{doctor_options}")]}

def present_slots(state: AgentState):
    print("---NODE: PRESENT SLOTS---")
    slots = state.get("available_slots")
    if not slots:
        return {"messages": [AIMessage(content="I'm sorry, but there are no available slots for that doctor in the near future. Would you like to try a different doctor?")]}
    return {"messages": [AIMessage(content=f"Great, here are the available slots: {', '.join(slots)}. Please choose your preferred time.")]}

def final_confirmation(state: AgentState):
    print("---NODE: FINAL CONFIRMATION---")
    tool_messages = [msg.content for msg in state.get("messages", []) if isinstance(msg, ToolMessage)]
    final_booking_message = tool_messages[-3] # Assuming book_appointment is the first of the last three tools
    return {"messages": [AIMessage(content=f"Excellent, we're all set! {final_booking_message} We've also sent the intake forms to your email and scheduled reminders.")]}

def call_get_doctor_list_node(state: AgentState):
    """A dedicated node to call the get_doctor_list tool."""
    print("---NODE: GETTING DOCTOR LIST---")
    return {"messages": [AIMessage(content="", tool_calls=[ToolCall(name="get_doctor_list", args={}, id="get_docs")])]}
    
def call_get_available_slots_node(state: AgentState):
    """A dedicated node to call the get_available_slots tool."""
    print("---NODE: GETTING SLOTS---")
    is_new = state.get("patient_status") == "NEW"
    return {"messages": [AIMessage(content="", tool_calls=[ToolCall(name="get_available_slots", args={"is_new_patient": is_new}, id="get_slots")])]}

# --- 4. The Main Router ---
def router(state: AgentState):
    """The main router. It inspects the state and decides the next step."""
    print("---NODE: ROUTER---")
    
    last_message = state["messages"][-1]
    
    if isinstance(last_message, HumanMessage):
        return "agent_brain"

    if isinstance(last_message, ToolMessage):
        parent_ai_message = next((msg for msg in reversed(state["messages"]) if isinstance(msg, AIMessage) and msg.tool_calls), None)
        last_tool_name = parent_ai_message.tool_calls[-1]["name"]
        
        if last_tool_name == "search_patient_in_emr":
            return "ask_for_insurance" if state.get("patient_status") == "NEW" else "ask_or_confirm_doctor"
        if last_tool_name in ["collect_insurance_details", "skip_insurance"]:
            return "call_get_doctor_list" if state.get("patient_status") == "NEW" else "call_get_available_slots"
        if last_tool_name == "get_doctor_list":
            return "ask_or_confirm_doctor"
        if last_tool_name == "get_available_slots":
            return "present_slots"
        if last_tool_name == "book_appointment":
            return "agent_brain"
        if last_tool_name in ["send_intake_forms", "schedule_reminders"]:
            return "final_confirmation"
            
    return END

# --- 5. Build the Final Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("agent_brain", agent_brain)
workflow.add_node("call_tool", call_tool_and_update_state)
workflow.add_node("extract_user_choice", extract_user_choice)
workflow.add_node("ask_for_insurance", ask_for_insurance)
workflow.add_node("ask_or_confirm_doctor", ask_or_confirm_doctor)
workflow.add_node("present_slots", present_slots)
workflow.add_node("final_confirmation", final_confirmation)
workflow.add_node("call_get_doctor_list", call_get_doctor_list_node)
workflow.add_node("call_get_available_slots", call_get_available_slots_node)

workflow.set_entry_point("agent_brain")

workflow.add_conditional_edges("agent_brain", lambda x: "call_tool")
workflow.add_edge("call_get_doctor_list", "call_tool")
workflow.add_edge("call_get_available_slots", "call_tool")

# This is the central routing logic after a tool is called
workflow.add_conditional_edges("call_tool", router)

# After the user replies to a question, we extract their choice, then go to the brain
workflow.add_edge("ask_for_insurance", "agent_brain")
workflow.add_edge("ask_or_confirm_doctor", "agent_brain")
workflow.add_edge("present_slots", "agent_brain")

workflow.add_edge("final_confirmation", END)

app_graph = workflow.compile(checkpointer=MemorySaver())