# ui.py

import streamlit as st
import requests
import uuid

BACKEND_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="AI Medical Scheduler", page_icon="🩺")
st.title("AI Medical Scheduling Agent 🩺")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you book an appointment today?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to do?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    request_data = {
        "message": prompt,
        "session_id": st.session_state.session_id
    }
    
    try:
        with st.spinner("Assistant is thinking... (This may take a moment for local models)"):
            # --- vvv THIS IS THE FIX vvv ---
            # We've added timeout=120 to wait up to 2 minutes for a response
            response = requests.post(BACKEND_URL, json=request_data, timeout=120)
            # --- ^^^ THIS IS THE FIX ^^^ ---

            response.raise_for_status() 
            response_data = response.json()
            assistant_response = response_data["response"]

        with st.chat_message("assistant"):
            st.markdown(assistant_response)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
    except requests.exceptions.Timeout:
        st.error("The request timed out. The model might be taking too long to respond.")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to get response from backend. Error: {e}")