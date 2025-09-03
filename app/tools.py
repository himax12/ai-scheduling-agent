# app/tools.py

from langchain_core.tools import tool
import pandas as pd
from datetime import datetime
import os

# --- Configuration: Define file paths for data ---
DATA_DIR = "./data"
PATIENT_DB_PATH = os.path.join(DATA_DIR, "patients.csv")
BOOKINGS_DB_PATH = os.path.join(DATA_DIR, "bookings.csv")
SCHEDULE_DB_PATH = os.path.join(DATA_DIR, "doctor_schedules.xlsx")

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


@tool
def search_patient_in_emr(full_name: str, dob: str) -> str:
    """
    Looks up a patient by their full name and date of birth (YYYY-MM-DD)
    in the EMR. Returns the patient's status (new or returning) and details if found.
    """
    print(f"🛠️ Tool Called: search_patient_in_emr(full_name='{full_name}', dob='{dob}')")
    try:
        # Load the patient database from the CSV file
        patients_df = pd.read_csv(PATIENT_DB_PATH)
        
        # Search for a matching patient (case-insensitive name)
        patient = patients_df[
            (patients_df['name'].str.lower() == full_name.lower()) & 
            (patients_df['dob'] == dob)
        ]
        
        if not patient.empty:
            # If we found a patient, return their details
            patient_details = patient.to_dict('records')[0]
            return f"SUCCESS: Found returning patient. Details: {patient_details}"
        else:
            # If no patient was found
            return "SUCCESS: This is a new patient."
    except FileNotFoundError:
        return "ERROR: The patient database file was not found. Please tell the user you're having technical difficulties."
    except Exception as e:
        return f"ERROR: An unexpected error occurred while searching for the patient: {str(e)}"


@tool
def get_available_slots(doctor_name: str, is_new_patient: bool) -> str:
    """
    Gets available appointment slots for a given doctor. 
    New patients get 60-minute slots, returning patients get 30-minute slots.
    This is a mock function and returns a fixed list of slots for demonstration.
    """
    print(f"🛠️ Tool Called: get_available_slots(doctor_name='{doctor_name}', is_new_patient={is_new_patient})")
    duration = 60 if is_new_patient else 30
    # In a real system, you would read SCHEDULE_DB_PATH and check against BOOKINGS_DB_PATH
    slots = [
        f"Tomorrow at 09:00 AM ({duration} min)",
        f"Tomorrow at 11:30 AM ({duration} min)",
        f"Tomorrow at 02:00 PM ({duration} min)",
        f"The day after tomorrow at 10:00 AM ({duration} min)",
    ]
    return f"SUCCESS: The following slots are available for Dr. {doctor_name}: {', '.join(slots)}."


@tool
def book_appointment(patient_name: str, doctor_name: str, appointment_time: str) -> str:
    """
    Books an appointment for a patient with a specific doctor at a given time.
    This function appends the booking to the bookings.csv file.
    """
    print(f"🛠️ Tool Called: book_appointment(patient_name='{patient_name}', doctor_name='{doctor_name}', appointment_time='{appointment_time}')")
    try:
        # Create a new DataFrame for the new booking
        new_booking = pd.DataFrame([{
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "appointment_time": appointment_time,
            "booking_date": datetime.now().strftime("%Y-%m-%d")
        }])
        
        # Check if the bookings file exists to decide whether to write headers
        file_exists = os.path.exists(BOOKINGS_DB_PATH)
        
        # Append the new booking to our bookings log
        new_booking.to_csv(BOOKINGS_DB_PATH, mode='a', header=not file_exists, index=False)
        
        return f"SUCCESS: The appointment has been successfully booked for {patient_name} with Dr. {doctor_name} at {appointment_time}."
    except Exception as e:
        return f"ERROR: Could not book the appointment due to a system error. Reason: {str(e)}"