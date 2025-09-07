# test_calendly_api.py (Corrected with Timezone-Aware Timestamps)
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone # <-- Import timezone

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
    # Create a timezone-aware timestamp for the current time in UTC
    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(days=7)
    
    params = {
        "user": USER_URI,
        "event_type": EVENT_URI,
        # Format to the ISO 8601 standard with a 'Z' for UTC
        "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
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