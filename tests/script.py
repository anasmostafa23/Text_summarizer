import os
import requests

ngrok_url = os.getenv('NGROK_URL', input("Enter Ngrok URL: ")) 


payload = {"text": "Sample text to summarize."}
response = requests.post(f"{ngrok_url}/summarize", json=payload)

if response.status_code == 200:
    print("Summary:", response.json()["summary"])
else:
    print("Failed to connect. Status code:", response.status_code)
    print("Error:", response.text)
