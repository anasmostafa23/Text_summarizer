import os
import requests

def summarize_text(text):
    """Send text to the external summarization service and return the summary."""
    ngrok_url = os.getenv('NGROK_URL', input("Enter Ngrok URL: ")) 
    
    payload = {"text": text}
    response = requests.post(f"{ngrok_url}/summarize", json=payload)
    
    if response.status_code == 200:
        return response.json().get("summary", "No summary provided.")
    else:
        raise RuntimeError(f"Summarization failed: {response.status_code} - {response.text}")
