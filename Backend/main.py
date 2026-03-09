from fastapi import FastAPI
from api.tts import router as tts_router
from api.stt import router as stt_router
from api.rag import router as rag_router
from api.heatmap import router as heatmap_router
from api.skill_wallet import router as skill_wallet_router
app = FastAPI(title="SkillSetu Backend")

app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(rag_router)
app.include_router(heatmap_router)
app.include_router(skill_wallet_router)

@app.get("/")
def root():
    return {"message": "SkillSetu Backend Running"}