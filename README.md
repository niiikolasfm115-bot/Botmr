# Cleaned README

This repository contains a cleaned, modularized Telegram OTP bot based on the original script.

Main files created:
- bot.py        Entry point
- handlers.py   Telegram handlers and bot wiring
- ivasms.py     Minimal client for iVasms (cookies/login/fetch)
- db.py         SQLite DB helpers
- utils.py      Small helpers and constants

Security and notes:
- Secrets have been removed from the repository. Use a .env file (or environment variables) to configure BOT_TOKEN, IVASMS_USERNAME, IVASMS_PASSWORD.
- Review and rotate any tokens that were previously committed publicly.

How to run
1. Copy .env.example to .env and fill values.
2. Create a virtualenv and install dependencies:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
3. Run the bot:
   python bot.py

License
MIT (see LICENSE)
