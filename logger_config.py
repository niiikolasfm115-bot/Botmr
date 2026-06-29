import os
from loguru import logger
from config import config

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Remove default handler
logger.remove()

# Add console handler with color
logger.add(
    lambda msg: print(msg, end=''),
    format="<level>{time:YYYY-MM-DD HH:mm:ss}</level> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=config.LOG_LEVEL,
    colorize=True
)

# Add file handler
logger.add(
    config.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="500 MB",
    retention="10 days"
)

# Suppress aiohttp logs
logging_logger = __import__('logging')
logging_logger.getLogger('aiohttp').setLevel(logging_logger.WARNING)
logging_logger.getLogger('telegram').setLevel(logging_logger.WARNING)
