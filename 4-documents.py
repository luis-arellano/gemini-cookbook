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

    prompt = "Summarize this document"

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
    

# test_url_document() # url document
test_local_document() # local document