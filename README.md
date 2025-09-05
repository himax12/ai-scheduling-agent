# AI Medical Scheduling Agent

This project is a sophisticated, AI-powered medical appointment scheduling agent . The agent automates the entire patient booking process, from initial contact to final confirmation, aiming to reduce no-shows and streamline clinic operations.

The core of this project is a robust, state-aware agent built with LangGraph that can handle multi-turn conversations, manage context, and interact with external data sources and APIs.

## Features

- **Patient Onboarding:** The agent greets users and intelligently collects patient information (Name, DOB).
- **Patient Lookup:** The agent connects to a mock EMR (`patients.csv`) to distinguish between new and returning patients.
- **Smart Scheduling:** The agent applies business logic to assign 60-minute appointment slots for new patients and 30-minute slots for returning patients.
- **Insurance Collection:** The agent includes a dedicated step to capture the patient's insurance carrier, member ID, and group number.
- **Live Calendar Integration:** The agent connects directly to the Calendly API to fetch real-time appointment availability, offering users up-to-date scheduling options.
- **Booking & Confirmation:** The agent logs confirmed appointments to a local CSV and provides the user with a clear confirmation message.
- **Automated Notifications (Simulated):** The agent triggers mock email confirmations (including intake forms for new patients) and SMS reminders upon successful booking.
- **Admin Reporting:** The agent features a one-click function to export the booking log from `bookings.csv` to an Excel file for administrative review.

## Technical Stack

This project was built using **Option 1** from the case study requirements.

- **Orchestration:** LangGraph & LangChain
- **Language Model (LLM):** Groq API (using `MODEL OF YOUR CHOICE `)
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Data Handling:** Pandas
- **Dependency Management:** Poetry

## Project Setup & Execution

### Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation) for package management.
- A [GroqCloud](https://console.groq.com/keys) account and API key.
- A [Calendly](https://calendly.com/) account with a Personal Access Token and at least two event types created (e.g., 30-min and 60-min).

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai-scheduling-agent
```

### 2. Install Dependencies

Poetry creates a virtual environment and installs all required libraries from `pyproject.toml`.

```bash
poetry install
```

### 3. Configure Environment Variables

A `.env` file is created in the root of the project directory. The following credentials are required:

- `GROQ_API_KEY`: Obtained from the GroqCloud account.
- `CALENDLY_API_KEY`: The Personal Access Token from Calendly Integrations.
- `CALENDLY_USER_URI`, `CALENDLY_EVENT_TYPE_30_MIN_URI`, `CALENDLY_EVENT_TYPE_60_MIN_URI`: The included helper script is run to find these values:

```bash
poetry run python find_uris.py
```

The output is then copied into the `.env` file.

The final `.env` file resembles this:

```
GROQ_API_KEY="gsk_..."
CALENDLY_API_KEY="ey..."
CALENDLY_USER_URI="https://api.calendly.com/users/..."
CALENDLY_EVENT_TYPE_30_MIN_URI="https://api.calendly.com/event_types/..."
CALENDLY_EVENT_TYPE_60_MIN_URI="https://api.calendly.com/event_types/..."
```

### 4. Run the Application

The backend and frontend are run in two separate terminals.

**Terminal 1: Start the Backend (FastAPI)**

```bash
poetry run uvicorn app.main:app --reload
```

**Terminal 2: Start the Frontend (Streamlit)**

```bash
poetry run streamlit run ui.py
```

A browser window with the Streamlit chatbot interface opens automatically.
