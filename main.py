#!/usr/bin/env python3
"""
Main entry point for the Telegram bot that monitors BookMyShow for movie ticket availability.
This bot provides basic chat functionality and continuous monitoring of movie booking status.
"""

import os
import logging
import threading
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from bot_handlers import BotHandlers
from monitor import BookingMonitor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to initialize and run the Telegram bot with BookMyShow monitoring.
    """
    # Get bot token from environment variables (Replit secrets)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is polling...")
    app.run_polling()
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required!")
        return

    # Get chat ID for notifications from environment variables
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID not set. Notifications will not be sent.")

    try:
        # Create the Application
        application = Application.builder().token(bot_token).build()
        
        # Initialize bot handlers
        bot_handlers = BotHandlers()
        
        # Initialize booking monitor
        booking_monitor = BookingMonitor(application.bot, chat_id)
        
        # Register command handlers
        application.add_handler(CommandHandler("start", bot_handlers.start_command))
        application.add_handler(CommandHandler("help", bot_handlers.help_command))
        application.add_handler(CommandHandler("status", bot_handlers.status_command))
        application.add_handler(CommandHandler("add_movie", bot_handlers.add_movie_command))
        application.add_handler(CommandHandler("test", bot_handlers.test_command))
        
        # Register message handler for text messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.echo_message))
        
        # Start the booking monitor in a separate thread
        monitor_thread = threading.Thread(target=booking_monitor.start_monitoring, daemon=True)
        monitor_thread.start()
        logger.info("Booking monitor started in background thread")
        
        # Start the bot with long polling
        logger.info("Starting Telegram bot...")
        application.run_polling(allowed_updates=["message"])
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    main()
