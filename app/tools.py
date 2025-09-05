# app/tools.py

import os
import pandas as pd
from datetime import datetime, timedelta
from langchain_core.tools import tool
from app.utils import send_confirmation_email, schedule_reminders
import traceback
# --- Configuration: Define file paths for data ---
DATA_DIR = "./data"
PATIENT_DB_PATH = os.path.join(DATA_DIR, "patients.csv")
BOOKINGS_DB_PATH = os.path.join(DATA_DIR, "bookings.csv")

os.makedirs(DATA_DIR, exist_ok=True)


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


@tool
def get_available_slots(doctor_name: str, is_new_patient: bool) -> str:
    """Gets available, specific, and future weekday appointment slots for a given doctor."""
    print(f"🛠️ Tool Called: get_available_slots(doctor_name='{doctor_name}', is_new_patient={is_new_patient})")
    duration = 60 if is_new_patient else 30
    slots = []
    today = datetime.now()
    for i in range(1, 8):
        future_date = today + timedelta(days=i)
        if future_date.weekday() < 5: 
            def get_day_with_suffix(d):
                return str(d.day) + ("th" if 11 <= d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d.day % 10, "th"))
            date_str = f"{future_date.strftime('%A, %B')} {get_day_with_suffix(future_date)}, {future_date.year}"
            slots.append(f"{date_str} at 09:00 AM ({duration} min)")
            slots.append(f"{date_str} at 11:30 AM ({duration} min)")
        if len(slots) >= 4:
            break
    return f"SUCCESS: The following slots are available for Dr. {doctor_name}: {', '.join(slots)}."

# --- vvv THIS FUNCTION IS NOW CORRECTED vvv ---
# In app/tools.py

@tool
def book_appointment(patient_name: str, doctor_name: str, time: str) -> str:
    """
    Books an appointment, appends it to the log, and triggers notifications.
    This version includes detailed debugging print statements.
    """
    print("\n---DEBUG: Inside book_appointment tool---")
    print(f"Received Patient Name: {patient_name} (Type: {type(patient_name)})")
    print(f"Received Doctor Name: {doctor_name} (Type: {type(doctor_name)})")
    print(f"Received Appointment Time: {time} (Type: {type(time)})")

    try:
        print("Step 1: Determining if patient is new by reading CSV...")
        patients_df = pd.read_csv(PATIENT_DB_PATH)
        is_new_patient = patients_df[patients_df['name'].str.lower() == patient_name.lower()].empty
        print(f"Step 2: Patient status determined. Is New: {is_new_patient}")

        print("Step 3: Creating booking DataFrame...")
        new_booking = pd.DataFrame([{"patient_name": patient_name, "doctor_name": doctor_name, "appointment_time": time, "booking_date": datetime.now().strftime("%Y-%m-%d")}])
        
        print("Step 4: Writing to bookings.csv...")
        file_exists = os.path.exists(BOOKINGS_DB_PATH)
        new_booking.to_csv(BOOKINGS_DB_PATH, mode='a', header=not file_exists, index=False)
        print("Step 5: CSV write successful. Calling email utility...")
        
        send_confirmation_email(patient_name, doctor_name, time, is_new_patient)
        print("Step 6: Email utility successful. Calling reminder utility...")
        
        schedule_reminders(patient_name, time)
        print("Step 7: All steps successful. Returning SUCCESS.")
        
        return f"SUCCESS: The appointment has been successfully booked for {patient_name} with Dr. {doctor_name} at {time}."
    
    except Exception as e:
        print(f"\n--- ❌ DEBUG: ERROR caught in book_appointment tool ---")
        # This will print the full, detailed Python error to your terminal
        traceback.print_exc()
        print("-----------------------------------------------------\n")
        return f"ERROR: Could not book the appointment. Reason: {str(e)}"