import streamlit as st
import requests # The library to send HTTP requests

# Define the URL of our backend API
BACKEND_URL = "http://127.0.0.1:8000"

st.title("AI Medical Scheduling Agent 🩺")

# Check the backend health and display a status message
try:
    # Send a GET request to the root endpoint of our API
    response = requests.get(BACKEND_URL)

    # Raise an error if the response status code is not 200 (OK)
    response.raise_for_status()

    # If the request was successful, show a success message
    st.success("✅ Connected to Backend API successfully!")

except requests.exceptions.RequestException as e:
    # If we couldn't connect, show an error message
    st.error(f"❌ Failed to connect to Backend API. Please ensure the backend is running. Error: {e}")

# We will add the chat interface code here later