# crawler.py
import os, requests, logging, re
from bs4 import BeautifulSoup
from utils import clean_text, chunk_text, save_chunked_content

logger = logging.getLogger(__name__)
COURSE_DIR = "courses"
os.makedirs(COURSE_DIR, exist_ok=True)

# (optional) yt-dlp transcript function if yt_dlp installed
def get_youtube_transcript(url: str) -> str:
    try:
        from yt_dlp import YoutubeDL
    except Exception:
        logger.warning("yt_dlp not installed; can't fetch youtube transcripts.")
        return ""
    ydl_opts = {"skip_download": True, "quiet": True, "writesubtitles": True, "writeautomaticsub": True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # try automatic captions
            subs = info.get("automatic_captions") or info.get("subtitles") or {}
            if not subs:
                return ""
            en = subs.get("en") or subs.get("en-US") or subs.get(next(iter(subs.keys())))
            if not en:
                return ""
            # en could be a list of dicts with 'url'
            urlm = en[0].get("url")
            if urlm:
                r = requests.get(urlm, timeout=10)
                text = re.sub(r'<.*?>', '', r.text)
                return clean_text(text)
    except Exception as e:
        logger.warning("YouTube transcript fetch failed: %s", e)
    return ""

def crawl_web(url: str) -> str:
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for s in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
            s.decompose()
        texts = [p.get_text(separator=" ", strip=True) for p in soup.find_all("p")]
        joined = "\n\n".join(t for t in texts if t)
        return clean_text(joined)
    except Exception as e:
        logger.warning("crawl_web failed for %s: %s", url, e)
        return ""
