import os
from dotenv import load_dotenv
load_dotenv() 

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NGROK_URL = os.getenv('ngrok_url') 
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    FLASK_API_URL = os.getenv('FLASK_API_URL') 


