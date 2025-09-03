import asyncio
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Bot

logger = logging.getLogger(__name__)

class BookingMonitor:
    def __init__(self, application, chat_id: str, interval: int = 60):
        """
        Monitors a BookMyShow movie page and notifies a Telegram chat
        when 'Interested' changes to 'Book'.

        :param application: PTB Application instance
        :param chat_id: Telegram chat ID to send notifications
        :param interval: Time between checks (in seconds)
        """
        self.application = application
        self.chat_id = chat_id
        self.interval = interval
        self.movie_urls = []  # list of movie URLs being tracked
        self.running = False

    def add_movie(self, url: str):
        """Add a movie URL to track."""
        if url not in self.movie_urls:
            self.movie_urls.append(url)
            logger.info(f"Added movie URL: {url}")

    async def check_movie(self, url: str):
        """Fetch the page and check if 'Book' button exists."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Example logic: adjust selectors as needed for BookMyShow
            button = soup.find("button")
            if button and "Book" in button.get_text():
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🎉 Tickets are available! Go book now: {url}"
                )
                logger.info(f"Booking available for {url}")
            else:
                logger.info(f"Still no booking for {url}")
        except Exception as e:
            logger.error(f"Error checking {url}: {e}")

    async def run(self):
        """Background loop that keeps checking movies."""
        self.running = True
        while self.running:
            if not self.movie_urls:
                await asyncio.sleep(self.interval)
                continue

            for url in self.movie_urls:
                await self.check_movie(url)

            await asyncio.sleep(self.interval)

    def start_monitoring(self):
        """Schedules the monitor task inside PTB's event loop."""
        self.application.job_queue.run_repeating(
            lambda _: asyncio.create_task(self.run()),
            interval=self.interval,
            first=0
        )
