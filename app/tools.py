# app/tools.py

import os
import re
import pandas as pd
from pydantic.v1 import BaseModel, Field 
from datetime import datetime, timedelta, timezone
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
DATA_DIR = "./data"
PATIENT_DB_PATH = os.path.join(DATA_DIR, "patients.csv")
BOOKINGS_DB_PATH = os.path.join(DATA_DIR, "bookings.csv")
DOCTOR_SCHEDULE_PATH = os.path.join(DATA_DIR, "dr schedules.xlsx")

os.makedirs(DATA_DIR, exist_ok=True)
CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {CALENDLY_API_KEY}",
    "Content-Type": "application/json"
}

# --- Helper Function for Date Validation ---
def _validate_and_normalize_date(date_string: str) -> str | None:
    """Attempts to parse a date string into YYYY-MM-DD format."""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_string, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None

# --- Tool Definitions ---


@tool
def search_patient_in_emr(full_name: str, dob: str) -> str:
    """Looks up a patient by their full name and date of birth in the EMR."""
    print(f"🛠️ Tool Called: search_patient_in_emr(full_name='{full_name}', dob='{dob}')")
    
    normalized_dob = _validate_and_normalize_date(dob)
    if not normalized_dob:
        return f"ERROR: The date of birth '{dob}' is not in a recognized format. Please use YYYY-MM-DD."

    try:
        patients_df = pd.read_csv(PATIENT_DB_PATH, encoding='utf-8')
        patients_df['dob'] = pd.to_datetime(patients_df['dob']).dt.strftime('%Y-%m-%d')
        
        patient = patients_df[
            (patients_df['name'].str.lower() == full_name.lower()) & 
            (patients_df['dob'] == normalized_dob)
        ]
        
        if not patient.empty:
            return f"SUCCESS: Found returning patient. Details: {patient.to_dict('records')[0]}"
        else:
            return "SUCCESS: This is a new patient."
    except FileNotFoundError:
        return "SUCCESS: This is a new patient."
    except Exception as e:
        return f"ERROR: An unexpected error occurred while searching the EMR: {str(e)}"

@tool
def get_doctor_list() -> str:
    """Gets the list of available doctors and their specialties from an Excel file."""
    print("🛠️ Tool Called: get_doctor_list()")
    try:
        doctors_df = pd.read_excel(DOCTOR_SCHEDULE_PATH)
        doctors = doctors_df.to_dict('records')
        # ... (rest of the code)
    except FileNotFoundError:
        return f"ERROR: The doctor schedule file was not found at {DOCTOR_SCHEDULE_PATH}."
    except Exception as e:
        return f"ERROR: An unexpected error occurred while reading the doctor schedule: {str(e)}"
class GetSlotsInput(BaseModel):
    is_new_patient: bool = Field(..., description="Set to true for a new patient (60 min), false for a returning patient (30 min).")

@tool(args_schema=GetSlotsInput)
def get_available_slots(is_new_patient: bool) -> str:
    """Gets real-time available appointment slots from the Calendly API."""
    print(f"🛠️ Tool Called: get_available_slots(is_new_patient={is_new_patient})")
    
    if not CALENDLY_API_KEY:
        return "ERROR: Calendly API key is not configured."
        
    try:
        # Business logic: 60min for new patients, 30min for returning
        event_type_uri = os.getenv("CALENDLY_EVENT_TYPE_60_MIN_URI") if is_new_patient else os.getenv("CALENDLY_EVENT_TYPE_30_MIN_URI")
        user_uri = os.getenv("CALENDLY_USER_URI")
        
        if not user_uri or not event_type_uri:
            return "ERROR: Calendly User or Event URI is not configured in .env file."

        url = "https://api.calendly.com/event_type_available_times"
        start_time = datetime.now(timezone.utc) + timedelta(minutes=1)
        end_time = start_time + timedelta(days=7)
        params = {
            "user": user_uri,
            "event_type": event_type_uri,
            "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
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
    """Logs the confirmed appointment details to a CSV file."""
    print(f"🛠️ Tool Called: book_appointment(patient_name='{patient_name}', appointment_time='{appointment_time}')")
    
    if not re.search(r'\d{1,2}:\d{2}\s*(?:AM|PM)', appointment_time, re.IGNORECASE):
        return f"ERROR: The appointment time '{appointment_time}' is invalid."
    try:
        new_booking = pd.DataFrame([{"patient_name": patient_name, "doctor_name": doctor_name, "appointment_time": appointment_time, "booking_date": datetime.now().strftime("%Y-%m-%d")}])
        new_booking.to_csv(BOOKINGS_DB_PATH, mode='a', header=not os.path.exists(BOOKINGS_DB_PATH), index=False)
        return f"SUCCESS: The appointment has been successfully booked for {patient_name} with {doctor_name} at {appointment_time}."
    except Exception as e:
        return f"ERROR: Could not log the appointment booking. Reason: {str(e)}"


@tool
def collect_insurance_details(carrier: str, member_id: str, group_number: str) -> str:
    """Collects the patient's insurance information."""
    print(f"🛠️ Tool Called: collect_insurance_details(carrier='{carrier}', member_id='{member_id}')")
    return f"SUCCESS: Insurance details for {carrier} have been collected and stored."

@tool
def skip_insurance() -> str:
    """Call this tool when the user indicates they do not have or do not want to provide insurance information."""
    print(f"🛠️ Tool Called: skip_insurance()")
    return "SUCCESS: Insurance step has been skipped."

@tool
def send_intake_forms(patient_name: str, patient_email: str) -> str:
    """Emails the required intake forms to a patient after their appointment is confirmed."""
    print(f"🛠️ Tool Called: send_intake_forms(patient_name='{patient_name}', email='{patient_email}')")
    # In a real app, this would use an email library.
    return f"SUCCESS: Intake forms have been sent via EMAIL to {patient_name} at {patient_email}."


@tool
def schedule_reminders(patient_name: str, patient_email: str, patient_phone: str, appointment_time: str) -> str:
    """Schedules 3 automated reminders for the patient via email and SMS."""
    print(f"🛠️ Tool Called: schedule_reminders for {patient_name} at {appointment_time}")
    # In a real app, this would integrate with a task scheduler like Celery or APScheduler.
    return f"SUCCESS: 3 reminders have been scheduled for {patient_name} via EMAIL ({patient_email}) and SMS ({patient_phone})."