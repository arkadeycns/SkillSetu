# SkillSetu Backend


The **SkillSetu Backend** is a modular AI-powered backend system built using **FastAPI**.
It exposes scalable RESTful APIs that support intelligent skill assessments, AI-based speech processing, retrieval-augmented generation, and skill analytics.

The backend is designed with a **clean service-oriented architecture**, separating API routing, AI services, and application logic to ensure scalability and maintainability.

---

# System Architecture

The backend follows a **layered architecture pattern** to maintain separation of concerns.

Client / Frontend
↓
FastAPI API Layer
↓
Service Layer (AI + Business Logic)
↓
External AI Models (Groq / Gemini)

### Architecture Layers

**1. API Layer**

* Handles incoming HTTP requests
* Performs request validation using **Pydantic**
* Routes requests to the appropriate services

**2. Service Layer**

* Encapsulates business logic
* Interfaces with AI models and internal modules
* Ensures reusable and modular functionality

**3. AI Integration Layer**

* Handles communication with external AI APIs
* Includes speech generation, transcription, and LLM inference

---

# Technology Stack

The backend leverages modern technologies optimized for high-performance API systems.

* **Python** – Core backend language
* **FastAPI** – High-performance API framework
* **Uvicorn** – ASGI server for running the application
* **Groq API** – Large language model inference
* **Gemini API** – AI capabilities and reasoning
* **Pydantic** – Data validation and serialization
* **Python-dotenv** – Secure environment configuration

---

## Project Structure

The project is organized using a modular architecture to maintain clarity and scalability.

Backend/
│
├── api/
│ ├── tts.py # Text-to-Speech API
│ ├── stt.py # Speech-to-Text API
│ ├── rag.py # Retrieval-Augmented Generation API
│ ├── heatmap.py # Skill analytics endpoints
│ ├── skill_wallet.py # User skill tracking
│ ├── assessment.py # Assessment workflow APIs
│ └── admin.py # Admin management APIs
│
├── AI_services/
│ ├── interface.py # Central AI interface layer
│ ├── tts_service.py # Speech generation logic
│ └── stt_service.py # Speech transcription logic
│
├── main.py # FastAPI application entrypoint
├── requirements.txt # Project dependencies
├── .env # Environment variables
└── README.md # Project documentation

---

# API Endpoints

The backend exposes several APIs categorized by functionality.

---

# Speech Processing APIs

### Text to Speech

**POST /api/v1/text-to-speech**

Converts textual input into synthesized speech audio.

**Key capabilities**

* Speech generation using AI models
* Text-to-audio conversion
* Audio file generation

---

### Speech to Text

**POST /api/v1/speech-to-text**

Transcribes spoken audio into textual format.

**Key capabilities**

* Audio transcription
* Speech recognition
* Integration with AI speech models

---

# Retrieval-Augmented Generation (RAG)

### RAG Query

**POST /api/v1/rag**

Processes user queries using **document retrieval combined with LLM reasoning** to generate contextual responses.

**Features**

* Context-aware responses
* Document retrieval
* LLM-powered reasoning

---

# Skill Analytics

### Skill Heatmap

**GET /heatmap**

Returns analytics data used to visualize skill performance across different domains.

**Features**

* Skill distribution analytics
* Performance heatmaps
* User progress insights

---

### Skill Wallet

**GET /api/v1/skill-wallet/{user_id}**

Tracks and returns the user's skill progression and competency levels.

**Features**

* Skill progress tracking
* Performance metrics
* Personalized analytics

---

# Assessment APIs

These APIs manage the **interactive skill assessment workflow**.

---

### Get Assessment Categories

**GET /api/assessment/categories**

Returns available assessment categories.

---

### Start Assessment

**POST /api/assessment/start**

Initializes a new assessment session.

**Functionality**

* Creates a session ID
* Initializes user assessment state

---

### Get Next Prompt

**GET /api/assessment/{session_id}/next**

Returns the next question or prompt in the active assessment session.

---

### Submit Answer

**POST /api/assessment/{session_id}/answer**

Submits a user's answer for evaluation.

---

### Get Assessment Summary

**GET /api/assessment/{session_id}/summary**

Returns a comprehensive summary of the user's assessment performance.

---

### Retrieve Generated Audio

**GET /api/assessment/audio/{filename}**

Fetches generated audio files used during assessments.

---

# Admin APIs

Administrative APIs enable system-level management.

---

### Upload Questions

**POST /api/admin/questions/upload**

Uploads new question datasets into the system.

---

### Reload Questions

**POST /api/admin/questions/reload**

Reloads the question bank dynamically without restarting the backend.

---

### Index SOPs

**POST /api/admin/sops/index**

Indexes SOP documents to enable **RAG-based retrieval**.

---

# Utility APIs

### Health Check

**GET /health**

Used for monitoring and verifying backend service availability.

---

### Root Endpoint

**GET /**

Returns a basic response confirming the backend is running.

---

# Authentication (Currently in Development)

Authentication functionality is being implemented to ensure secure API access.

Planned features include:

* JWT-based authentication
* Secure user registration and login
* Protected API routes
* Role-based access control
* Token validation middleware

Authentication will secure user-specific endpoints such as:

* Skill wallet
* Assessments
* Analytics APIs

---

# Environment Configuration

Create a `.env` file in the project root directory.

Example configuration:

GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
QUESTION_BANK_PATH=path_to_question_bank

Environment variables are loaded securely using **python-dotenv**.

---

# Installation

### 1. Clone the repository

git clone <repository_url>
cd Backend

### 2. Install dependencies

pip install -r requirements.txt

---

# Running the Server

Start the FastAPI application using Uvicorn.

uvicorn main:app --reload

The server will run at:

http://127.0.0.1:8000

---

# API Documentation

FastAPI automatically generates interactive documentation.

**Swagger UI**

http://127.0.0.1:8000/docs

**ReDoc**

http://127.0.0.1:8000/redoc

These interfaces allow developers to explore and test endpoints interactively.

---

# Testing

API endpoints were tested through:

* FastAPI Swagger UI
* Local API requests
* Response validation checks

This ensured seamless integration between the API routes and the AI service modules.

---

# Design Principles

The backend is designed around the following principles:

* Modular architecture
* Clear separation of concerns
* Scalable API design
* Secure environment configuration
* Maintainable service abstraction

---

# Future Improvements

Planned improvements include:

* Docker containerization
* Advanced authentication and authorization
* API rate limiting
* Centralized logging and monitoring
* Cloud deployment

---

# Maintainer

**Apoorva Pandey**

* Backend Development
* FastAPI Architecture
* AI Service Integration

GitHub:https://github.com/apoorva-ppl
