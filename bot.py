# Entry point for the Telegram OTP bot
# Loads configuration from environment and starts the bot
from dotenv import load_dotenv
import os
import logging

load_dotenv()

from handlers import start_bot

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == '__main__':
    logging.info("Starting bot...")
    start_bot()
