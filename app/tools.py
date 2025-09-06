# app/tools.py
from datetime import datetime, timedelta, timezone
import os
import pandas as pd
from datetime import datetime, timedelta
import requests
from langchain_core.tools import tool
from app.utils import send_confirmation_email, schedule_reminders
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
DATA_DIR = "./data"
PATIENT_DB_PATH = os.path.join(DATA_DIR, "patients.csv")
BOOKINGS_DB_PATH = os.path.join(DATA_DIR, "bookings.csv")
os.makedirs(DATA_DIR, exist_ok=True)
CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {CALENDLY_API_KEY}",
    "Content-Type": "application/json"
}

@tool
def search_patient_in_emr(full_name: str, dob: str) -> str:
    """Looks up a patient by their full name and date of birth (YYYY-MM-DD) in the EMR."""
    print(f"🛠️ Tool Called: search_patient_in_emr(full_name='{full_name}', dob='{dob}')")
    try:
        patients_df = pd.read_csv(PATIENT_DB_PATH)
        patient = patients_df[(patients_df['name'].str.lower() == full_name.lower()) & (patients_df['dob'] == dob)]
        if not patient.empty:
            return f"SUCCESS: Found returning patient. Details: {patient.to_dict('records')[0]}"
        else:
            return "SUCCESS: This is a new patient."
    except Exception as e:
        return f"ERROR: An unexpected error occurred: {str(e)}"

# In app/tools.py

# In app/tools.py

@tool
def get_available_slots(is_new_patient: bool) -> str:
    """Gets real-time available appointment slots from the Calendly API."""
    print(f"🛠️ Tool Called: get_available_slots(is_new_patient={is_new_patient})")
    if not CALENDLY_API_KEY:
        return "ERROR: Calendly API key is not configured."
        
    try:
        event_type_uri = os.getenv("CALENDLY_EVENT_TYPE_60_MIN_URI") if is_new_patient else os.getenv("CALENDLY_EVENT_TYPE_30_MIN_URI")
        user_uri = os.getenv("CALENDLY_USER_URI")
        
        if not user_uri or not event_type_uri:
            return "ERROR: Calendly User or Event URI is not configured in .env file."

        url = "https://api.calendly.com/event_type_available_times"
        
        # --- vvv THIS IS THE FIX vvv ---
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(days=7)
        
        params = {
            "user": user_uri,
            "event_type": event_type_uri,
            "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
        # --- ^^^ THIS IS THE FIX ^^^ ---
        
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        
        slots = [datetime.fromisoformat(slot['start_time'].replace("Z", "+00:00")).strftime('%A, %B %d, %Y at %I:%M %p') for slot in data.get('collection', [])]
        
        if not slots:
            return "SUCCESS: No available slots found in the next 7 days."
            
        return f"SUCCESS: The following slots are available: {', '.join(slots[:5])}."
    except requests.exceptions.HTTPError as e:
        return f"ERROR: Could not retrieve slots from Calendly. API Error: {e.response.text}"
    except Exception as e:
        return f"ERROR: Could not retrieve slots from Calendly. Reason: {str(e)}"
@tool
def book_appointment(patient_name: str, doctor_name: str, appointment_time: str) -> str:
    """Logs the confirmed appointment and triggers notifications."""
    print(f"🛠️ Tool Called: book_appointment(patient_name='{patient_name}', appointment_time='{appointment_time}')")
    try:
        patients_df = pd.read_csv(PATIENT_DB_PATH)
        is_new_patient = patients_df[patients_df['name'].str.lower() == patient_name.lower()].empty
        
        new_booking = pd.DataFrame([{"patient_name": patient_name, "doctor_name": doctor_name, "appointment_time": appointment_time, "booking_date": datetime.now().strftime("%Y-%m-%d")}])
        new_booking.to_csv(BOOKINGS_DB_PATH, mode='a', header=not os.path.exists(BOOKINGS_DB_PATH), index=False)
        
        send_confirmation_email(patient_name, doctor_name, appointment_time, is_new_patient)
        schedule_reminders(patient_name, appointment_time)
        
        return f"SUCCESS: The appointment has been successfully booked for {patient_name} with {doctor_name} at {appointment_time}. The user has been notified."
    except Exception as e:
        return f"ERROR: Could not log the appointment booking. Reason: {str(e)}"
    
@tool
def collect_insurance_details(carrier: str, member_id: str, group_number: str) -> str:
    """Collects the patient's insurance information."""
    print(f"🛠️ Tool Called: collect_insurance_details(carrier='{carrier}', member_id='{member_id}')")
    # In a real application, this would be saved to a database.
    # For this case study, we just confirm it was collected.
    return f"SUCCESS: Insurance details for {carrier} have been collected and stored."

# In app/tools.py

@tool
def skip_insurance() -> str:
    """Call this tool when the user indicates they do not have or do not want to provide insurance information."""
    print(f"🛠️ Tool Called: skip_insurance()")
    return "SUCCESS: Insurance step has been skipped."