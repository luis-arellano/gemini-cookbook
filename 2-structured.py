import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, TypeAdapter
import json


#### DOCUMENTATION: https://ai.google.dev/gemini-api/docs/structured-output?lang=python

# --------------------------------------------------------------
# Step 1: Define the response format in a Pydantic model
# --------------------------------------------------------------

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

# --------------------------------------------------------------
# Step 2: Initialize Gemini client
# --------------------------------------------------------------

def initialize_gemini():
    """Initialize Gemini with API key."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)

# --------------------------------------------------------------
# Step 3: Generate and parse response
# --------------------------------------------------------------

def extract_event_info(client, text: str) -> CalendarEvent:
    """Extract event information using Gemini and return as CalendarEvent."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Extract event information from this text: {text}",
        config={
            'response_mime_type': 'application/json',
            'response_schema': CalendarEvent,
        }
    )    
    return response.parsed

def main():
    client = initialize_gemini()
    
    # Test input
    test_text = "Alice and Bob are going to a science fair on Friday."
    
    try:
        event = extract_event_info(client, test_text)
        print('RAW RESPONSE: ', event)
        print('RAW RESPONSE TYPE: ', type(event))
        
        # Convert to JSON in different ways:
        
        # Method 1: Using model_dump_json() - returns JSON string
        json_str = event.model_dump_json()
        print("\nJSON string (using model_dump_json):")
        print(json_str)
        print("Type:", type(json_str))
        
        # Method 2: Using model_dump() - returns dict
        event_dict = event.model_dump()
        print("\nPython dict (using model_dump):")
        print(event_dict)
        print("Type:", type(event_dict))
        
        # Convert dict to JSON string using json.dumps
        json_str_2 = json.dumps(event_dict, indent=2)
        print("\nJSON string (using json.dumps):")
        print(json_str_2)
        print("Type:", type(json_str_2))
        
        print("\nExtracted Event Information:")
        print(f"Name: {event.name}")
        print(f"Date: {event.date}")
        print(f"Participants: {', '.join(event.participants)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()