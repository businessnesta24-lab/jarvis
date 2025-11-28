# memory_loop.py
import asyncio
from typing import List, Dict, Any

class MemoryExtractor:
    """
    Periodically extracts conversation text and stores into memory.
    """
    def __init__(self, session_history: List[Dict[str, Any]], user_id: str, interval: float = 5.0):
        self.session_history = session_history
        self.user_id = user_id
        self.interval = interval
        self._running = False

    async def run(self, check_interval: float = None):
        """Background loop"""
        self._running = True
        interval = check_interval or self.interval
        while self._running:
            await self.extract_memory()
            await asyncio.sleep(interval)

    async def extract_memory(self):
        """Extract messages from session history (dummy placeholder)"""
        # You can implement embedding or FAISS indexing here
        if self.session_history:
            # For demo, just print length
            print(f"[MemoryExtractor] Session has {len(self.session_history)} messages.")

    def stop(self):
        self._running = False
