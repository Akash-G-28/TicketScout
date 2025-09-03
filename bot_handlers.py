"""
Bot handlers module containing all Telegram bot command and message handlers.
Provides basic chat functionality including commands and keyword detection.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler
from scraper import BookMyShowScraper

logger = logging.getLogger(__name__)
ApplicationBuilder, CommandHandlerclass BotHandlers:
    """
    Class containing all bot handler methods for Telegram commands and messages.
    """
    
    def __init__(self):
        """Initialize the bot handlers."""
        self.keywords = {
            'hello': ['hello', 'hi', 'hey', 'greetings'],
            'bye': ['bye', 'goodbye', 'see you', 'farewell']
        }
        # Initialize scraper for testing commands
        self.scraper = BookMyShowScraper()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /start command - sends welcome message to user.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        welcome_message = (
            "🎬 Welcome to BookMyShow Movie Monitor Bot! 🎬\n\n"
            "I can help you monitor movie ticket availability on BookMyShow.\n\n"
            "📋 Available commands:\n"
            "/help - Show all available commands\n"
            "/status - Check monitoring status\n"
            "/add_movie - Add a movie URL to monitor\n\n"
            "💬 You can also just chat with me - I'll respond to your messages!\n\n"
            "🔔 I'll automatically notify you when movie tickets become available."
        )
        
        await update.message.reply_text(welcome_message)
        logger.info(f"Sent welcome message to user {update.effective_user.id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /help command - shows list of available commands.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        help_message = (
            "📋 Available Commands:\n\n"
            "/start - Welcome message and bot introduction\n"
            "/help - Show this help message\n"
            "/status - Check current monitoring status\n"
            "/add_movie - Add a BookMyShow movie URL to monitor\n"
            "/test - Test any BookMyShow URL for ticket availability\n\n"
            "💬 Chat Features:\n"
            "• Send me any text message and I'll echo it back\n"
            "• I can detect keywords like 'hello' and 'bye'\n\n"
            "🎬 Monitoring Features:\n"
            "• Automatic monitoring of BookMyShow for ticket availability\n"
            "• Checks every 5 minutes for 'Book tickets' button\n"
            "• Instant notifications when tickets become available\n\n"
            "⚙️ Technical Info:\n"
            "• Running continuously with long polling\n"
            "• Handles rate limiting and errors gracefully\n"
            "• Easy to add multiple movie URLs for monitoring"
        )
        
        await update.message.reply_text(help_message)
        logger.info(f"Sent help message to user {update.effective_user.id}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /status command - shows current monitoring status.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        status_message = (
            "📊 Bot Status:\n\n"
            "🤖 Bot: ✅ Online and running\n"
            "🔄 Monitoring: ✅ Active (checks every 5 minutes)\n"
            "🎬 Target: BookMyShow movie pages\n"
            "🔍 Looking for: 'Book tickets' availability\n\n"
            "💡 To add a movie URL for monitoring, use /add_movie command\n"
            "📱 Chat with me anytime - I'm always listening!"
        )
        
        await update.message.reply_text(status_message)
        logger.info(f"Sent status message to user {update.effective_user.id}")
    
    async def add_movie_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /add_movie command - provides instructions for adding movie URLs.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        add_movie_message = (
            "🎬 Add Movie URL for Monitoring\n\n"
            "To add a BookMyShow movie URL for monitoring:\n\n"
            "1️⃣ Go to BookMyShow website\n"
            "2️⃣ Find the movie you want to monitor\n"
            "3️⃣ Copy the movie page URL\n"
            "4️⃣ Send it to me as a regular message\n\n"
            "📝 Example URL format:\n"
            "https://in.bookmyshow.com/movie-name-city/ET00123456\n\n"
            "⚠️ Note: Currently monitoring is configured in the code.\n"
            "For now, I'm monitoring pre-configured URLs.\n"
            "Future versions will support dynamic URL addition!"
        )
        
        await update.message.reply_text(add_movie_message)
        logger.info(f"Sent add movie instructions to user {update.effective_user.id}")
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the /test command - test a BookMyShow URL for ticket availability.
        Usage: /test https://in.bookmyshow.com/movie-url
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        user_id = update.effective_user.id
        
        # Check if URL was provided
        if not context.args or len(context.args) == 0:
            help_message = (
                "🧪 Test Movie URL\n\n"
                "Usage: `/test <BookMyShow URL>`\n\n"
                "📝 Example:\n"
                "`/test https://in.bookmyshow.com/movies/mumbai/movie-name/ET00123456`\n\n"
                "This will immediately check if the movie page has booking available."
            )
            await update.message.reply_text(help_message, parse_mode='Markdown')
            logger.info(f"Sent test command help to user {user_id}")
            return
        
        # Get the URL from command arguments
        test_url = ' '.join(context.args)
        
        # Validate URL format
        if 'bookmyshow.com' not in test_url.lower():
            error_message = (
                "❌ Invalid URL\n\n"
                "Please provide a valid BookMyShow URL.\n"
                "Example: `https://in.bookmyshow.com/movies/mumbai/movie-name/ET00123456`"
            )
            await update.message.reply_text(error_message, parse_mode='Markdown')
            logger.info(f"Invalid test URL from user {user_id}: {test_url}")
            return
        
        # Send "checking" message
        checking_message = await update.message.reply_text(
            f"🔍 Testing URL...\n\n"
            f"📱 Checking: {test_url}\n\n"
            f"⏳ Please wait while I check for ticket availability..."
        )
        
        try:
            # Use scraper to check the URL
            logger.info(f"Testing URL from user {user_id}: {test_url}")
            result = self.scraper.check_ticket_availability(test_url)
            
            # Prepare result message
            movie_title = result.get('title', 'Unknown Movie')
            available = result.get('available', False)
            status = result.get('status', 'Unknown status')
            error = result.get('error', None)
            
            if error:
                result_message = (
                    f"❌ **Test Result - Error**\n\n"
                    f"🎬 Movie: {movie_title}\n"
                    f"🔗 URL: {test_url}\n\n"
                    f"⚠️ Error: {error}\n\n"
                    f"💡 This might be due to:\n"
                    f"• Website blocking automated requests\n"
                    f"• Page not found or moved\n"
                    f"• Network connectivity issues"
                )
            elif available:
                result_message = (
                    f"✅ **Test Result - TICKETS AVAILABLE!**\n\n"
                    f"🎬 Movie: {movie_title}\n"
                    f"🔗 URL: {test_url}\n\n"
                    f"🎟️ Status: {status}\n\n"
                    f"🎉 Great news! Booking appears to be open!"
                )
            else:
                result_message = (
                    f"❌ **Test Result - No Tickets Found**\n\n"
                    f"🎬 Movie: {movie_title}\n"
                    f"🔗 URL: {test_url}\n\n"
                    f"📋 Status: {status}\n\n"
                    f"⏰ Booking may not have started yet or tickets are sold out."
                )
            
            # Edit the checking message with results
            await checking_message.edit_text(result_message, parse_mode='Markdown')
            logger.info(f"Sent test result to user {user_id}: available={available}")
            
        except Exception as e:
            error_message = (
                f"❌ **Test Failed**\n\n"
                f"🔗 URL: {test_url}\n\n"
                f"⚠️ Error: {str(e)}\n\n"
                f"Please try again or check if the URL is correct."
            )
            await checking_message.edit_text(error_message, parse_mode='Markdown')
            logger.error(f"Test command error for user {user_id}: {e}")
    
    async def echo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle text messages - echo back and detect keywords.
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        user_message = update.message.text.lower()
        user_id = update.effective_user.id
        
        # Check for greeting keywords
        if any(keyword in user_message for keyword in self.keywords['hello']):
            response = f"Hello there! 👋 How can I help you with movie ticket monitoring today?"
            logger.info(f"Detected greeting from user {user_id}")
        
        # Check for farewell keywords
        elif any(keyword in user_message for keyword in self.keywords['bye']):
            response = f"Goodbye! 👋 I'll keep monitoring for movie tickets. See you later!"
            logger.info(f"Detected farewell from user {user_id}")
        
        # Check if message looks like a BookMyShow URL
        elif 'bookmyshow.com' in user_message:
            response = (
                "🎬 I see you've shared a BookMyShow URL!\n\n"
                "📝 URL received: " + update.message.text + "\n\n"
                "⚠️ Note: Dynamic URL addition is not yet implemented.\n"
                "Currently monitoring pre-configured URLs.\n"
                "I'll keep this URL for future reference!"
            )
            logger.info(f"BookMyShow URL received from user {user_id}: {update.message.text}")
        
        # Default echo response
        else:
            response = f"You said: {update.message.text}\n\nI'm listening! 🎧"
            logger.info(f"Echoed message from user {user_id}")
        
        await update.message.reply_text(response)
