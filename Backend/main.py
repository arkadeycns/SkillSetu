from fastapi import FastAPI
from api.tts import router as tts_router
app = FastAPI(title="SkillSetu Backend")

app.include_router(tts_router)
@app.get("/")
def root():
    return {"message": "SkillSetu Backend Running"}