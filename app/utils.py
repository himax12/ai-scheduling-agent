# app/utils.py

# app/utils.py

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
    
def schedule_reminders(patient_name: str, time: str):
    """
    A mock function to simulate scheduling SMS & email reminders.
    In a real application, this would add jobs to a task queue like Celery or RQ.
    """
    print("\n--- ⏰ SIMULATING SCHEDULING REMINDERS ---")
    print(f"1. [Action Registered] Send reminder to {patient_name} 24 hours before {time}.")
    print(f"2. [Action Registered] Send reminder to {patient_name} 3 hours before {time} (with form completion check).")
    print("--- ✅ REMINDERS SCHEDULED ---\n")