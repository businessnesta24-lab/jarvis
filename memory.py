# memory.py
import os, json
from typing import List

class MemoryManager:
    """
    Handles storing and retrieving text memories.
    Saves memories in local JSON files.
    """
    def __init__(self, memory_dir: str = "memories"):
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)
        self.memories_file = os.path.join(self.memory_dir, "memory.json")
        self._memories: List[str] = []

        # Load existing memories
        if os.path.exists(self.memories_file):
            try:
                with open(self.memories_file, "r", encoding="utf-8") as f:
                    self._memories = json.load(f)
            except Exception:
                self._memories = []

    def add_text(self, text: str):
        """Add text to memory"""
        self._memories.append(text)
        self._save()

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve relevant memories containing query keywords.
        Simple keyword match for demo purposes.
        """
        results = [m for m in self._memories if query.lower() in m.lower()]
        return results[:top_k]

    def clear(self):
        """Clear all memories"""
        self._memories = []
        self._save()

    def _save(self):
        """Save memories to disk"""
        try:
            with open(self.memories_file, "w", encoding="utf-8") as f:
                json.dump(self._memories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Error saving memory:", e)
