import time
import logging
from typing import List, Dict, Optional
from telegram.ext import Application
from scraper import BookMyShowScraper

logger = logging.getLogger(__name__)

class BookingMonitor:
    def __init__(self, application: Application, chat_id: Optional[str] = None):
        self.application = application
        self.chat_id = chat_id
        self.scraper = BookMyShowScraper()
        self.check_interval = 300  # 5 minutes
        self.monitored_urls = [
            "https://in.bookmyshow.com/movies/mumbai/demon-slayer-kimetsu-no-yaiba-the-movie-infinity-castle-japanese/ET00436673",
            "https://in.bookmyshow.com/movies/mumbai/param-sundari-hindi/ET00426409",
        ]
        self.previous_states = {}

    async def send_notification(self, message: str) -> None:
        if not self.chat_id:
            logger.warning("No chat ID configured for notifications")
            return
        try:
            await self.application.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info(f"Notification sent: {message[:50]}...")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    async def check_all_urls(self) -> List[Dict]:
        results = []
        for url in self.monitored_urls:
            try:
                result = self.scraper.check_ticket_availability(url)
                results.append(result)

                prev = self.previous_states.get(url, {})
                if result.get("available") and not prev.get("available"):
                    # Schedule async notification on PTB loop
                    self.application.create_task(self.send_availability_notification(result))

                self.previous_states[url] = result

            except Exception as e:
                logger.error(f"Error checking {url}: {e}")
                results.append({
                    "url": url,
                    "available": False,
                    "status": "Check failed",
                    "error": str(e)
                })
        return results

    async def send_availability_notification(self, result: Dict) -> None:
        movie = result.get("title", "Unknown Movie")
        url = result.get("url", "")
        status = result.get("status", "")

        msg = (
            f"🎬 TICKETS AVAILABLE! 🎬\n\n"
            f"🎭 Movie: {movie}\n"
            f"✅ Status: {status}\n"
            f"🔗 URL: {url}\n\n"
            f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await self.send_notification(msg)

    def start_monitoring(self) -> None:
        """Add monitoring job to PTB’s job queue."""
        self.application.job_queue.run_repeating(
            lambda _: self.application.create_task(self.check_all_urls()),
            interval=self.check_interval,
            first=5
        )
        logger.info("Booking monitor scheduled in job queue")
