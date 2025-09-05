# app/utils.py

import pandas as pd
import os
from datetime import datetime

def send_confirmation_email(patient_name: str, doctor_name: str, appointment_time: str, is_new_patient: bool):
    """
    A mock function to simulate sending a confirmation email.
    It now correctly accepts the 'is_new_patient' flag to customize the message.
    """
    form_message = "\nAs a next step, please complete the attached patient intake forms before your visit." if is_new_patient else ""

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
    print("--- ✅ REMINDERS SCHEDULED ---\n")

# In app/utils.py

def export_to_excel():
    """
    Reads the bookings.csv file and exports its content to an Excel file
    for administrative review. This version is robust to missing columns.
    """
    bookings_csv_path = os.path.join("data", "bookings.csv")
    report_excel_path = "admin_review_report.xlsx"

    if not os.path.exists(bookings_csv_path):
        return "No bookings found to export."

    try:
        df = pd.read_csv(bookings_csv_path)
        
        # Define the ideal column order for the report
        desired_columns = ['booking_date', 'patient_name', 'doctor_name', 'appointment_time']
        
        # Find which of our ideal columns actually exist in the CSV file
        existing_columns = [col for col in desired_columns if col in df.columns]
        
        # Create the report using only the columns that exist
        df_report = df[existing_columns]
        
        df_report.to_excel(report_excel_path, index=False, sheet_name="Bookings")
        
        return f"✅ Report successfully generated: {report_excel_path}"
    except Exception as e:
        return f"❌ Failed to generate report. Error: {str(e)}"