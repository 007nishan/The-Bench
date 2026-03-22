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
from models import db, User, Case, Submission, Inquiry
from auth import auth_bp
from flask_login import LoginManager, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///the_bench.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'index'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)

# --- Routes for Pages ---

@app.route('/')
def index():
    """Render the Login page."""
    return render_template('login.html')

@app.route('/<role>')
@login_required
def dashboard(role):
    """Render the Dashboard for a specific role."""
    # Allow admins to view any dashboard, otherwise match role
    if current_user.role != 'admin' and current_user.role != role:
        return redirect(url_for('dashboard', role=current_user.role))
        
    if role not in ['accuser', 'accused', 'judge', 'admin']:
        return redirect(url_for('index'))
    return render_template('dashboard.html', role=role, user=current_user)

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
@login_required
def submit_argument():
    try:
        data = request.get_json()
        case_id = data.get('case_id')
        text = data.get('argument_text')
        
        if not case_id or not text:
            return jsonify({"error": "Missing case_id or argument text"}), 400
            
        sub = Submission(case_id=case_id, sender_role=current_user.role, content=text)
        db.session.add(sub)
        db.session.commit()
        return jsonify({
            "status": "success",
            "submission_id": sub.id,
            "message": "Argument filed with The Bench."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/judge/pending', methods=['GET'])
@login_required
def get_pending():
    try:
        case_id = request.args.get('case_id')
        query = Submission.query
        if case_id:
            query = query.filter_by(case_id=case_id)
        subs = query.order_by(Submission.timestamp.desc()).all()
        
        res = []
        for s in subs:
            res.append({
                "id": s.id,
                "sender": s.sender_role,
                "argument": s.content,
                "status": s.status,
                "timestamp": str(s.timestamp)
            })
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/court_log', methods=['GET'])
def get_court_log():
    try:
        case_id = request.args.get('case_id')
        query = Submission.query.filter_by(status='admitted')
        if case_id:
            query = query.filter_by(case_id=case_id)
        subs = query.order_by(Submission.timestamp.asc()).all()
        
        res = []
        for s in subs:
            res.append({
                "timestamp": str(s.timestamp),
                "actor": s.sender_role,
                "action": "Argument Admitted",
                "details": s.content[:100] + "..." if len(s.content) > 100 else s.content
            })
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/judge/inquiry', methods=['POST'])
@login_required
def add_inquiry():
    try:
        data = request.get_json()
        sub_id = data.get('submission_id')
        question = data.get('question_text')
        
        if not sub_id or not question:
            return jsonify({"error": "Missing submission_id or question"}), 400
            
        inq = Inquiry(submission_id=sub_id, judge_id=current_user.id, question=question)
        db.session.add(inq)
        db.session.commit()
        return jsonify({"status": "success", "message": "Inquiry issued."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/judge/respond_inquiry', methods=['POST'])
@login_required
def respond_inquiry():
    try:
        data = request.get_json()
        inq_id = data.get('inquiry_id')
        response_text = data.get('response_text')
        
        if not inq_id or not response_text:
            return jsonify({"error": "Missing fields"}), 400
            
        inq = Inquiry.query.get(inq_id)
        if inq:
            inq.response = response_text
            inq.respondent_role = current_user.role
            db.session.commit()
            return jsonify({"status": "success", "message": "Response filed."})
        return jsonify({"error": "Inquiry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/judge/verify', methods=['POST'])
@login_required
def verify_submission():
    try:
        data = request.get_json()
        sub_id = data.get('submission_id')
        status = data.get('status') # 'admitted' or 'rejected'
        
        if not sub_id or not status:
            return jsonify({"error": "Missing submission_id or status"}), 400
            
        sub = Submission.query.get(sub_id)
        if sub:
            sub.status = status
            db.session.commit()
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

@app.route('/api/admin/cases', methods=['GET'])
@login_required
def admin_get_cases():
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    cases = Case.query.all()
    res = []
    for c in cases:
        j = User.query.get(c.judge_id) if c.judge_id else None
        acc = User.query.get(c.accuser_id) if c.accuser_id else None
        acd = User.query.get(c.accused_id) if c.accused_id else None
        res.append({
            "id": c.id,
            "title": c.title,
            "status": c.status,
            "judge": j.username if j else "Unassigned",
            "accuser": acc.username if acc else "Unassigned",
            "accused": acd.username if acd else "Unassigned"
        })
    return jsonify(res)

@app.route('/api/admin/users', methods=['GET'])
@login_required
def admin_get_users():
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    users = User.query.filter(User.role != 'admin').all()
    return jsonify([{"id": u.id, "username": u.username, "role": u.role} for u in users])

@app.route('/api/admin/create_case', methods=['POST'])
@login_required
def admin_create_case():
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    title = data.get('title')
    desc = data.get('description')
    if not title:
        return jsonify({"error": "Title required"}), 400
    c = Case(title=title, description=desc)
    db.session.add(c)
    db.session.commit()
    return jsonify({"status": "success", "case_id": c.id, "message": "Case created."})

@app.route('/api/admin/allocate_case', methods=['POST'])
@login_required
def admin_allocate_case():
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    case_id = data.get('case_id')
    judge_id = data.get('judge_id')
    accuser_id = data.get('accuser_id')
    accused_id = data.get('accused_id')
    
    c = Case.query.get(case_id)
    if not c:
        return jsonify({"error": "Case not found"}), 404
        
    if judge_id: c.judge_id = judge_id
    if accuser_id: c.accuser_id = accuser_id
    if accused_id: c.accused_id = accused_id
    
    db.session.commit()
    return jsonify({"status": "success", "message": "Case allocated successfully."})

@app.route('/api/cases', methods=['GET'])
@login_required
def get_user_cases():
    if current_user.role == 'admin':
        # Admin can see all, but endpoint usually for regular dashboards
        cases = Case.query.all()
    elif current_user.role == 'judge':
        cases = Case.query.filter_by(judge_id=current_user.id).all()
    elif current_user.role == 'accuser':
        cases = Case.query.filter_by(accuser_id=current_user.id).all()
    else:
        cases = Case.query.filter_by(accused_id=current_user.id).all()
        
    return jsonify([{"id": c.id, "title": c.title, "status": c.status} for c in cases])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
