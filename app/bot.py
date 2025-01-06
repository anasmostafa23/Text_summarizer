import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
FLASK_API_URL = os.getenv('FLASK_API_URL')  # URL of your existing Flask app (e.g., "http://localhost:5000")

async def set_ngrok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the ngrok URL."""
    global ngrok_url
    if context.args:
        ngrok_url = context.args[0]
        await update.message.reply_text(f'Ngrok URL set to: {ngrok_url}')
    else:
        await update.message.reply_text('Please provide a valid ngrok URL.')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command, welcome the user."""
    await update.message.reply_text('Welcome to the Summarization Bot! Use /set_ngrok <url> to set the service URL.')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command, displays all available commands."""
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Welcome message and bot introduction\n"
        "/set_ngrok <url> - Set the ngrok URL for the summarization service\n"
        "/summarize <text> - Summarize the provided text\n"
        "/recharge <amount> - Recharge your balance with the specified amount\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Summarize the provided text."""
    user_id = update.message.from_user.id
    text = ' '.join(context.args)
    global ngrok_url

    if not text:
        await update.message.reply_text('Please provide text to summarize.')
        return

    if not ngrok_url:
        await update.message.reply_text('Ngrok URL not set. Use /set_ngrok <url> first.')
        return

    # Send a POST request to the Flask app's /submit_task endpoint
    response = requests.post(f"{FLASK_API_URL}/api/submit_task", json={
        "user_id": user_id,  # Simulate passing user data
        "text_to_summarize": text, 
        "ngrok_url": ngrok_url
    })

    if response.status_code == 200:
        data = response.json()
        summary = data.get('summary', 'No summary returned')
        new_balance = data.get('balance', 'unknown')
        await update.message.reply_text(f'Summary: {summary}\nRemaining Balance: {new_balance}')
    elif response.status_code == 400:
        error_message = response.json().get('error', 'Error processing request')
        await update.message.reply_text(f'Error: {error_message}')
    else:
        await update.message.reply_text('Error: Failed to process the task.')

async def recharge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recharge the user's balance."""
    amount = float(context.args[0]) if context.args else 0
    user_id = update.message.from_user.id

    # Send a request to Flask API to recharge balance
    response = requests.post(f"{FLASK_API_URL}/api/recharge", json={"user_id": user_id, "amount": amount})


    if response.status_code == 200:
        new_balance = response.json().get('balance')
        await update.message.reply_text(f'Balance updated. New balance: {new_balance}')
    else:
        await update.message.reply_text('Error: Failed to recharge.')

def main():
    # Initialize the bot and dispatcher
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('set_ngrok', set_ngrok))
    application.add_handler(CommandHandler('summarize', summarize))
    application.add_handler(CommandHandler('recharge', recharge))
    application.add_handler(CommandHandler('help', help))  # Added help command

    # Start polling for new messages
    application.run_polling()

if __name__ == '__main__':
    main()
