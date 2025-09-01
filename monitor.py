"""
Monitoring module for continuous BookMyShow ticket availability checking.
Runs in background thread and sends notifications when tickets become available.
"""

import time
import logging
import threading
import asyncio
from typing import List, Dict, Optional
from telegram import Bot
from scraper import BookMyShowScraper

logger = logging.getLogger(__name__)

class BookingMonitor:
    """
    Background monitor that continuously checks BookMyShow for ticket availability.
    Sends Telegram notifications when tickets become available.
    """
    
    def __init__(self, bot: Bot, chat_id: Optional[str] = None):
        """
        Initialize the booking monitor.
        
        Args:
            bot: Telegram bot instance for sending notifications
            chat_id: Chat ID to send notifications to
        """
        self.bot = bot
        self.chat_id = chat_id
        self.scraper = BookMyShowScraper()
        self.is_running = False
        self.check_interval = 300  # 5 minutes in seconds
        
        # List of URLs to monitor - can be expanded
        self.monitored_urls = [
            # Primary URL to monitor for booking availability
            "https://in.bookmyshow.com/movies/mumbai/demon-slayer-kimetsu-no-yaiba-the-movie-infinity-castle-japanese/ET00436673",
            # Reference URL where booking is already live (for testing detection)
            "https://in.bookmyshow.com/movies/mumbai/param-sundari-hindi/ET00426409",
        ]
        
        # Track previous states to detect changes
        self.previous_states = {}
        
        # Statistics
        self.checks_performed = 0
        self.notifications_sent = 0
        self.start_time = None
    
    def add_url(self, url: str) -> bool:
        """
        Add a new URL to monitor.
        
        Args:
            url: BookMyShow URL to add to monitoring
            
        Returns:
            True if URL was added successfully
        """
        try:
            if url not in self.monitored_urls:
                self.monitored_urls.append(url)
                logger.info(f"Added URL to monitoring: {url}")
                return True
            else:
                logger.info(f"URL already being monitored: {url}")
                return False
        except Exception as e:
            logger.error(f"Error adding URL {url}: {e}")
            return False
    
    def remove_url(self, url: str) -> bool:
        """
        Remove a URL from monitoring.
        
        Args:
            url: URL to remove from monitoring
            
        Returns:
            True if URL was removed successfully
        """
        try:
            if url in self.monitored_urls:
                self.monitored_urls.remove(url)
                if url in self.previous_states:
                    del self.previous_states[url]
                logger.info(f"Removed URL from monitoring: {url}")
                return True
            else:
                logger.info(f"URL not found in monitoring list: {url}")
                return False
        except Exception as e:
            logger.error(f"Error removing URL {url}: {e}")
            return False
    
    async def send_notification(self, message: str) -> None:
        """
        Send notification message to configured chat.
        
        Args:
            message: Message to send
        """
        if not self.chat_id:
            logger.warning("No chat ID configured for notifications")
            return
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            self.notifications_sent += 1
            logger.info(f"Notification sent: {message[:50]}...")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def check_all_urls(self) -> List[Dict]:
        """
        Check all monitored URLs for ticket availability.
        
        Returns:
            List of check results
        """
        results = []
        
        for url in self.monitored_urls:
            try:
                logger.info(f"Checking URL: {url}")
                result = self.scraper.check_ticket_availability(url)
                results.append(result)
                
                # Check if availability status changed
                previous_state = self.previous_states.get(url, {})
                current_available = result.get('available', False)
                previous_available = previous_state.get('available', False)
                
                # If tickets became available (changed from False to True)
                if current_available and not previous_available:
                    asyncio.create_task(self.send_availability_notification(result))
                
                # Update previous state
                self.previous_states[url] = result
                
            except Exception as e:
                logger.error(f"Error checking URL {url}: {e}")
                results.append({
                    'url': url,
                    'available': False,
                    'status': 'Check failed',
                    'error': str(e)
                })
        
        self.checks_performed += 1
        return results
    
    async def send_availability_notification(self, result: Dict) -> None:
        """
        Send notification when tickets become available.
        
        Args:
            result: Check result dictionary
        """
        movie_title = result.get('title', 'Unknown Movie')
        url = result.get('url', '')
        status = result.get('status', '')
        
        notification_message = (
            f"🎬 TICKETS AVAILABLE! 🎬\n\n"
            f"🎭 Movie: {movie_title}\n"
            f"✅ Status: {status}\n"
            f"🔗 URL: {url}\n\n"
            f"🏃‍♂️ Hurry up and book your tickets now!\n"
            f"⏰ Notification sent at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await self.send_notification(notification_message)
        logger.info(f"Sent availability notification for {movie_title}")
    
    def get_monitoring_stats(self) -> Dict:
        """
        Get monitoring statistics.
        
        Returns:
            Dictionary with monitoring statistics
        """
        uptime = 0
        if self.start_time:
            uptime = time.time() - self.start_time
        
        return {
            'is_running': self.is_running,
            'urls_monitored': len(self.monitored_urls),
            'checks_performed': self.checks_performed,
            'notifications_sent': self.notifications_sent,
            'uptime_seconds': uptime,
            'check_interval': self.check_interval
        }
    
    def start_monitoring(self) -> None:
        """
        Start the continuous monitoring loop.
        This method runs in a background thread.
        """
        import asyncio
        
        self.is_running = True
        self.start_time = time.time()
        logger.info("Starting BookMyShow monitoring...")
        
        # Create event loop for async operations in thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.is_running:
                try:
                    logger.info("Performing monitoring check...")
                    
                    # Check all URLs
                    results = self.check_all_urls()
                    
                    # Log summary
                    available_count = sum(1 for r in results if r.get('available', False))
                    logger.info(f"Check completed: {available_count}/{len(results)} movies have tickets available")
                    
                    # Wait for next check
                    logger.info(f"Waiting {self.check_interval} seconds until next check...")
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    # Wait before retrying
                    time.sleep(60)  # Wait 1 minute before retrying
                    
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
        finally:
            self.is_running = False
            logger.info("Monitoring stopped")
            loop.close()
    
    def stop_monitoring(self) -> None:
        """
        Stop the monitoring loop.
        """
        self.is_running = False
        logger.info("Stopping monitoring...")
