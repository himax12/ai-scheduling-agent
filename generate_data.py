# generate_data.py
import pandas as pd
from faker import Faker
import random
import os

# --- Configuration ---
DATA_DIR = "./data"
PATIENT_DB_PATH = os.path.join(DATA_DIR, "patients.csv")
DOCTOR_SCHEDULE_PATH = os.path.join(DATA_DIR, "dr schedules.xlsx")
NUM_PATIENTS = 50

# --- Initialize Faker ---
fake = Faker()

# --- Create Directory ---
os.makedirs(DATA_DIR, exist_ok=True)

# --- Generate Doctor Schedules ---
print("Generating doctor schedules...")
doctors_data = {
    'name': ['Dr. Adams', 'Dr. Chen', 'Dr. Patel', 'Dr. Lee'],
    'specialty': ['General Health', 'Cardiology', 'Orthopedics', 'Pediatrics']
}
doctors_df = pd.DataFrame(doctors_data)
doctors_df.to_excel(DOCTOR_SCHEDULE_PATH, index=False)
print(f"✅ Doctor schedules saved to {DOCTOR_SCHEDULE_PATH}")

# --- Generate Patient Database ---
print(f"Generating {NUM_PATIENTS} synthetic patients...")
patients = []
doctor_names = doctors_df['name'].tolist()

for _ in range(NUM_PATIENTS):
    patients.append({
        'name': fake.name(),
        'dob': fake.date_of_birth(minimum_age=1, maximum_age=90).strftime('%Y-%m-%d'),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'last_visit_doctor': random.choice(doctor_names)
    })

patients_df = pd.DataFrame(patients)
patients_df.to_csv(PATIENT_DB_PATH, index=False)
print(f"✅ Patient database saved to {PATIENT_DB_PATH}")

print("\nData generation complete!")