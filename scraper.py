"""
Web scraper module for monitoring BookMyShow movie ticket availability.
Uses requests and BeautifulSoup to check for 'Book tickets' button availability.
"""

import requests
import logging
import time
from bs4 import BeautifulSoup
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class BookMyShowScraper:
    """
    Web scraper class for monitoring BookMyShow movie pages for ticket availability.
    """
    
    def __init__(self):
        """Initialize the scraper with session and headers."""
        self.session = requests.Session()
        
        # Set headers to mimic a real browser - updated to latest Chrome
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'identity',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(self.headers)
        
        # Rate limiting - minimum time between requests
        self.last_request_time = 0
        self.min_request_interval = 2  # seconds
    
    def _rate_limit(self) -> None:
        """
        Implement rate limiting to avoid overwhelming the server.
        Ensures minimum interval between requests.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def check_ticket_availability(self, url: str) -> Dict[str, any]:
        """
        Check if movie tickets are available for booking on the given URL.
        
        Args:
            url: BookMyShow movie page URL to check
            
        Returns:
            Dictionary containing:
            - available: Boolean indicating if tickets are available
            - status: String status message
            - error: Error message if any
            - title: Movie title if found
        """
        result = {
            'available': False,
            'status': 'Unknown',
            'error': None,
            'title': 'Unknown Movie',
            'url': url
        }
        
        try:
            # Apply rate limiting
            self._rate_limit()
            
            logger.info(f"Checking ticket availability for: {url}")
            
            # Make request to the movie page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Handle encoding properly for compressed content
            response.encoding = 'utf-8'
            
            # Parse HTML content with proper encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract movie title
            title_selectors = [
                'h1[data-testid="movie-title"]',
                'h1.movie-title',
                '.movie-name h1',
                'h1',
                '.title'
            ]
            
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    result['title'] = title_element.get_text(strip=True)
                    break
            
            # Look for booking availability indicators
            booking_indicators = [
                'Book tickets',
                'Book now',
                'Buy tickets',
                'Purchase tickets',
                'Select seats',
                'Choose seats'
            ]
            
            page_text = soup.get_text().lower()
            
            # Check for booking button or text
            for indicator in booking_indicators:
                if indicator.lower() in page_text:
                    result['available'] = True
                    result['status'] = f"Tickets available - found '{indicator}'"
                    logger.info(f"Tickets available for {result['title']}: {indicator}")
                    return result
            
            # Check for specific button elements
            booking_buttons = soup.find_all(['button', 'a'])
            for button in booking_buttons:
                button_text = button.get_text(strip=True) if button else ''
                if button_text and any(indicator.lower() in button_text.lower() for indicator in booking_indicators):
                    result['available'] = True
                    result['status'] = f"Booking button found: {button_text}"
                    logger.info(f"Booking button found for {result['title']}: {button_text}")
                    return result
            
            
            # Check for sold out or unavailable indicators
            unavailable_indicators = [
                'sold out',
                'not available',
                'coming soon',
                'advance booking not started',
                'no shows available'
            ]
            
            for indicator in unavailable_indicators:
                if indicator.lower() in page_text:
                    result['status'] = f"Not available - {indicator}"
                    logger.info(f"Tickets not available for {result['title']}: {indicator}")
                    return result
            
            # Default case - no clear indicators found
            result['status'] = "No clear booking indicators found"
            logger.info(f"No clear booking status for {result['title']}")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            result['error'] = error_msg
            result['status'] = "Request failed"
            logger.error(f"Request error for {url}: {e}")
            
        except Exception as e:
            error_msg = f"Scraping error: {str(e)}"
            result['error'] = error_msg
            result['status'] = "Scraping failed"
            logger.error(f"Scraping error for {url}: {e}")
        
        return result
    
    def get_movie_info(self, url: str) -> Optional[Dict[str, str]]:
        """
        Extract basic movie information from BookMyShow page.
        
        Args:
            url: BookMyShow movie page URL
            
        Returns:
            Dictionary with movie information or None if failed
        """
        try:
            self._rate_limit()
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            info = {}
            
            # Extract title
            title_element = soup.select_one('h1[data-testid="movie-title"], h1.movie-title, h1')
            if title_element:
                info['title'] = title_element.get_text(strip=True)
            
            # Extract genre
            genre_element = soup.select_one('.genre, .movie-genre')
            if genre_element:
                info['genre'] = genre_element.get_text(strip=True)
            
            # Extract rating
            rating_element = soup.select_one('.rating, .movie-rating')
            if rating_element:
                info['rating'] = rating_element.get_text(strip=True)
            
            logger.info(f"Extracted movie info: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Error extracting movie info from {url}: {e}")
            return None
