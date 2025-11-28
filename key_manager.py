import os
from dotenv import load_dotenv

load_dotenv()

class APIKeyManager:
    def __init__(self):
        # Load all keys
        self.keys = [os.getenv(f"OPENAI_KEY_{i}") for i in range(1, 16) if os.getenv(f"OPENAI_KEY_{i}")]
        if not self.keys:
            raise ValueError("❌ No API keys found in .env")
        self.index = 0

    def get_key(self):
        return self.keys[self.index]

    def rotate_key(self):
        # Move to next key for next call
        self.index = (self.index + 1) % len(self.keys)
        os.environ["OPENAI_API_KEY"] = self.keys[self.index]  # update env variable if code reads it
        return self.keys[self.index]
