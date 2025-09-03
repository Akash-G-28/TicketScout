import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class BotHandlers:
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 Hello! I'm your TicketScout bot.\n\n"
            "I can monitor BookMyShow for movie tickets and notify you when they're available."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📖 Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/status - Show current monitoring status\n"
            "/add_movie <url> - Add a movie URL to monitor\n"
            "/test - Send a test notification"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ Monitoring is running in the background.")

    async def add_movie_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args:
            url = context.args[0]
            # TODO: integrate with BookingMonitor to actually add
            await update.message.reply_text(f"🎬 Added movie URL to monitor:\n{url}")
        else:
            await update.message.reply_text("⚠️ Usage: /add_movie <bookmyshow_url>")
