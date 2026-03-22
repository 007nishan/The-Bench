from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

import rag_engine
import case_manager

app = Flask(__name__)
CORS(app)

# --- Routes for Pages ---

@app.route('/')
def index():
    """Render the Login page."""
    return render_template('login.html')

@app.route('/<role>')
def dashboard(role):
    """Render the Dashboard for a specific role."""
    if role not in ['accuser', 'accused', 'judge']:
        return redirect(url_for('index'))
    return render_template('dashboard.html', role=role)

# --- API Endpoints ---

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "message": "The Bench Flask is Active"})

@app.route('/api/chat/strategy', methods=['POST'])
def strategy_chat():
    try:
        data = request.get_json()
        role = data.get('user_role')
        query = data.get('query_text')
        
        if not role or not query:
            return jsonify({"error": "Missing role or query"}), 400
            
        raw_response = rag_engine.generate_strategic_response(role, query)
        
        # Parse for [ARGUMENT] and [WARNING]
        argument = ""
        warning = ""
        
        if "[ARGUMENT]" in raw_response:
            parts = raw_response.split("[WARNING]")
            arg_part = parts[0].replace("[ARGUMENT]", "").strip()
            warn_part = parts[1].strip() if len(parts) > 1 else ""
            argument = arg_part
            warning = warn_part
        else:
            # Fallback if structure is missing
            argument = raw_response
            warning = "Strategist issued no warnings for this query."
            
        return jsonify({
            "argument": argument,
            "warning": warning
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/submit_argument', methods=['POST'])
def submit_argument():
    try:
        data = request.get_json()
        role = data.get('user_role')
        text = data.get('argument_text')
        references = data.get('evidence_ids', []) # List of strings/ids
        
        if not role or not text:
            return jsonify({"error": "Missing role or argument text"}), 400
            
        sub = case_manager.submit_argument(role, text, references)
        return jsonify({
            "status": "success",
            "submission_id": sub["id"],
            "message": "Argument filed with The Bench."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/judge/pending', methods=['GET'])
def get_pending():
    try:
        # Return ALL submissions for the timeline view, or use filtering
        record = case_manager.load_case_record()
        return jsonify(record.get("submissions", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/court_log', methods=['GET'])
def get_court_log():
    try:
        return jsonify(case_manager.get_court_log())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/judge/inquiry', methods=['POST'])
def add_inquiry():
    try:
        data = request.get_json()
        sub_id = data.get('submission_id')
        question = data.get('question_text')
        
        if not sub_id or not question:
            return jsonify({"error": "Missing submission_id or question"}), 400
            
        sub = case_manager.add_inquiry(sub_id, question)
        if sub:
            return jsonify({"status": "success", "message": "Inquiry issued."})
        return jsonify({"error": "Submission not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/judge/respond_inquiry', methods=['POST'])
def respond_inquiry():
    try:
        data = request.get_json()
        sub_id = data.get('submission_id')
        inq_id = data.get('inquiry_id')
        response_text = data.get('response_text')
        
        if not all([sub_id, inq_id, response_text]):
            return jsonify({"error": "Missing fields"}), 400
            
        sub = case_manager.respond_to_inquiry(sub_id, inq_id, response_text)
        if sub:
            return jsonify({"status": "success", "message": "Response filed."})
        return jsonify({"error": "Submission or Inquiry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/judge/verify', methods=['POST'])
def verify_submission():
    try:
        data = request.get_json()
        sub_id = data.get('submission_id')
        status = data.get('status') # 'admitted' or 'rejected'
        notes = data.get('notes', '')
        
        if not sub_id or not status:
            return jsonify({"error": "Missing submission_id or status"}), 400
            
        sub = case_manager.update_submission_status(sub_id, status, ai_notes=notes)
        if sub:
            return jsonify({"status": "success", "message": f"Verdict: {status}"})
        return jsonify({"error": "Submission not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_doc', methods=['POST'])
def upload_doc():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        user_role = request.form.get('user_role')
        dest = request.form.get('destination', 'private') # 'private' or 'common'
        
        if not user_role:
            return jsonify({"error": "user_role is required"}), 400
            
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        content = file.read().decode('utf-8')
        
        role_to_store = user_role if dest == 'private' else 'common'
        
        rag_engine.store_document(role_to_store, filename, content)
        
        return jsonify({"status": "success", "message": f"Uploaded to {dest} vault."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
