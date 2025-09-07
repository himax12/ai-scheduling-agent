# find_uris.py (Corrected with direct API calls)
import os
import requests
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = os.getenv("CALENDLY_API_KEY")
    if not api_key:
        print("Error: CALENDLY_API_KEY not found in .env file.")
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 1. Get User Info
        user_info_url = "https://api.calendly.com/users/me"
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()  # This will raise an error if the request failed
        user_data = user_response.json()
        user_uri = user_data["resource"]["uri"]
        print(f"Your User URI is: {user_uri}\n")
        
        # 2. Get Event Types
        event_types_url = "https://api.calendly.com/event_types"
        params = {"user": user_uri}
        event_types_response = requests.get(event_types_url, headers=headers, params=params)
        event_types_response.raise_for_status()
        event_types_data = event_types_response.json()
        
        print("--- Available Event Types ---")
        for event in event_types_data.get("collection", []):
            print(f"Name: '{event['name']}'")
            print(f"  URI: {event['uri']}\n")

except requests.exceptions.HTTPError as e:
    print(f"An API error occurred: {e.response.status_code} - {e.response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
# find_uris.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = os.getenv("CALENDLY_API_KEY")
    if not api_key:
        print("Error: CALENDLY_API_KEY not found in .env file.")
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 1. Get User Info
        user_info_url = "https://api.calendly.com/users/me"
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        user_uri = user_data["resource"]["uri"]
        print(f"Your User URI is: {user_uri}\n")

        # 2. Get Event Types
        event_types_url = "https://api.calendly.com/event_types"
        params = {"user": user_uri}
        event_types_response = requests.get(event_types_url, headers=headers, params=params)
        event_types_response.raise_for_status()
        event_types_data = event_types_response.json()

        print("--- Available Event Types ---")
        for event in event_types_data.get("collection", []):
            print(f"Name: '{event['name']}'")
            print(f"  URI: {event['uri']}\n")

except requests.exceptions.HTTPError as e:
    print(f"An API error occurred: {e.response.status_code} - {e.response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")