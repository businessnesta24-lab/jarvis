# utils.py
import os, re, json, logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# try sentence-transformers
_HAS_ST = False
try:
    from sentence_transformers import SentenceTransformer
    _HAS_ST = True
except Exception:
    _HAS_ST = False

EMBED_MODEL = None
if _HAS_ST:
    try:
        EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        logger.warning("SentenceTransformer load failed: %s", e)
        EMBED_MODEL = None
        _HAS_ST = False

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'<.*?>', ' ', text)
    return text.strip()

def chunk_text(text: str, max_words: int = 400) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i+max_words]))
    return chunks

def save_chunked_content(chunks: List[str], outpath: str):
    os.makedirs(os.path.dirname(outpath) or ".", exist_ok=True)
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def embed_text(texts: List[str]):
    """
    Returns list of vectors. If sentence-transformers not available, returns None.
    """
    if EMBED_MODEL is None:
        logger.warning("Embed model not available (sentence-transformers missing).")
        return None
    return EMBED_MODEL.encode(texts, show_progress_bar=False)
