import json
import os

import requests
from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pprint import pprint, PrettyPrinter

pp = PrettyPrinter(indent=2, width=80)


# Configure Gemini Pro API

"""
github: https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini
https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/function-calling
"""

# Configure Gemini Pro API
def initialize_gemini():
    """Initialize Gemini with API key."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)

# --------------------------------------------------------------
# Define the tools (function) that we want to call
# Gemini uses Python's native type hits and docstring to automatically
# understand the function signature and requirements
# --------------------------------------------------------------

def set_light_values(brightness: int, color_temp: str) -> dict[any,any]:
    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    print('CALLING SET_LIGHT_VALUES: ', brightness, color_temp)
    return {
        "brightness": brightness,
        "colorTemperature": color_temp
    }
    
def get_weather(latitude: float, longitude: float) -> dict[str, float]:
    """Get current weather data for a specific location.

    Args:
        latitude: Location latitude (between -90 and 90 degrees)
        longitude: Location longitude (between -180 and 180 degrees)

    Returns:
        A dictionary containing current weather metrics:
        - temperature_2m: Current temperature in Celsius
        - wind_speed_10m: Current wind speed in km/h
    """
    print('CALLING GET_WEATHER: ', latitude, longitude)
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]
    
def test_light_control():
    client = initialize_gemini()
     
    config = {
        'tools': [set_light_values],
    }

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        config=config,
        contents='Turn the lights down to a romantic level'
    )
    print("\nLight Control Test:")
    print(response.text)

def test_weather():
    client = initialize_gemini()
     
    config = {
        'tools': [get_weather],
    }

    response = client.models.generate_content(
        # model='gemini-2.0-flash', # This model doesn't know the latitude and longitude of Paris
        model='gemini-1.5-pro', # This model knows the latitude and longitude of Paris
        config=config,
        contents="What's the current temperature in Paris, France?"
    )
    print("\nWeather Test:")
    print(response.text)
    
def test_function_calling_config():
    client = initialize_gemini()
     
    config = {
        'tools': [get_weather, set_light_values],
        ### Force the model to act (call 'any' function), instead of chatting.
        # 'tool_config': {
        #     'function_calling_config': {
        #         'mode': 'ANY'
        #     }
        # }
        ### Disable automatic function calling, this is useful when we want to get the function call request, without executing it.
        ## We don't get an LLM text response, only the function call request. so we can control the logic flow more precisely.
        # 'automatic_function_calling': {'disable': True},  
        }
    
    # --------------------------------------------------------------
    # NOTE:
    # Gemini doesn't show it's thinking when calling functions. So use with caution.
    # for example we can add the get_weather and set_lights functions, and ask a question that requires both functions.
    # e.g What is the weather like in Paris? If it's not good, set the lights to a romantic level.
    # Gemini's behavior is to randomly pick one or both functions, and not necessarily follow a commmon sense logic (first check weather, then depending on the weather, set the lights).
    # --------------------------------------------------------------

    response = client.models.generate_content(
        # model='gemini-2.0-flash', # This model doesn't know the latitude and longitude of Paris
        model='gemini-1.5-pro', # This model knows the latitude and longitude of Paris
        config=config,
        contents="What is the weather like in Paris?"
    )
    
    print("\n=== Full Response Structure ===")
    pp.pprint(response)

    print('/nLLM RESPONSE: ', response.text)

def main():
    # Test both tools
    # test_light_control()
    # test_weather() 
    test_function_calling_config()

if __name__ == "__main__":
    main()
