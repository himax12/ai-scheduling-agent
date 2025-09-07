# app/utils.py

import pandas as pd
import os
from datetime import datetime

def generate_admin_report(): # <-- Corrected function name
    """
    Reads the bookings.csv file and exports its content to an Excel file
    for administrative review, as required by the case study.
    """
    bookings_csv_path = os.path.join("data", "bookings.csv")
    # Save the report to the data directory for organization
    report_excel_path = os.path.join("data", "admin_review_report.xlsx")

    if not os.path.exists(bookings_csv_path):
        return "No bookings.csv file found to export."

    try:
        df = pd.read_csv(bookings_csv_path, encoding='utf-8')
        
        desired_columns = ['booking_date', 'patient_name', 'doctor_name', 'appointment_time']
        existing_columns = [col for col in desired_columns if col in df.columns]
        df_report = df[existing_columns]
        
        df_report.to_excel(report_excel_path, index=False, sheet_name="Bookings")
        
        return f"✅ Report successfully generated: {report_excel_path}"
    except Exception as e:
        return f"❌ Failed to generate report. Error: {str(e)}"

# The following functions are placeholders and are not called directly by the UI.
# They are here to represent the full logic of the application.

def send_confirmation_email(patient_name: str, doctor_name: str, appointment_time: str, is_new_patient: bool):
    """
    A mock function to simulate sending a confirmation email.
    """
    form_message = "\nAs a next step, please complete the patient intake forms sent to your email." if is_new_patient else ""

    email_body = f"""
    Subject: Your Appointment Confirmation

    Dear {patient_name},

    This is a confirmation for your upcoming appointment with {doctor_name} at {appointment_time}.
    {form_message}

    We look forward to seeing you.

    Sincerely,
    The Clinic
    """
    print("\n--- 📧 SIMULATING SENDING CONFIRMATION EMAIL ---")
    print(email_body)
    print("--- ✅ EMAIL 'SENT' ---\n")

def schedule_reminders(patient_name: str, appointment_time: str):
    """
    A mock function to simulate scheduling SMS & email reminders.
    """
    print("\n--- ⏰ SIMULATING SCHEDULING REMINDERS ---")
    print(f"1. [Action Registered] Send reminder to {patient_name} 24 hours before {appointment_time}.")
    print(f"2. [Action Registered] Send reminder to {patient_name} 3 hours before {appointment_time} (with form completion check).")
    print(f"3. [Action Registered] Send final reminder to {patient_name} 1 hour before {appointment_time}.")
    print("--- ✅ REMINDERS SCHEDULED ---\n")