# The Bench - Multi-Agent Legal Simulation

## Overview
A web application where three parties (Accuser, Accused, Judge) contest a legal case in a structured, RAG-enhanced environment.

## 🚀 How to Run

### 1. Frontend (React)
Open a terminal in the `frontend` directory and run:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start at `http://localhost:5173`.

### 2. Backend (FastAPI)
Open a separate terminal in the `backend` directory and run:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend API documentation will be available at `http://localhost:8000/docs`.

## Technology Stack
-   **Frontend**: React, Vite, Tailwind CSS
-   **Backend**: Python, FastAPI
-   **Database**: SQLite/PostgreSQL, ChromaDB (Vector DB)
-   **AI**: Google Gemini/OpenAI API

## Project Structure
-   `/frontend`: Dashboard, Chat Interface, Court Record UI
-   `/backend`: API Logic, RAG Engine, LLM Integration
