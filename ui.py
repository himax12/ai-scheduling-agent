# ui.py

import streamlit as st
import requests
import uuid
from app.utils import export_to_excel

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000/chat"

# --- Page Setup ---
st.set_page_config(page_title="AI Medical Scheduler", page_icon="🩺")
st.title("AI Medical Scheduling Agent 🩺")

# --- Session State Initialization ---
# This ensures that the session ID and message history are preserved across reruns.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you book an appointment today?"}]

# --- Admin Panel Sidebar ---
st.sidebar.title("Admin Panel")
if st.sidebar.button("Generate Admin Report (Excel)"):
    with st.sidebar:
        with st.spinner("Generating report..."):
            result = export_to_excel()
            if "✅" in result:
                st.success(result)
            else:
                st.warning(result)

# --- Chat History Display ---
# Display all the messages stored in the session state.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and API Call ---
# This block runs when the user types a message and hits Enter.
if prompt := st.chat_input("What would you like to do?"):
    # 1. Add user's message to the session state and display it.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Prepare the data to send to the backend API.
    request_data = {
        "message": prompt,
        "session_id": st.session_state.session_id
    }
    
    # 3. Call the backend and handle the response.
    try:
        with st.spinner("Assistant is thinking... (This may take a moment)"):
            # We add a long timeout to patiently wait for the API response.
            response = requests.post(BACKEND_URL, json=request_data, timeout=120)
            
            # This line will raise an error if the API returns a non-200 status code.
            response.raise_for_status() 
            
            response_data = response.json()
            assistant_response = response_data["response"]

        # 4. Display the assistant's response and add it to the session state.
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
    except requests.exceptions.Timeout:
        st.error("The request timed out. The API might be taking too long to respond.")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to get response from backend. Error: {e}")