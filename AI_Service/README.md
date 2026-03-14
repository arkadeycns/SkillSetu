# SkillSetu AI_Service

Multimodal assessment microservice for SkillSetu.

It supports:
- STT from voice answers (Groq Whisper)
- Translation to and from English (Groq Llama)
- SOP retrieval (Pinecone + Gemini embeddings)
- Image + transcript competency evaluation (Gemini Vision)
- TTS feedback audio (gTTS)
- Multi-turn interview state machine: 5 categories, 10 primary questions per category, 2 adaptive counter questions per primary

## 1. High-Level Flow

1. Frontend asks AI service for categories.
2. User picks one category.
3. Backend starts an assessment session.
4. For each turn, backend sends `audio + image`.
5. Service runs STT -> translation -> SOP retrieval -> evaluation.
6. If turn is a primary question, service generates 2 counter questions from SOP context.
7. Service returns:
- evaluation JSON
- localized feedback text
- feedback audio file name
- next prompt
8. Repeat until all 10 primary questions are completed.

## 2. Project Structure

- `interface.py`: FastAPI routes and pipeline orchestration
- `src/stt/transcriber.py`: Groq Whisper STT
- `src/engine/translator.py`: translation in/out of English
- `src/rag/indexer.py`: SOP ingestion to Pinecone
- `src/rag/retriever.py`: SOP retrieval
- `src/vision/analyzer.py`: multimodal competency evaluation
- `src/engine/question_bank.py`: question bank loader and runtime reload
- `src/engine/counter_generator.py`: SOP-guided counter question generation
- `src/engine/interview_manager.py`: in-memory session state machine
- `data/question_bank.json`: default 5-category question bank

## 3. Environment Variables

Use `.env` with:

```env
GROQ_API_KEY="..."
GEMINI_API_KEY="..."
PINECONE_API_KEY="..."
QUESTION_BANK_PATH="data/question_bank.json"
```

Notes:
- `QUESTION_BANK_PATH` is optional. If omitted, default is `data/question_bank.json`.
- Pinecone index name is currently hardcoded as `skillsetu-sops`.

## 4. Install and Run

```bash
cd AI_Service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn interface:app --reload --port 8001
```

## 5. API Contract

### GET `/api/assessment/categories`
Returns available category list.

### POST `/api/assessment/start`
Form field: `category_id`

Returns:
- `session_id`
- `next_prompt` (first primary)

### GET `/api/assessment/{session_id}/next`
Returns current prompt for session.

### POST `/api/assessment/{session_id}/answer`
Multipart form-data:
- `audio` (required)
- `image` (required)

Returns:
- transcript fields
- evaluation JSON (`pass_fail`, `feedback`, `identified_gaps`)
- `localized_feedback`
- `feedback_audio_file`
- `next_prompt`
- `is_completed`

### GET `/api/assessment/{session_id}/summary`
Returns complete session history and pass-rate summary.

### GET `/api/assessment/audio/{filename}`
Returns generated feedback MP3.

## 6. Admin Content Operations

### POST `/api/admin/sops/index`
Upload a raw SOP `.txt` file and index it into Pinecone.

Form fields:
- `sop_file` (file)
- `batch_size` (optional, default `25`)

### POST `/api/admin/questions/upload`
Upload a custom question bank JSON and activate it immediately.

Form fields:
- `question_bank_file` (file)

### POST `/api/admin/questions/reload`
Reload question bank from a specific server path.

Form fields:
- `path` (string)

## 7. Custom SOP Format Guidance

For best retrieval quality:
- Keep SOP text grouped by paragraph-level procedure steps.
- Include task name, safety checks, tools, quality checks.
- Include guidance for probing counters, for example:
- What follow-up to ask when safety is missing
- What follow-up to ask when sequence is wrong
- What follow-up to ask when quality verification is weak

SOP ingestion chunks by paragraph (`\n\n`).

## 8. Custom Question Bank Format

JSON shape:

```json
{
  "categories": [
    {
      "id": "plumbing",
      "title": "Plumbing",
      "questions": [
        {"id": "PL-01", "text": "..."}
      ]
    }
  ]
}
```

Rules:
- Exactly 5 categories recommended (you can add/remove if needed).
- Each category must contain exactly 10 primary questions.
- Each question must include `id` and `text`.

## 9. Backend Integration (Recommended)

Recommended orchestration from `Backend/` service:

1. Call `GET /api/assessment/categories`.
2. User selects category in frontend.
3. Backend calls `POST /api/assessment/start` and stores `session_id`.
4. For each turn:
- Backend uploads `audio + image` to `POST /api/assessment/{session_id}/answer`.
- Backend forwards `next_prompt` and localized feedback to frontend.
- Optional: stream/download `feedback_audio_file` from `/api/assessment/audio/{filename}`.
5. When `is_completed=true`, fetch final summary from `/api/assessment/{session_id}/summary`.

## 10. Operational Notes

- Session state is currently in-memory. If service restarts, sessions are lost.
- For production, move session store to Redis/Postgres.
- Generated feedback audio files remain in `data/` until cleaned externally.
- Service assumes Pinecone index `skillsetu-sops` already exists with correct embedding dimension.

## 11. Suggested Next Hardening Steps

1. Add Redis-backed session persistence.
2. Add auth for admin endpoints.
3. Add background cleanup job for old feedback audio files.
4. Add rate limits and timeout/retry wrappers for external model calls.
5. Add unit tests for question bank validation and interview stage transitions.
