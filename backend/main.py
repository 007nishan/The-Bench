from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import rag_engine
import case_manager
import shutil

load_dotenv()

app = FastAPI(title="The Bench API", description="Backend logical layer for the Multi-Agent Legal Simulation.")

# CORS for frontend (Replaces default CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArgumentSubmission(BaseModel):
    user_role: str
    argument_text: str
    evidence_ids: list[str]

class StrategyRequest(BaseModel):
    user_role: str
    query_text: str

class DocumentIngest(BaseModel):
    user_role: str
    doc_id: str
    content: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "The Bench System (RAG + Agents) is Active"}

@app.post("/ingest_document")
def ingest_document(ingest: DocumentIngest):
    """
    Simulate uploading a document to the Private Vault.
    """
    rag_engine.store_document(ingest.user_role, ingest.doc_id, ingest.content)
    return {"status": "stored", "message": f"Document {ingest.doc_id} added to {ingest.user_role}'s Private Vault."}

@app.post("/upload_doc")
async def upload_doc(
    user_role: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload a file (TXT/MD) to the Private Vault.
    """
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        
        # Store in RAG
        rag_engine.store_document(user_role, file.filename, text_content)
        
        return {"status": "success", "filename": file.filename, "message": "File processed and extracted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@app.post("/chat/strategy")
def get_strategy(request: StrategyRequest):
    """
    Ask the biased LLM for a strategy or draft argument.
    """
    try:
        response_text = rag_engine.generate_strategic_response(request.user_role, request.query_text)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit_argument")
def submit_argument(submission: ArgumentSubmission):
    """
    Submit an argument to the Judge. The Judge LLM automatically verifies references.
    """
    # Store in case record
    record = case_manager.submit_argument(submission.user_role, submission.argument_text, submission.evidence_ids)
    
    return {
        "status": "received", 
        "submission_id": record["id"],
        "message": "Argument filed. Awaiting Bench Review."
    }

@app.get("/judge/pending")
def get_pending_review():
    """
    Get all arguments waiting for Judge's verification.
    """
    return case_manager.get_pending_submissions()

@app.get("/court_log")
def get_court_log():
    """
    Get the public court record/timeline.
    """
    return case_manager.get_court_log()

class VerifyRequest(BaseModel):
    submission_id: str

@app.post("/judge/verify")
def verify_submission(req: VerifyRequest):
    """
    The AI Judge reviews a specific submission against the Evidence Vaults.
    """
    # 1. Fetch the submission details (We'd need a get_by_id, but for now filtering pending)
    pending = case_manager.get_pending_submissions()
    target = next((p for p in pending if p["id"] == req.submission_id), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    # 2. RAG Verification
    # The Judge searches for context related to the argument
    context = rag_engine.retrieve_context("judge", target["argument"], n_results=5)
    
    # 3. AI Judgment Call
    # Ask Gemini: "Does the context support this argument?"
    judge_prompt = f"""
    SYSTEM: You are the Presiding Judge. Your job is strict FACT CHECKING.
    
    ARGUMENT TO VERIFY (filed by {target['sender']}):
    "{target['argument']}"
    
    EVIDENCE FROM RECORD (Private & Public Vaults):
    {context}
    
    TASK:
    - If the evidence strictly supports the argument, verdict is "ADMITTED".
    - If the evidence contradicts or is missing, verdict is "REJECTED".
    - Provide brief notes on why.
    
    OUTPUT FORMAT:
    Verdict: [ADMITTED/REJECTED]
    Notes: [Explanation]
    """
    
    # Call Gemini (using the existing model from rag_engine for simplicity, or we could expose a generate method)
    # We'll assume rag_engine.model is accessible or use a helper
    import google.generativeai as genai
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(judge_prompt)
    ai_output = response.text
    
    # Parse Verdict (Naive parsing)
    status = "admitted" if "ADMITTED" in ai_output.upper() else "rejected"
    
    # 4. Update Record
    updated = case_manager.update_submission_status(req.submission_id, status, ai_notes=ai_output)
    
    return {"status": "success", "verdict": status, "details": updated}
