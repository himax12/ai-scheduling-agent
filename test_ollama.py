# test_ollama.py

from langchain_ollama import ChatOllama

print("--- 1. Initializing ChatOllama with 'mistral' model... ---")
try:
    # This connects to your local Ollama server
    llm = ChatOllama(model="phi3:mini", temperature=0)
    print("--- 2. Initialization successful. ---")
except Exception as e:
    print(f"--- ❌ FAILED to initialize. Error: {e} ---")
    exit()

print("--- 3. Sending a simple prompt to the model... (This may take a moment) ---")

try:
    # This sends the message and waits for a response
    response = llm.invoke("Why is the sky blue?")
    print("\n--- ✅ SUCCESS! Response received: ---")
    print(response)
except Exception as e:
    print(f"\n--- ❌ FAILED to get a response. Error: {e} ---")