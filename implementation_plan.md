# implementation_plan.md

## Project: The Bench
**Vision**: A Multi-Agent Legal Simulation where three parties (Accuser, Accused, Judge) interact in a structured, adversarial environment. The system uses RAG (Retrieval-Augmented Generation) to ground arguments in facts and strictly enforces legal logic via an AI Judge.

---

## 1. Technology Stack

### Frontend (The Visual Layer)
-   **Framework**: React (Vite)
-   **Styling**: Tailwind CSS (Configured for a "Bloomberg Terminal" style dark mode - Slate/Navy/Gold palette)
-   **Icons**: Lucide React (Gavel, Shield, Pointer icons)
-   **State Management**: Zustand or Context API (To manage the 3-party session state)

### Backend (The Logic Layer)
-   **Framework**: Python (FastAPI) - Chosen for superior RAG/LLM library support.
-   **AI Orchestration**: LangChain or direct API calls with Pydantic for structured outputs.
-   **Database**: 
    -   *Relational*: SQLite (Development) / PostgreSQL (Production) for Users, Case Logs, Chat History.
    -   *Vector*: ChromaDB (Local) or Pinecone for Semantic Search (RAG).

### AI & LLMs
-   **Provider**: Google Gemini API (or OpenAI/Anthropic based on preference).
-   **Agent Personas**:
    -   *Prosecutor Agent*: Biased, maximizing guilt arguments.
    -   *Defense Agent*: Biased, minimizing liability arguments.
    -   *Judge Agent*: Weighted Logic (Positivism > Formalism > Realism), strict verifier.

---

## 2. Architecture & Modules

### A. The "Three Portal" System
Authentication will route users to one of three dashboards:

1.  **The War Room (Accuser/Accused)**
    -   **Private Vault**: Upload/Manage private evidence.
    -   **Strategist Chat**: Chat with biased LLM to draft arguments.
    -   **Internal Warning System**: Red-box warnings for weak arguments (visible only to user).
    -   **Drafting Pad**: Text editor to refine and "Submit to Bench".

2.  **The Bench (Judge)**
    -   **Review Panel**: Incoming arguments vs. Source Documents.
    -   **Verification Heatmap**: Green/Red highlights for verified/hallucinated citations.
    -   **Inquiry System**: Interface to issue "Show Cause" or "Clarification" questions.

3.  **The Common Ground (Shared View)**
    -   **Court Record**: Chronological, immutable timeline of accepted filings.
    -   **Shared Library**: Laws, Statutes, and Evidence admitted into discovery.

### B. The Logic Flow (Backend)
1.  **Ingestion**: Documents are uploaded -> Chunked -> Vectorized -> Stored with Metadata (Page #, Source).
2.  **Submission Gate**: User submits argument -> Algorithm checks for "Exact References" -> If missing, reject.
3.  **Judicial Review**: Valid submission -> Judge LLM queries Vector DB -> Verifies Citations -> Updates Record.

---

## 3. Phase 1: MVP Roadmap

-   [ ] **Step 1: Setup**: Initialize React Frontend and FastAPI Backend.
-   [ ] **Step 2: Database**: Set up SQLite schema and ChromaDB connection.
-   [ ] **Step 3: UI Shell**: Build the "Split-View" Layout (Sidebar, Main Workspace, Common Feed).
-   [ ] **Step 4: RAG Engine**: Implement document upload and vectorization.
-   [ ] **Step 5: Agent Logic**: Implement the 3 System Prompts (Accuser, Accused, Judge).
-   [ ] **Step 6: The "Trial" Loop**: Connect the flow: Draft -> Submit -> Verify -> Judgement.
