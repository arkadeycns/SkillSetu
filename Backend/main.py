import sys
import os
from dotenv import load_dotenv

# --- DEBUG SHIELD START ---
# Force Python to find the exact .env file next to this main.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(CURRENT_DIR, ".env")
load_dotenv(dotenv_path=env_path)

print("\n=== 🚦 ENVIRONMENT VARIABLE CHECK 🚦 ===")
print(f"Looking for .env file at: {env_path}")
print(f"Is GROQ_API_KEY found? {'✅ YES' if os.environ.get('GROQ_API_KEY') else '❌ NO'}")
print(f"Is PINECONE_API_KEY found? {'✅ YES' if os.environ.get('PINECONE_API_KEY') else '❌ NO'}")
print("========================================\n")
# --- DEBUG SHIELD END ---

BASE_DIR = os.path.dirname(CURRENT_DIR)

sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "AI_Service"))
sys.path.append(os.path.join(BASE_DIR, "AI_Service", "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.tts import router as tts_router
from api.stt import router as stt_router
from api.rag import router as rag_router
from api.heatmap import router as heatmap_router
from api.skill_wallet import router as skill_wallet_router
from api.assessment import router as assessment_router
from api.admin import router as admin_router
from api.audio import router as audio_router

app = FastAPI(title="SkillSetu Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(rag_router)
app.include_router(heatmap_router)
app.include_router(skill_wallet_router)
app.include_router(assessment_router)
app.include_router(admin_router)
app.include_router(audio_router)

@app.get("/health")
def health():
    return {"status": "backend running"}

@app.get("/")
def root():
    return {"message": "SkillSetu Backend Running"}