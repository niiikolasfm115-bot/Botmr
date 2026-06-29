import asyncio
import time
from collections import defaultdict
from typing import Optional
from logger_config import logger
from config import config

class RateLimiter:
    """Rate limiter to prevent bot from getting banned"""
    
    def __init__(self, max_requests: int = config.MAX_REQUESTS_PER_MINUTE, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def acquire(self, identifier: str = 'default') -> bool:
        """Check if request can be made"""
        async with self.lock:
            now = time.time()
            # Clean old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if now - req_time < self.window
            ]
            
            if len(self.requests[identifier]) < self.max_requests:
                self.requests[identifier].append(now)
                return True
            return False
    
    async def wait_if_needed(self, identifier: str = 'default') -> float:
        """Wait until a request can be made"""
        while not await self.acquire(identifier):
            await asyncio.sleep(0.1)
        return 0.0
    
    async def reset(self, identifier: str = 'default'):
        """Reset counter for identifier"""
        async with self.lock:
            self.requests[identifier] = []

rate_limiter = RateLimiter()
