import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Main configuration class"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_ADMIN_ID = int(os.getenv('TELEGRAM_ADMIN_ID', 0))
    
    # Free Fire Server
    FF_SERVER_IP = os.getenv('FF_SERVER_IP', 'localhost')
    FF_SERVER_PORT = int(os.getenv('FF_SERVER_PORT', 9339))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ff_bot.db')
    
    # Bot Settings
    REGION = os.getenv('REGION', 'PK')
    BOT_OWNER_UID = os.getenv('BOT_OWNER_UID', '')
    WHITELIST_MODE = os.getenv('WHITELIST_MODE', 'False').lower() == 'true'
    
    # Safety & Rate Limiting
    COMMAND_DELAY = float(os.getenv('COMMAND_DELAY', 2.0))
    MESSAGE_DELAY = float(os.getenv('MESSAGE_DELAY', 0.5))
    EMOTE_DELAY = float(os.getenv('EMOTE_DELAY', 1.0))
    RECONNECT_DELAY = float(os.getenv('RECONNECT_DELAY', 5.0))
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 30))
    
    # Security
    ENCRYPTION_ENABLED = os.getenv('ENCRYPTION_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    
    # Timeouts
    CONNECTION_TIMEOUT = 30
    REQUEST_TIMEOUT = 10
    
    # Emote Configuration
    FREEZE_EMOTES = [909052010, 909052010, 909052010]
    FREEZE_DURATION = 10
    
    # Badge Configuration
    BADGE_VALUES = {
        's1': 1, 's2': 2, 's3': 3, 's4': 4,
        's5': 5, 's6': 6, 's7': 7, 's8': 8
    }
    
    # Anti-Ban Settings
    RANDOM_DELAY_MIN = 0.5
    RANDOM_DELAY_MAX = 2.0
    USER_AGENT_ROTATION = True
    CONNECTION_POOL_SIZE = 5
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/bot.log'
    
config = Config()
