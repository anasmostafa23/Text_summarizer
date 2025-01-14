import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from config import Config

load_dotenv()  # Load environment variables from .env
BOT_TOKEN = Config.BOT_TOKEN
FLASK_API_URL = Config.FLASK_API_URL  # URL of your existing Flask app (e.g., "http://localhost:5000")
ngrok_url = Config.NGROK_URL


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command, welcome the user."""
    await update.message.reply_text('Welcome to the Summarization Bot! Use /help to see commands!')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command, displays all available commands."""
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Welcome message and bot introduction\n"
        "/summarize <text> - Summarize the provided text\n"
        "/recharge <amount> - Recharge your balance with the specified amount or leave empty to know balance.\n"
        "/help - Show this help message\n/latest_result to see the latest submission result"
    )
    await update.message.reply_text(help_text)

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Summarize the provided text."""
    user_id = update.message.from_user.id
    text = ' '.join(context.args)
    ngrok_url = Config.NGROK_URL

    if not text:
        await update.message.reply_text('Please provide text to summarize.')
        return

    if len(text) > 2500:
        await update.message.reply_text(f'The provided text is too long. Please keep it under 2500 English characters.')
        return

    

    response = requests.post(f"{FLASK_API_URL}/api/submit_task", json={
        "user_id": user_id,
        "text_to_summarize": text,
        "ngrok_url": ngrok_url
    })

    if response.status_code == 200:
        await update.message.reply_text('Task submitted successfully! Check your history in a few minutes use /latest_result !')
    elif response.status_code == 400:
        error_message = response.json().get('error', 'Error processing request')
        await update.message.reply_text(f'Error: {error_message}')
    else:
        await update.message.reply_text('Error: Failed to process the task.')

async def recharge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recharge the user's balance or show current balance if no amount is provided."""
    user_id = update.message.from_user.id

    if context.args:
        try:
            amount = float(context.args[0])
        except ValueError:
            await update.message.reply_text('Invalid amount. Please enter a valid number.')
            return

        # Send a request to Flask API to recharge balance
        response = requests.post(f"{FLASK_API_URL}/api/recharge", json={"user_id": user_id, "amount": amount})

        if response.status_code == 200:
            new_balance = response.json().get('balance', 'unknown')
            await update.message.reply_text(f'Balance updated. New balance: {new_balance}')
        else:
            await update.message.reply_text('Error: Failed to recharge.')
    else:
        # Fetch the current balance if no amount is provided
        response = requests.get(f"{FLASK_API_URL}/api/balance", json={"user_id": user_id})

        if response.status_code == 200:
            balance = response.json().get('balance', 'unknown')
            await update.message.reply_text(f'Your current balance is: {balance}')
        else:
            await update.message.reply_text('Error: Failed to retrieve balance.')

async def latest_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and display the latest task result."""
    user_id = update.message.from_user.id

    response = requests.get(f"{FLASK_API_URL}/api/latest_result", json={"user_id": user_id})

    if response.status_code == 200:
        data = response.json()
        summary = data.get('summary', 'No summary available')
        prompt = data.get('prompt', 'No prompt available')
        await update.message.reply_text(f"Prompt: {prompt}\nSummary: {summary}")
    elif response.status_code == 404:
        await update.message.reply_text('No recent tasks found.')
    else:
        await update.message.reply_text('Error: Failed to fetch the latest result.')


def main():
    # Initialize the bot and dispatcher
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('summarize', summarize))
    application.add_handler(CommandHandler('recharge', recharge))
    application.add_handler(CommandHandler('help', help))  # Added help command
    application.add_handler(CommandHandler('latest_result', latest_result))

    # Start polling for new messages
    application.run_polling()
    print("bot is running...")

if __name__ == '__main__':
    main()
    
