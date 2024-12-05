
import asyncio
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = datetime.now()
            
            while self.requests and now - self.requests[0] > timedelta(minutes=1):
                self.requests.popleft()
                
            if len(self.requests) >= self.requests_per_minute:
                wait_time = 60 - (now - self.requests[0]).total_seconds()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    
            self.requests.append(now)
