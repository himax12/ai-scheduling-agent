# AI Medical Scheduling Agent

This project is an AI agent that automates patient appointment scheduling.

## Tech Stack

- Python, Poetry
- FastAPI (Backend)
- Streamlit (Frontend)
- LangChain / LangGraph with Google Gemini

## Setup Instructions

1.  **Clone the repository:**
    `git clone <your-repo-url>`
    `cd ai-scheduling-agent`

2.  **Install dependencies using Poetry:**
    `poetry install`

3.  **Set up your environment variables:**
    Create a `.env` file in the root directory and add your Google API key:
    `GOOGLE_API_KEY="your_api_key_here"`

4.  **Run the application:**

    - **Terminal 1 (Backend):** `poetry run uvicorn app.main:app --reload`
    - **Terminal 2 (Frontend):** `poetry run streamlit run ui.py`

5.  Open your browser to the Streamlit address provided (usually `http://localhost:8501`).
