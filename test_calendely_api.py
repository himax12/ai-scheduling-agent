# test_calendly_api.py (Corrected with time range)
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

print("--- Starting Calendly API Direct Test ---")
load_dotenv()

API_KEY = os.getenv("CALENDLY_API_KEY")
USER_URI = os.getenv("CALENDLY_USER_URI")
EVENT_URI = os.getenv("CALENDLY_EVENT_TYPE_30_MIN_URI")

if not all([API_KEY, USER_URI, EVENT_URI]):
    print("❌ ERROR: One or more required variables are missing from your .env file.")
else:
    print("✅ All .env variables found.")
    
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    url = "https://api.calendly.com/event_type_available_times"

    # --- vvv THIS IS THE FIX vvv ---
    # Define the start and end time for the search (e.g., the next 7 days)
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(days=7)
    
    params = {
        "user": USER_URI,
        "event_type": EVENT_URI,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    # --- ^^^ THIS IS THE FIX ^^^ ---

    print(f"\nAttempting to call API...")
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"API Response Status Code: {response.status_code}")
        response.raise_for_status()
        
        data = response.json()
        print("\n✅ SUCCESS! API call was successful.")
        print("Response data:")
        print(data)
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ FAILED! An HTTP error occurred.")
        print(f"Error Details: {e.response.text}")
    except Exception as e:
        print(f"\n❌ FAILED! An unexpected error occurred: {e}")