# implementation_plan.md

## Project: The Bench
**Vision**: A Multi-Agent Legal Simulation where three parties (Accuser, Accused, Judge) interact in a structured, adversarial environment. The system uses RAG (Retrieval-Augmented Generation) to ground arguments in facts and strictly enforces legal logic via an AI Judge.

**Status**: ✅ MVP Complete | 🚀 Ready for Deployment

---

## 1. Technology Stack

### Frontend (The Visual Layer)
-   **Framework**: React (Vite) ✅
-   **Styling**: Tailwind CSS (Configured for a "Bloomberg Terminal" style dark mode - Slate/Navy/Gold palette) ✅
-   **Icons**: Lucide React (Gavel, Shield, Pointer icons) ✅
-   **State Management**: React Context (To manage the 3-party session state) ✅

### Backend (The Logic Layer)
-   **Framework**: 
    -   **Development**: FastAPI (ASGI) - Hot reload, async features ✅
    -   **Production**: Flask (WSGI) - Native support for PythonAnywhere ✅
-   **AI Orchestration**: Direct Google Gemini API calls with structured outputs ✅
-   **Database**: 
    -   *Vector*: ChromaDB (Local) for Semantic Search (RAG) ✅
    -   *Relational*: In-memory case management (Future: PostgreSQL)

### AI & LLMs
-   **Provider**: Google Gemini API ✅
-   **Agent Personas**:
    -   *Accuser Agent*: Biased, persuasive arguments for guilt ✅
    -   *Defense Agent*: Biased, persuasive arguments for innocence ✅
    -   *Judge Agent*: Fact-checking with strict citation verification ✅

---

## 2. Architecture & Modules

### A. The "Three Portal" System ✅

1.  **The War Room (Accuser/Accused)** ✅
    -   **Private Vault**: Upload/Manage private evidence ✅
    -   **Strategist Chat**: Chat with biased LLM to draft arguments ✅
    -   **Drafting Pad**: Text area to refine and "File Motion" ✅

2.  **The Bench (Judge)** ✅
    -   **Review Panel**: Incoming arguments from both parties ✅
    -   **Verification System**: AI-powered citation checking ✅
    -   **Ruling Display**: Shows ADMITTED/REJECTED with reasoning ✅

3.  **The Common Ground (Shared View)** ✅
    -   **Court Record**: Live timeline of all submissions and rulings ✅
    -   **Evidence Library**: Displays uploaded documents ✅

### B. The Logic Flow (Backend) ✅
1.  **Ingestion**: Documents uploaded → Chunked → Vectorized → Stored with metadata ✅
2.  **Submission**: User submits argument → Stored in case manager ✅
3.  **Judicial Review**: Judge verifies → RAG retrieval → AI judgment → Record updated ✅

---

## 3. Deployment Architecture

### Dual Backend Approach (Problem Solution)

**Issue**: PythonAnywhere uses WSGI servers, but FastAPI is ASGI. The `a2wsgi` adapter was causing 504 timeout errors.

**Solution**: Created two backend implementations:

#### **FastAPI Backend** (`backend/main.py`)
- **Purpose**: Local development
- **Server**: Uvicorn (ASGI)
- **Features**: Hot reload, async operations, full FastAPI features
- **Command**: `uvicorn main:app --reload`

#### **Flask Backend** (`backend/flask_app.py`) ✅ NEW
- **Purpose**: Production deployment (PythonAnywhere)
- **Server**: Native WSGI (no adapter needed)
- **Features**: 
  - ✅ Identical API endpoints to FastAPI
  - ✅ No hanging/timeout issues
  - ✅ Better error messages
  - ✅ Production-ready and stable
- **Command**: `python flask_app.py` (or via WSGI config)

### Frontend Updates ✅
- All API calls updated to use relative paths (`/api/...`)
- Works seamlessly with both backends
- Build: `npm run build` creates production-ready `dist/` folder

---

## 4. Phase 1: MVP Roadmap ✅ COMPLETED

-   [x] **Step 1: Setup**: Initialize React Frontend and FastAPI Backend ✅
-   [x] **Step 2: Database**: Set up ChromaDB connection ✅
-   [x] **Step 3: UI Shell**: Build the "Split-View" Layout (Sidebar, Main Workspace, Common Feed) ✅
-   [x] **Step 4: RAG Engine**: Implement document upload and vectorization ✅
-   [x] **Step 5: Agent Logic**: Implement the 3 System Prompts (Accuser, Accused, Judge) ✅
-   [x] **Step 6: The "Trial" Loop**: Connect the flow: Draft → Submit → Verify → Judgement ✅
-   [x] **Step 7: Flask Backend**: Create production-ready WSGI backend ✅
-   [x] **Step 8: Deployment Ready**: Update WSGI config, frontend API paths ✅

---

## 5. Deployment Checklist

### Pre-Deployment
- [x] Flask backend created and tested
- [x] Frontend updated to use relative API paths
- [x] Requirements.txt updated with Flask dependencies
- [x] WSGI configuration updated (no more a2wsgi)
- [ ] Frontend built for production (`npm run build`)

### PythonAnywhere Setup
- [ ] Upload code to `/home/YourUsername/TheBench/`
- [ ] Create virtual environment (`mkvirtualenv thebench`)
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Set environment variables (`.env` file with `GOOGLE_API_KEY`)
- [ ] Configure WSGI file (use `pa_wsgi.py`)
- [ ] Set virtualenv path in Web tab
- [ ] Reload web app
- [ ] Test all endpoints

---

## 6. Documentation Created

- ✅ `FIX_SUMMARY.md` - Details of the a2wsgi issue and solution
- ✅ `DEPLOYMENT_GUIDE.md` - Comprehensive deployment instructions
- ✅ `QUICK_REFERENCE.md` - Command reference card
- ✅ `test_flask_backend.py` - Automated backend testing script

---

## 7. Future Enhancements (Phase 2)

-   [ ] User Authentication & Sessions
-   [ ] PostgreSQL integration for persistent case storage
-   [ ] Multi-case support (case IDs, case management)
-   [ ] Enhanced Judge UI with citation highlighting
-   [ ] Evidence cross-referencing visualization
-   [ ] Real-time collaborative features
-   [ ] API rate limiting and security hardening
-   [ ] Admin portal for case oversight

---

## Quick Start Commands

### Local Development
```bash
# Backend (FastAPI)
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

### Production Build
```bash
# Build frontend
cd frontend
npm run build

# Test Flask backend
python test_flask_backend.py

# Run Flask
cd backend
python flask_app.py
```

---

**Next Step**: Deploy to PythonAnywhere following `DEPLOYMENT_GUIDE.md`

