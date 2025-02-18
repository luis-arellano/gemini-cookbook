import os
from dotenv import load_dotenv
import google.generativeai as genai
from google import genai as genai_client
from google.cloud import aiplatform

def initialize_gemini():
    """Initialize Gemini with API key."""
    # Load environment variables from .env file
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)

#### OLD IMPLEMENTATION ###
# def generate_text(prompt):
#     """Generate text using Gemini model."""
#     model = genai.GenerativeModel('gemini-pro')
#     response = model.generate_content(prompt)
#     return response.text

def generate_content(prompt):
    """Generate text using Gemini model- new implementation."""
    client = genai_client.Client()
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text

def main():
    initialize_gemini()
    
    # Test prompt
    prompt = "Explain why Bali is popular with influencers."
    # response = generate_text(prompt)
    response = generate_content(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")

if __name__ == "__main__":
    main() 