TicketScout
A lightweight Python script that checks if movie tickets on BookMyShow are available and notifies you via Telegram.

What it does
Visits one or more BookMyShow movie pages.
Detects when the “Book tickets” option appears.
Sends you a Telegram message immediately, reminding you to grab tickets.
Designed for easy deployment via GitHub Actions on a Chromebook or any setup.

Repository Structure:

TicketScout/
├─ bot_handlers.py         # (If applicable) command logic for Telegram interaction
├─ main.py                 # Main entry — orchestrates scraping + messaging
├─ monitor.py              # Scrapes BookMyShow pages for booking status
├─ scraper.py              # Helper functions for HTTP fetching & HTML parsing
├─ pyproject.toml          # Python dependency configuration
├─ replit.md               # Notes from your Replit setup process
├─ .github/workflows/
│   └─ bot.yml             # GitHub Actions workflow to run every interval
└─ README.md               # (This file)

------------------------------------------------------------------------
------------------------------------------------------------------------

Getting Started
1. Set Up Your Telegram Bot
Talk to @BotFather in Telegram and use /newbot to create your bot.
Copy and keep the API token (a string like 123456789:ABC...).

2. Get Your Chat ID
Send any message to your bot.
Open this URL in your browser (replace <token>):
https://api.telegram.org/bot<token>/getUpdates
In the response JSON, locate your chat ID. You’ll need it shortly.

3. Configure GitHub Secrets
In your GitHub repo:
Go to Settings → Secrets → Actions.
Add:
BOT_TOKEN → your Telegram bot token.
CHAT_ID → your personal Telegram chat ID.

4. GitHub Actions Setup
You’ve already got a workflow (.github/workflows/bot.yml) that:
Runs every 10 minutes.
Checks movie availability.
Sends you alerts via the Telegram bot when tickets open.
So once everything’s pushed, GitHub takes care of the rest.

Sample Message
When tickets are available, you'll get a message like:
⏰ Check at 2025-09-03 15:40:27
✅ TICKETS AVAILABLE for Demon Slayer 🎟️
https://in.bookmyshow.com/…
❌ No tickets yet for Param Sundari ⏳

Customize It
Add more movies
Modify the MOVIES dictionary to include movie names and URLs.
Adjust the check interval
Edit the cron schedule in bot.yml. For example:
on:
  schedule:
    - cron: "*/5 * * * *"  # every 5 minutes

Add logging or alerts
You can tweak the messaging format or extend the logic for richer output.

License & Contributions
Feel free to reuse or adapt this for your own projects. If you build new features or improve it, I’d love to see what you create!
