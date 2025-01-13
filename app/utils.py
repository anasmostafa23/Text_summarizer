import os , re
import requests

def sanitize_url(url):
        """Sanitize ngrok_url to remove whitespace and special characters."""
        sanitized_url = re.sub(r'[^\w:/.-]', '', url).strip()  # Allow only typical URL characters
        return sanitized_url

def summarize_text(text, ngrokUrl):
    """Send text to the external summarization service and return the summary."""

    
    
    payload = {"text": text}
    response = requests.post(f"{ngrokUrl}/summarize", json=payload)
    
    if response.status_code == 200:
        return response.json().get("summary", "No summary provided.")
    else:
        raise RuntimeError(f"Summarization failed: {response.status_code} - {response.text}")
    
    
