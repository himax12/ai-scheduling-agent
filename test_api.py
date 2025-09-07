# test_api.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import traceback

print("--- Starting Groq API Connection Test ---")

try:
    # Step 1: Load environment variables
    load_dotenv()
    print("✅ .env file loaded.")

    # Step 2: Check if the API key is present
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("ERROR: GROQ_API_KEY not found in your .env file.")
    print("✅ GROQ_API_KEY is present.")

    # Step 3: Initialize the ChatGroq client
    llm = ChatGroq(model_name="gemma2-9b-it")
    print("✅ ChatGroq client initialized successfully.")

    # Step 4: Make a simple API call
    print("\nAttempting a simple API call to Groq...")
    response = llm.invoke("Hello!")

    print("\n✅ SUCCESS! The API call was successful.")
    print("\nResponse from Groq:")
    print(response.content)

except Exception:
    print(f"\n❌ ERROR: The API call failed.")
    print("This is the traceback that will tell us what's wrong:")
    traceback.print_exc()

print("\n--- Test Complete ---")