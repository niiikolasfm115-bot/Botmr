import asyncio
import random
from typing import Optional
from logger_config import logger
from config import config

class DelayManager:
    """Manages delays to simulate natural behavior"""
    
    @staticmethod
    async def command_delay():
        """Apply delay between commands"""
        delay = random.uniform(
            config.COMMAND_DELAY * 0.8,
            config.COMMAND_DELAY * 1.2
        )
        await asyncio.sleep(delay)
    
    @staticmethod
    async def message_delay():
        """Apply delay between messages"""
        delay = random.uniform(
            config.MESSAGE_DELAY * 0.8,
            config.MESSAGE_DELAY * 1.2
        )
        await asyncio.sleep(delay)
    
    @staticmethod
    async def emote_delay():
        """Apply delay between emotes"""
        delay = random.uniform(
            config.EMOTE_DELAY * 0.8,
            config.EMOTE_DELAY * 1.2
        )
        await asyncio.sleep(delay)
    
    @staticmethod
    async def random_delay(min_delay: float = 0.5, max_delay: float = 2.0):
        """Apply random delay"""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def batch_delay(items_count: int):
        """Apply delay based on number of items"""
        # Longer delay after batch operations
        delay = random.uniform(1.0, 3.0) * (items_count / 10)
        await asyncio.sleep(min(delay, 10.0))  # Cap at 10 seconds

delay_manager = DelayManager()
