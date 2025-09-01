# Overview

A Telegram bot that monitors BookMyShow for movie ticket availability. The bot provides conversational chat capabilities and runs continuous background monitoring to notify users when tickets become available for specified movies. Users can interact with the bot through commands and receive automated notifications when booking status changes.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Python-telegram-bot**: Core framework for handling Telegram API interactions
- **Asynchronous handlers**: All bot commands and message handlers use async/await pattern
- **Modular design**: Separated concerns with dedicated modules for handlers, monitoring, and scraping

## Command System
- **BotHandlers class**: Centralized command handling with methods for start, help, status, and add_movie commands
- **Keyword detection**: Basic conversational AI with predefined keyword matching for greetings and farewells
- **Environment-based configuration**: Bot token and chat ID configured through environment variables

## Background Monitoring
- **BookingMonitor class**: Continuous monitoring system running in separate thread
- **Configurable intervals**: Default 5-minute check intervals with rate limiting
- **State tracking**: Maintains previous states to detect availability changes
- **Statistics tracking**: Monitors performance metrics like checks performed and notifications sent

## Web Scraping Architecture
- **BookMyShowScraper class**: Handles HTTP requests to BookMyShow with session management
- **Rate limiting**: Built-in delays between requests to avoid overwhelming target servers
- **Browser simulation**: Uses realistic headers to mimic legitimate browser traffic
- **BeautifulSoup parsing**: HTML parsing to detect ticket availability indicators

## Threading Model
- **Main thread**: Handles Telegram bot message processing and command execution
- **Background thread**: Runs continuous monitoring without blocking user interactions
- **Thread-safe communication**: Uses Telegram bot instance for cross-thread notifications

## Error Handling
- **Comprehensive logging**: Structured logging throughout all modules for debugging and monitoring
- **Graceful degradation**: Bot continues operating even if monitoring encounters errors
- **Environment validation**: Checks for required configuration before starting services

## Data Management
- **In-memory storage**: URL monitoring list and state tracking stored in memory
- **Dynamic URL management**: Support for adding/removing monitored URLs during runtime
- **No persistent storage**: Simple stateless design suitable for single-session monitoring

# External Dependencies

## Core Dependencies
- **python-telegram-bot**: Official Telegram Bot API wrapper for Python
- **requests**: HTTP library for web scraping BookMyShow pages
- **BeautifulSoup4**: HTML parsing library for extracting ticket availability data

## Target Service
- **BookMyShow**: Primary target website for movie ticket monitoring
- **Rate limiting compliance**: Designed to respect server resources with built-in delays

## Configuration Requirements
- **TELEGRAM_BOT_TOKEN**: Environment variable for bot authentication
- **TELEGRAM_CHAT_ID**: Environment variable for notification target (optional)

## Runtime Environment
- **Python 3.7+**: Async/await support required for telegram-bot framework
- **Threading support**: Background monitoring requires multi-threading capabilities