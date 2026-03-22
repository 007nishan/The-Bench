import json
import os
import uuid
from datetime import datetime
import pytz

CASE_FILE = "case_record.json"

def _get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime("%Y-%m-%d %I:%M %p")

def load_case_record():
    if os.path.exists(CASE_FILE):
        try:
            with open(CASE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"submissions": [], "court_log": []}

def save_case_record(record):
    with open(CASE_FILE, "w") as f:
        json.dump(record, f, indent=2)

def submit_argument(role, text, references):
    record = load_case_record()
    
    submission_id = str(uuid.uuid4())
    submission = {
        "id": submission_id,
        "sender": role,
        "argument": text,
        "references": references or [],
        "status": "pending", # pending, verified, rejected, admitted
        "timestamp": _get_ist_time(),
        "ai_notes": None,
        "inquiries": []
    }
    
    record["submissions"].append(submission)
    
    # Log to court record (Private log for now, until admitted)
    record["court_log"].append({
        "timestamp": _get_ist_time(),
        "actor": role,
        "action": "Filed Argument",
        "details": f"Submission ID {submission_id[:8]}"
    })
    
    save_case_record(record)
    return submission

def get_pending_submissions():
    record = load_case_record()
    return [s for s in record["submissions"] if s["status"] == "pending"]

def get_court_log():
    record = load_case_record()
    return record.get("court_log", [])

def update_submission_status(sub_id, status, ai_notes=None):
    record = load_case_record()
    updated_item = None
    
    for sub in record["submissions"]:
        if sub["id"] == sub_id:
            sub["status"] = status
            if ai_notes:
                sub["ai_notes"] = ai_notes
            updated_item = sub
            break
            
    if updated_item and status == "admitted":
        record["court_log"].append({
            "timestamp": _get_ist_time(),
            "actor": "Judge",
            "action": "Ruling",
            "details": f"Argument {sub_id[:8]} Admitted to Record."
        })
    elif updated_item and status == "rejected":
         record["court_log"].append({
            "timestamp": _get_ist_time(),
            "actor": "Judge",
            "action": "Ruling",
            "details": f"Argument {sub_id[:8]} REJECTED from Record."
        })
        
    save_case_record(record)
    return updated_item

def add_inquiry(sub_id, question_text):
    record = load_case_record()
    for sub in record["submissions"]:
        if sub["id"] == sub_id:
            if "inquiries" not in sub:
                sub["inquiries"] = []
            sub["inquiries"].append({
                "id": str(uuid.uuid4()),
                "question": question_text,
                "response": None,
                "timestamp": _get_ist_time()
            })
            sub["status"] = "inquiry" # Update status to indicate pending question
            record["court_log"].append({
                "timestamp": _get_ist_time(),
                "actor": "Judge",
                "action": "Bench Inquiry",
                "details": f"Question issued for Submission {sub_id[:8]}"
            })
            save_case_record(record)
            return sub
    return None

def respond_to_inquiry(sub_id, inquiry_id, response_text):
    record = load_case_record()
    for sub in record["submissions"]:
        if sub["id"] == sub_id:
            for inq in sub.get("inquiries", []):
                if inq["id"] == inquiry_id:
                    inq["response"] = response_text
                    inq["response_timestamp"] = _get_ist_time()
                    # Optionally reset status or keep as inquiry until judge reviews
                    # sub["status"] = "pending" 
                    record["court_log"].append({
                        "timestamp": _get_ist_time(),
                        "actor": sub["sender"],
                        "action": "Responded to Inquiry",
                        "details": f"Response filed for Submission {sub_id[:8]}"
                    })
                    save_case_record(record)
                    return sub
    return None
