# ui.py

import streamlit as st
import requests
import uuid
import os
from app.utils import generate_admin_report # Import the utility function

# --- Page Configuration ---
st.set_page_config(page_title="AI Medical Scheduler", layout="centered")
st.title("👩‍⚕️ AI Medical Scheduling Agent")

# --- State Management ---
# Initialize session_id and messages if they don't exist
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you book an appointment today?"}]

# --- UI Rendering ---
# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and Backend Interaction ---
if prompt := st.chat_input("How can I help you?"):
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Call the FastAPI backend
            api_url = "http://127.0.0.1:8000/chat"
            response = requests.post(api_url, json={"message": prompt, "session_id": st.session_state.session_id})
            response.raise_for_status() # Raise an exception for bad status codes
            
            full_response = response.json().get("response", "Sorry, I encountered an error.")
            message_placeholder.markdown(full_response)
            
        except requests.exceptions.RequestException as e:
            full_response = f"Error: Could not connect to the backend. Please ensure it's running. Details: {e}"
            message_placeholder.markdown(full_response)

    # Add assistant response to state
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Admin Panel ---
st.sidebar.title("Admin Panel")
st.sidebar.write("Manage system reports and data.")

if st.sidebar.button("Generate Admin Report"):
    with st.spinner("Generating report..."):
        report_status = generate_admin_report()
        st.sidebar.success(report_status)