# SkillSetu Backend Blueprint

## Objective
Build Backend as the orchestration and product API layer, while AI_Service remains the AI execution engine.

This keeps responsibilities clean:
- Backend: auth, product APIs, orchestration, session metadata, normalized responses
- AI_Service: STT, translation, RAG retrieval, competency evaluation, counter-question generation, feedback audio

## Recommended Architecture

### Service boundaries
- Frontend talks only to Backend.
- Backend talks to AI_Service over HTTP.
- Backend should not re-implement STT, RAG, translation, or vision logic.

### Why this is the right baseline
- Faster development and fewer duplicate bugs.
- AI model changes stay isolated in AI_Service.
- Backend can evolve independently for auth, analytics, and business rules.

## Target Backend API (public contract)

### Assessment flow
- GET /api/v1/assessment/categories
- POST /api/v1/assessment/start
- GET /api/v1/assessment/{session_id}/next
- POST /api/v1/assessment/{session_id}/answer
- GET /api/v1/assessment/{session_id}/summary
- GET /api/v1/assessment/audio/{filename}

### Existing product modules
- GET /api/v1/skill-wallet/{user_id}
- GET /api/v1/heatmap

Note: Keep heatmap and skill wallet local for now if they are product-only features and not part of AI_Service.

## Endpoint mapping to AI_Service

Backend should map internal calls as:
- GET /api/v1/assessment/categories -> AI_Service GET /api/assessment/categories
- POST /api/v1/assessment/start -> AI_Service POST /api/assessment/start
- GET /api/v1/assessment/{session_id}/next -> AI_Service GET /api/assessment/{session_id}/next
- POST /api/v1/assessment/{session_id}/answer -> AI_Service POST /api/assessment/{session_id}/answer
- GET /api/v1/assessment/{session_id}/summary -> AI_Service GET /api/assessment/{session_id}/summary
- GET /api/v1/assessment/audio/{filename} -> AI_Service GET /api/assessment/audio/{filename}

## Foundation decisions to lock now

### 1) One response envelope
Use a single response shape for all Backend endpoints:
- success: boolean
- data: object or null
- error: object or null
- request_id: string

Error object:
- code: string
- message: string
- details: optional object

### 2) Timeout and retry policy
For AI_Service calls:
- connect timeout: 3s
- read timeout: 60s for answer endpoint, 15s for others
- retries: 2 retries only for transient 5xx and network errors
- no retries for 4xx

### 3) Session ownership model
Short term:
- AI_Service owns assessment session progression.
- Backend stores minimal mapping and telemetry only.

Long term:
- move session persistence to Redis or DB and make ownership explicit.

### 4) File strategy
- Backend receives multipart audio and image from frontend.
- Backend forwards streams to AI_Service without saving permanently.
- Feedback audio endpoint can proxy stream from AI_Service.

### 5) Configuration contract
Add env variables in Backend:
- AI_SERVICE_BASE_URL
- AI_SERVICE_TIMEOUT_SECONDS
- AI_SERVICE_CONNECT_TIMEOUT_SECONDS
- API_VERSION

## Recommended folder structure (incremental)

Backend/
- api/
  - assessment.py
  - heatmap.py
  - skill_wallet.py
- clients/
  - ai_service_client.py
- schemas/
  - common.py
  - assessment_schemas.py
  - heatmap_schemas.py
  - skill_wallet_schemas.py
- services/
  - assessment_service.py
  - heatmap_service.py
  - skill_wallet_service.py
- core/
  - config.py
  - errors.py
  - logging.py
- main.py

## Implementation phases

### Phase 1: Skeleton and contracts
- Add assessment router and schemas.
- Add AI service client with base URL, timeout, and retry wrappers.
- Keep current heatmap and skill_wallet endpoints as-is.

### Phase 2: Full assessment proxy
- Wire all assessment endpoints through assessment service.
- Normalize AI_Service responses into Backend envelope.
- Map upstream errors into stable backend errors.

### Phase 3: Hardening
- request_id propagation
- structured logging
- input validation and size limits for uploads
- health checks for AI_Service reachability

### Phase 4: Production readiness
- auth and authorization
- rate limiting
- background cleanup and monitoring
- integration tests against AI_Service staging

## Minimal test plan
- Contract tests for each assessment endpoint.
- Negative tests for missing audio/image, invalid session_id, AI_Service timeout.
- Smoke test that category->start->answer->summary works end to end.

## Migration from current code
1. Keep existing app bootstrap in main.py.
2. Add new assessment router under /api/v1/assessment.
3. Deprecate placeholder STT, TTS, and RAG endpoints once assessment flow is live.
4. Remove dummy service functions only after frontend switches to assessment flow.

## Current files to keep and evolve
- main.py
- api/heatmap.py
- api/skill_wallet.py
- services/heatmap_service.py
- services/skill_wallet_service.py

## Current files to replace over time
- api/stt.py
- api/tts.py
- api/rag.py
- services/stt_service.py
- services/tts_service.py
- services/rag_service.py
