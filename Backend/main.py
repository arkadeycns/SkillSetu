import sys
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- DEBUG SHIELD START ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(CURRENT_DIR, ".env")
load_dotenv(dotenv_path=env_path)

print("\n=== ENVIRONMENT VARIABLE CHECK ===")
print(f"Looking for .env file at: {env_path}")
print(f"Is GROQ_API_KEY found? {' YES' if os.environ.get('GROQ_API_KEY') else ' NO'}")
print(f"Is PINECONE_API_KEY found? {' YES' if os.environ.get('PINECONE_API_KEY') else ' NO'}")
print("========================================\n")

# Path setup for AI Service
BASE_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "AI_Service"))
sys.path.append(os.path.join(BASE_DIR, "AI_Service", "src"))

# Router Imports
from api.tts import router as tts_router
from api.stt import router as stt_router
from api.rag import router as rag_router
from api.heatmap import router as heatmap_router
from api.skill_wallet import router as skill_wallet_router
from api.assessment import router as assessment_router
from api.admin import router as admin_router
from api.audio import router as audio_router
from api.resume_parser import router as resume_router
from api.training import router as training_router
from api.chat import router as chat_router
from api.user_routes import router as user_router

# Core Services
from services.bootstrap_service import ensure_ai_service_ready
from core.database import connect_to_mongo, close_mongo_connection

# --- CONSOLIDATED LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events cleanly."""
    # 1. Connect to MongoDB
    try:
        await connect_to_mongo()
        print("[startup] MongoDB connected successfully.")
    except Exception as exc:
        print("[startup] MongoDB connection failed:", exc)

    # 2. Bootstrap AI Service (Groq/Pinecone/etc)
    try:
        result = ensure_ai_service_ready()
        print("[startup] AI service bootstrap complete:", result)
    except Exception as exc:
        print("[startup] AI service bootstrap failed:", exc)
        
    yield  # --- Application Runs Here ---
    
    # 3. Cleanup on shutdown
    try:
        await close_mongo_connection()
        print("[shutdown] MongoDB connection closed.")
    except Exception as exc:
        print("[shutdown] Error during MongoDB cleanup:", exc)


app = FastAPI(title="SkillSetu Backend", lifespan=lifespan)

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",   
        "http://127.0.0.1:5174", ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER REGISTRATION ---
# User & Wallet Routes
app.include_router(skill_wallet_router, prefix="/api/wallet", tags=["Wallet"])
app.include_router(assessment_router, prefix="/api/assessment", tags=["Assessment"])
app.include_router(user_router, prefix="/api/user", tags=["User"])

# Admin & Heatmap Routes
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(heatmap_router, prefix="/api/heatmap", tags=["Heatmap"])

# AI & Media Routes
app.include_router(tts_router, prefix="/api/tts", tags=["AI"])
app.include_router(stt_router, prefix="/api/stt", tags=["AI"])
app.include_router(audio_router, prefix="/api/audio", tags=["Media"])
app.include_router(chat_router, prefix="/api/chat", tags=["AI"])

# Documentation & Training
app.include_router(rag_router, prefix="/api/rag", tags=["AI"])
app.include_router(resume_router, prefix="/api/resume", tags=["Utility"])
app.include_router(training_router, prefix="/api/training", tags=["Training"])

@app.get("/health")
def health():
    return {"status": "backend running", "database": "connected"}

@app.get("/")
def root():
    return {"message": "SkillSetu API v1.0 - Active"}