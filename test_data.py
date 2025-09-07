 # test_data.py
import pandas as pd
import os
import traceback

print("--- Starting Data File Test ---")

# Define the path exactly as it is in your tools.py
DATA_DIR = "./data"
PATIENT_DB_PATH = os.path.join(DATA_DIR, "patients.csv")

try:
    print(f"Attempting to read file from path: {os.path.abspath(PATIENT_DB_PATH)}")

    # Use the same logic as the tool to read the file
    patients_df = pd.read_csv(PATIENT_DB_PATH, encoding='utf-8')

    print("\n✅ SUCCESS! The patients.csv file was read successfully.")
    print(f"Number of patients found: {len(patients_df)}")
    print("\nFirst 3 rows of data:")
    print(patients_df.head(3))

except FileNotFoundError:
    print("\n❌ ERROR: FileNotFoundError")
    print(f"The file was not found at the expected path: {os.path.abspath(PATIENT_DB_PATH)}")
    print("Please make sure your 'patients.csv' file is inside the 'data' directory.")

except Exception:
    print(f"\n❌ ERROR: An unexpected error occurred while reading the file.")
    print("This is the traceback that we need to fix the issue:")
    # Print the full traceback
    traceback.print_exc()

print("\n--- Test Complete ---")