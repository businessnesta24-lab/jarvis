# agent.py - Hybrid Jarvis (voice + memory + crawler + offline LLM + OpenAI fallback)

import os, asyncio, logging, json
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jarvis")

# Load environment variables
load_dotenv()
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

# Voice libraries
try:
    import pyttsx3, speech_recognition as sr
except Exception:
    pyttsx3 = None
    sr = None

# Repo modules
from key_manager import APIKeyManager
from utils import clean_text, chunk_text, embed_text
from crawler import crawl_web
from memory import MemoryManager
from memory_store import ConversationMemory
from memory_loop import MemoryExtractor
from llm_offline import OfflineLLM

# OpenAI fallback
try:
    import openai
except Exception:
    openai = None

# Key manager
key_manager = APIKeyManager()

# Initialize TTS
TTS_ENGINE = None
if pyttsx3:
    try:
        TTS_ENGINE = pyttsx3.init()
        TTS_ENGINE.setProperty("rate", 150)
    except Exception as e:
        logger.warning("TTS init failed: %s", e)

def speak(text: str):
    print("Jarvis:", text)
    if TTS_ENGINE:
        try:
            TTS_ENGINE.say(text)
            TTS_ENGINE.runAndWait()
        except Exception:
            pass

# STT setup
RECOGNIZER = sr.Recognizer() if sr else None
MIC = None
if sr:
    try:
        MIC = sr.Microphone()
    except Exception:
        MIC = None

def listen(timeout: int = None, phrase_time_limit: int = 8) -> str:
    """Return user speech as text, fallback to input"""
    if RECOGNIZER is None or MIC is None:
        return input("You (type): ")
    try:
        with MIC as source:
            RECOGNIZER.adjust_for_ambient_noise(source, duration=0.6)
            print("Listening...")
            audio = RECOGNIZER.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        return RECOGNIZER.recognize_google(audio)
    except Exception:
        return input("You (type): ")

# Memory
memory = MemoryManager()
conv_mem = ConversationMemory(user_id="Gaurav")
session_history: List[Dict[str, Any]] = []

# Memory extractor
mem_extractor = MemoryExtractor(session_history, user_id="Gaurav")

# Offline LLM
offline = OfflineLLM(model_name=os.getenv("OFFLINE_MODEL") or None)

# OpenAI helper
def call_openai_chat(prompt: str, max_tokens: int = 500) -> str:
    key = key_manager.get_key()
    if not key:
        return ""
    try:
        openai.api_key = key
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        key_manager.rotate_key()
        return ""

# LLM wrapper
def call_llm(prompt: str) -> str:
    # Offline first
    if offline and getattr(offline, "model", None):
        try:
            ans = offline.generate(prompt)
            if ans:
                return ans
        except Exception:
            pass
    # Online fallback
    if openai:
        ans = call_openai_chat(prompt)
        if ans:
            return ans
    return "Sorry, mujhe iska answer nahi mila."

# Weather
def get_weather_city(city: str) -> str:
    if not WEATHERAPI_KEY:
        return "Weather API key missing."
    try:
        import requests
        r = requests.get(
            "http://api.weatherapi.com/v1/current.json",
            params={"key": WEATHERAPI_KEY, "q": city, "aqi": "no"},
            timeout=6
        )
        j = r.json()
        c = j["current"]["condition"]["text"]
        t = j["current"]["temp_c"]
        return f"Weather in {city}: {c}. Temp {t}°C."
    except Exception:
        return "Weather fetch error."

# Brain answer
def brain_answer(query: str, chat_history: List[Tuple[str, str]]) -> str:
    # Memory retrieval
    docs = memory.retrieve(query, top_k=4)
    if docs:
        context = "\n\n".join(docs)
        prompt = f"Use context:\n{context}\n\nQuestion: {query}"
        ans = call_llm(prompt)
        if ans:
            return ans

    # Wikipedia fallback
    try:
        import requests
        params = {"action": "opensearch", "search": query, "limit": 1, "format": "json"}
        r = requests.get("https://en.wikipedia.org/w/api.php", params=params, timeout=6)
        data = r.json()
        if data and len(data) > 1 and data[1]:
            title = data[1][0]
            q = {
                "action": "query",
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "titles": title,
                "format": "json"
            }
            r2 = requests.get("https://wikipedia.org/w/api.php", params=q, timeout=6)
            j = r2.json()
            for _, page in j["query"]["pages"].items():
                extract = page.get("extract", "")
                if extract:
                    memory.add_text(extract)
                    return f"{title}: {extract[:300]}..."
    except Exception:
        pass

    # Final fallback
    return call_llm(query)

# Main assistant loop
async def assistant_loop():
    task = asyncio.create_task(mem_extractor.run(check_interval=1.0))
    speak("Hello, main Jarvis hoon. Boliye.")
    learning_enabled = True
    chat_history: List[Tuple[str, str]] = []

    try:
        while True:
            user_text = listen()
            if not user_text:
                continue

            # Update memories
            session_history.append({"role": "user", "content": user_text})
            conv_mem.append_message("user", user_text)

            u = user_text.lower().strip()

            # Exit
            if u in ("exit", "quit", "bye"):
                speak("Theek hai. Alvida.")
                break

            # Clear memory
            if "clear memory" in u:
                memory.clear()
                conv_mem.clear()
                speak("Memory cleared.")
                continue

            # Weather query
            if "weather" in u:
                city = u.split(" in ")[-1] if "in" in u else "your city"
                res = get_weather_city(city)
                speak(res)
                session_history.append({"role": "assistant", "content": res})
                conv_mem.append_message("assistant", res)
                continue

            # General Q&A
            ans = brain_answer(user_text, chat_history)
            speak(ans)
            session_history.append({"role": "assistant", "content": ans})
            conv_mem.append_message("assistant", ans)
            chat_history.append((user_text, ans))

            if learning_enabled:
                memory.add_text(f"Q: {user_text}\nA: {ans}")

    finally:
        mem_extractor.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

# Start
if __name__ == "__main__":
    try:
        asyncio.run(assistant_loop())
    except Exception as e:
        logger.exception("Error: %s", e)
