import os
from dotenv import load_dotenv
load_dotenv() 

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:////instance/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NGROK_URL = "https://crappie-amazed-blindly.ngrok-free.app"
    BOT_TOKEN = "7846685181:AAFy6eCasmnlVZOy1kXrrfMWIDV3-Je6fDA"
    FLASK_API_URL = "http://flask-app:5000" 


