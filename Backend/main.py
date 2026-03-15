import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
