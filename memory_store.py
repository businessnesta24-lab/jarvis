# memory_store.py
from typing import List, Dict

class ConversationMemory:
    """
    Handles conversational history for a user.
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.messages: List[Dict[str, str]] = []

    def append_message(self, role: str, content: str):
        """Append a message from user or assistant"""
        self.messages.append({"role": role, "content": content})

    def add_text(self, text: str):
        """Add system/assistant text"""
        self.messages.append({"role": "system", "content": text})

    def clear(self):
        """Clear all messages"""
        self.messages = []

    def get_messages(self):
        """Return full conversation history"""
        return self.messages
