import json
import os

import requests
from google import genai
from google.genai import types

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pprint import pprint, PrettyPrinter

import httpx
import pathlib

from googleapiclient.discovery import build
from google.oauth2 import service_account
import requests


pp = PrettyPrinter(indent=2, width=80)


# Documentation
"""
https://ai.google.dev/gemini-api/docs/document-processing?lang=python
"""

# Configure Gemini Pro API
def initialize_gemini():
    """Initialize Gemini with API key."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)

def test_url_document():
    doc_url = "https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"  # Replace with the actual URL of your PDF

    # Retrieve and encode the PDF byte
    doc_data = httpx.get(doc_url).content

    prompt = "Summarize this document."

    client = initialize_gemini()
    response = client.models.generate_content(
        model='gemini-1.5-pro',
          contents=[
            genai.types.Part.from_bytes(
                data=doc_data,
                mime_type='application/pdf',
            ),
            prompt
        ]
    )
    print(response.text)
    
def test_local_document():

    # Retrieve and encode the PDF byte
    # filepath = pathlib.Path('/Users/larellano/Desktop/Luis Arellano - Applied AI.pdf')
    filepath = pathlib.Path('/Users/larellano/Desktop/test-table.pdf')

    prompt = "Create a an Markdown version of this document"

    client = initialize_gemini()
    response = client.models.generate_content(
        model='gemini-1.5-pro',
          contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            ),
            prompt
        ]
    )
    print(response.text)
    
    
def get_drive_service():
    """Get or create Google Drive API service."""
    # Path to your service account key file
    SERVICE_ACCOUNT_FILE = "service-account.json"
    
    # Check if file exists
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found at: {SERVICE_ACCOUNT_FILE}")
    
    # Print file path and basic info (without sensitive data)
    print(f"Loading service account from: {os.path.abspath(SERVICE_ACCOUNT_FILE)}")
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            service_account_info = json.load(f)
            print(f"Service account email: {service_account_info.get('client_email', 'Not found')}")
            print(f"Project ID: {service_account_info.get('project_id', 'Not found')}")
    except json.JSONDecodeError:
        raise ValueError("Service account file is not valid JSON")
    except Exception as e:
        raise Exception(f"Error reading service account file: {str(e)}")

    # Define scopes
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/presentations.readonly"]

    # Authenticate and build the service
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build("drive", "v3", credentials=creds)
    return drive_service

def download_google_slides_as_pdf(presentation_id, output_file):
    """
    Downloads a Google Slides presentation as a PDF.
    
    :param presentation_id: The ID of the Google Slides presentation
    :param output_file: The output file path for the PDF
    """
    drive_service = get_drive_service()
    try:
        request = drive_service.files().export_media(
            fileId=presentation_id,
            mimeType='application/pdf'
        )
        
        data = request.execute()
        
        with open(output_file, 'wb') as f:
            f.write(data)
        print(f"PDF downloaded successfully: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        # Print more detailed error information
        import traceback
        traceback.print_exc()
    
    
# --------------------------------------------------------------
# First create a Google Service Account,
# Share access with the service account email to the Google Slides presentation.
# Enable Drive API and Slides API for the project.

# NOTE: you will need a service-account.json file to run this code.
# you can download it from the Google Cloud Console.
# --------------------------------------------------------------
    
def test_google_slides():
    """Download Google Slides as PDF and analyze with Gemini."""
    # First download the slides
    presentation_id = '1C7X34qE3cconG9TgyRUtzv3rtWFhoa3Ho6fMwnSfXjA'
    output_pdf = 'test-slides.pdf'
    download_google_slides_as_pdf(presentation_id, output_pdf)
    
    # Initialize Gemini client
    client = initialize_gemini()
    
    # Read the PDF file
    pdf_path = pathlib.Path(output_pdf)
    
    # Prepare the prompt for slide-by-slide analysis
    prompt = """
    Create a summary of every slide in this document.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=[
                types.Part.from_bytes(
                    data=pdf_path.read_bytes(),
                    mime_type='application/pdf',
                ),
                prompt
            ]
        )
        
        print("\nSlide-by-Slide Analysis:")
        print("------------------------")
        print(response.text)
        
    except Exception as e:
        print(f"Error analyzing PDF with Gemini: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Optionally clean up the PDF file
        # os.remove(output_pdf)
        pass


# test_url_document() # url document
# test_local_document() # local document
test_google_slides()