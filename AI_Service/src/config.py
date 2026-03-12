# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GROQ_API_KEY or not GEMINI_API_KEY:
    print("WARNING: Missing API Keys in .env file.")