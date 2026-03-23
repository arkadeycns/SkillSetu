## SkillSetu

SkillSetu is an AI-powered skill assessment and guidance platform focused on practical, blue-collar upskilling.
It also provides an analytical dashboard to monitor and track the distribution of skills and talent across India - region wise. 
It includes:

- AI interview and scoring workflow
  <img width="1280" height="832" alt="Screenshot 2026-03-24 at 2 10 40 AM" src="https://github.com/user-attachments/assets/b42f761a-219b-4d52-9240-e5d91947713c" />

  
- Voice-based interaction (STT/TTS)
- Personalized guidance chat
- Training roadmap generation based on profile, strengths, and gaps

## Screenshots

<p align="left">
	<img src="https://github.com/user-attachments/assets/227e0f1e-de17-479a-8030-040c79df1afa" alt="SkillSetu Screenshot 1" width="250" />
	<img src="https://github.com/user-attachments/assets/b42f761a-219b-4d52-9240-e5d91947713c" alt="SkillSetu Screenshot 2" width="250" />
	<img src="https://github.com/user-attachments/assets/9f280f89-6e25-455b-8c75-b18646cf44ba" alt="SkillSetu Screenshot 3" width="250" />
</p>

## Repository Structure

- `AI_Service/`: Core AI logic (interview orchestration, roadmap generation, RAG, STT/TTS helpers)
- `Backend/`: FastAPI APIs for interview, chat, training, resume parsing, and persistence
- `Frontend/skillsetu-frontend/`: React + Vite web client

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React + Vite
- AI: Groq-based chat flows + RAG pipeline
- Voice: Speech-to-Text and Text-to-Speech integration

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

## Quick Start

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd SkillSetu
```

### 2. Backend setup

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create/update `Backend/.env` with required keys (example):

```env
GROQ_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

Run backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. AI service setup (if run separately)

```bash
cd ../AI_Service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Frontend setup

```bash
cd ../Frontend/skillsetu-frontend
npm install
npm run dev
```

Frontend runs on Vite default port (usually `5173`), backend on `8000`.

## Main API Routes

- `/api/assessment/*`: Interview session start, voice assessment turn handling, summary
- `/api/chat/*`: Guidance chat start and conversation turns
- `/api/training/recommend`: Personalized training roadmap generation
- `/api/v1/resume/parse`: Resume parsing endpoint

## Typical User Flow

1. User chooses skill and language.
2. AI interview runs via voice turns.
3. System computes summary, strengths, and gaps.
4. Training roadmap is generated from profile + interview evidence.
5. User can continue in AI guidance chat.

## Notes

- Keep API keys out of source control.
- Runtime temp folders and generated artifacts should remain ignored by git.
- If ports are busy, change backend/frontend ports accordingly.

## License

Public and Open-source
