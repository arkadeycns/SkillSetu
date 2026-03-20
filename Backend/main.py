import sys
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# --- DEBUG SHIELD START ---
# Force Python to find the exact .env file next to this main.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(CURRENT_DIR, ".env")
load_dotenv(dotenv_path=env_path)

print("\n===  ENVIRONMENT VARIABLE CHECK  ===")
print(f"Looking for .env file at: {env_path}")
print(f"Is GROQ_API_KEY found? {'✅ YES' if os.environ.get('GROQ_API_KEY') else '❌ NO'}")
print(f"Is PINECONE_API_KEY found? {'✅ YES' if os.environ.get('PINECONE_API_KEY') else '❌ NO'}")
print("========================================\n")


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
from services.bootstrap_service import ensure_ai_service_ready
from api.resume_parser import router as resume_router
from api.training import router as training_router
from api.chat import router as chat_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        result = ensure_ai_service_ready()
        print("[startup] AI service bootstrap complete:", result)
    except Exception as exc:
        print("[startup] AI service bootstrap failed:", exc)
    yield


app = FastAPI(title="SkillSetu Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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
app.include_router(resume_router)
# FIXED: Removed the double prefix here so the routes resolve correctly!
app.include_router(training_router)
app.include_router(chat_router)

@app.get("/health")
def health():
    return {"status": "backend running"}

@app.get("/")
def root():
    return {"message": "SkillSetu Backend Running"}
