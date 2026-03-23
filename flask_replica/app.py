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
from models import db, User, Case, Submission, Inquiry, Article, Notice
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
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard/<role>')
@login_required
def dashboard(role):
    if current_user.role != 'admin' and current_user.role != role:
        return redirect(url_for('dashboard', role=current_user.role))
    if role not in ['accuser', 'accused', 'judge', 'admin']:
        return redirect(url_for('index'))
    return render_template('dashboard.html', role=role, user=current_user)

# --- API Endpoints ---

@app.route('/api/public/cases', methods=['GET'])
def get_public_cases():
    cases = Case.query.all()
    return jsonify([{"id": c.id, "title": c.title, "status": c.status} for c in cases])

@app.route('/api/public/court_log', methods=['GET'])
def get_public_court_log():
    case_id = request.args.get('case_id')
    if not case_id: return jsonify([])
    subs = Submission.query.filter_by(case_id=case_id, status='admitted').order_by(Submission.timestamp.asc()).all()
    return jsonify([{
        "id": s.id, "actor": s.sender, "details": s.argument, "timestamp": str(s.timestamp)
    } for s in subs])

@app.route('/api/public/file_case', methods=['POST'])
@login_required
def file_public_case():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    case_type = data.get('case_type', 'standard')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    new_case = Case(
        title=title,
        description=description,
        status='pending_admission',
        case_type=case_type,
        accuser_id=current_user.id  # Bind directly to registered user
    )
    db.session.add(new_case)
    db.session.commit()
    return jsonify({
        "status": "success", 
        "message": "Case filed successfully!",
        "receipt": f"CN-{new_case.id:04d}",
        "case_id": new_case.id
    })


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
            
        case_ref = Case.query.get(case_id)
        sender_role = current_user.role
        if current_user.role == 'user':
            if case_ref and case_ref.accuser_id == current_user.id:
                sender_role = 'accuser'
            elif case_ref and case_ref.accused_id == current_user.id:
                sender_role = 'accused'
            
        sub = Submission(case_id=case_id, sender_role=sender_role, content=text)
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
            if current_user.role == 'user':
                c_ref = Case.query.get(s.case_id)
                is_mine = False
                if c_ref:
                    if s.sender_role == 'accuser' and c_ref.accuser_id == current_user.id:
                        is_mine = True
                    elif s.sender_role == 'accused' and c_ref.accused_id == current_user.id:
                        is_mine = True
                if s.status != 'admitted' and not is_mine:
                    continue

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
    return jsonify([{"id": u.id, "username": u.username, "role": u.role, "approved": u.approved} for u in users])

@app.route('/api/admin/approve_user', methods=['POST'])
@login_required
def admin_approve_user():
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    user_id = data.get('user_id')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    user.approved = True
    db.session.commit()
    return jsonify({"status": "success", "message": f"User approved."})

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
    return jsonify({"status": "success", "message": "Case allocated. Pending judicial review."})

@app.route('/api/judge/admit_case', methods=['POST'])
@login_required
def admit_case():
    if current_user.role != 'judge':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    case_id = data.get('case_id')
    action = data.get('action') # 'active' or 'rejected'
    
    c = Case.query.get(case_id)
    if c and c.judge_id == current_user.id:
        c.status = action
        db.session.commit()
        return jsonify({"status": "success", "message": f"Case updated to {action} successfully."})
    return jsonify({"error": "Invalid authority or case."}), 400

@app.route('/api/cases', methods=['GET'])
@login_required
def get_user_cases():
    if current_user.role == 'admin':
        cases = Case.query.all()
    elif current_user.role == 'judge':
        cases = Case.query.filter_by(judge_id=current_user.id).all()
    else:
        cases = Case.query.filter((Case.accuser_id == current_user.id) | (Case.accused_id == current_user.id)).all()
        
    res = []
    for c in cases:
        j = User.query.get(c.judge_id) if c.judge_id else None
        acc = User.query.get(c.accuser_id) if c.accuser_id else None
        acd = User.query.get(c.accused_id) if c.accused_id else None
        res.append({
            "id": c.id,
            "title": c.title,
            "status": c.status,
            "case_type": c.case_type,
            "public_filer_name": c.public_filer_name,
            "public_filer_contact": c.public_filer_contact,
            "judge": j.username if j else "Unassigned",
            "accuser": acc.username if acc else "Unassigned",
            "accused": acd.username if acd else "Unassigned"
        })
    return jsonify(res)

@app.route('/api/judge/close_case', methods=['POST'])
@login_required
def judge_close_case():
    if current_user.role != 'judge':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    case_id = data.get('case_id')
    result = data.get('result')  # decided, dismissed, rejected
    reason = data.get('reason')

    if not case_id or not result or not reason:
        return jsonify({"error": "Missing parameters"}), 400

    c = Case.query.get(case_id)
    if not c:
        return jsonify({"error": "Case not found"}), 404

    if c.judge_id != current_user.id:
        return jsonify({"error": "Forbidden: Not assigned to this case"}), 403

    c.status = result

    msg = Submission(
        case_id=case_id,
        sender_role='judge',
        content=f"[VERDICT: {result.upper()}] {reason}",
        status='admitted'
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"status": "success", "message": f"Case updated to {result}."})

@app.route('/api/judge/intervene', methods=['POST'])
@login_required
def judge_intervene():
    if current_user.role != 'judge':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    case_id = data.get('case_id')
    content = data.get('content')

    if not case_id or not content:
        return jsonify({"error": "Missing parameters"}), 400

    c = Case.query.get(case_id)
    if not c:
        return jsonify({"error": "Case not found"}), 404

    if c.judge_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    msg = Submission(
        case_id=case_id,
        sender_role='judge',
        content=f"[INTERVENTION] {content}",
        status='admitted'
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"status": "success", "message": "Intervention posted."})

@app.route('/api/judge/post_article', methods=['POST'])
@login_required
def judge_post_article():
    if current_user.role != 'judge':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    image_url = data.get('image_url')

    if not title or not content:
        return jsonify({"error": "Missing title or content"}), 400

    art = Article(
        title=title,
        content=content,
        image_url=image_url,
        judge_id=current_user.id
    )
    db.session.add(art)
    db.session.commit()
    return jsonify({"status": "success", "message": "Article published."})

@app.route('/api/judge/post_notice', methods=['POST'])
@login_required
def judge_post_notice():
    if current_user.role != 'judge':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    importance = data.get('importance', 'standard')

    if not title or not content:
        return jsonify({"error": "Missing title or content"}), 400

    notc = Notice(
        title=title,
        content=content,
        importance=importance,
        judge_id=current_user.id
    )
    db.session.add(notc)
    db.session.commit()
    return jsonify({"status": "success", "message": "Notice issued."})

@app.route('/api/public/content', methods=['GET'])
def get_public_content():
    articles = Article.query.all()
    notices = Notice.query.all()
    
    arts = []
    for a in articles:
        j = User.query.get(a.judge_id)
        arts.append({
            "id": a.id, "title": a.title, "content": a.content,
            "image_url": a.image_url, "judge": j.username if j else "Anonymous"
        })
        
    nots = []
    for n in notices:
        j = User.query.get(n.judge_id)
        nots.append({
            "id": n.id, "title": n.title, "content": n.content,
            "importance": n.importance, "judge": j.username if j else "Anonymous"
        })
    return jsonify({"articles": arts, "notices": nots})

# --- Judge Profile & Interaction Endpoints ---

@app.route('/api/judge/profile', methods=['GET', 'POST'])
@login_required
def manage_judge_profile():
    from models import JudgeProfile
    if request.method == 'POST':
        if current_user.role != 'judge':
            return jsonify({"error": "Forbidden"}), 403
        data = request.get_json()
        
        profile = JudgeProfile.query.filter_by(user_id=current_user.id).first()
        if not profile:
            profile = JudgeProfile(user_id=current_user.id)
            db.session.add(profile)
            
        profile.qualifications = data.get('qualifications', profile.qualifications)
        profile.experience = data.get('experience', profile.experience)
        profile.landmark_judgements = data.get('landmark_judgements', profile.landmark_judgements)
        db.session.commit()
        return jsonify({"status": "success", "message": "Profile updated."})
        
    else: # GET
        judge_id = request.args.get('judge_id', current_user.id)
        user = User.query.get(judge_id)
        if not user or user.role != 'judge':
            return jsonify({"error": "Judge not found"}), 404
            
        profile = JudgeProfile.query.filter_by(user_id=judge_id).first()
        
        # Aggregators
        ongoing = Case.query.filter_by(judge_id=judge_id).filter(Case.status == 'active').count()
        disposed = Case.query.filter_by(judge_id=judge_id).filter(Case.status.in_(['decided', 'dismissed', 'rejected'])).count()
        
        return jsonify({
            "username": user.username,
            "qualifications": profile.qualifications if profile else "",
            "experience": profile.experience if profile else "",
            "landmark_judgements": profile.landmark_judgements if profile else "",
            "ongoing_cases": ongoing,
            "disposed_cases": disposed
        })

@app.route('/api/comment', methods=['POST'])
@login_required
def add_comment():
    from models import Comment
    data = request.get_json()
    article_id = data.get('article_id')
    notice_id = data.get('notice_id')
    content = data.get('content')
    
    if not content:
        return jsonify({"error": "Content required"}), 400
        
    com = Comment(
        user_id=current_user.id,
        article_id=article_id,
        notice_id=notice_id,
        content=content
    )
    db.session.add(com)
    db.session.commit()
    return jsonify({"status": "success", "message": "Comment posted."})

@app.route('/api/public/comments', methods=['GET'])
def get_comments():
    from models import Comment
    article_id = request.args.get('article_id')
    notice_id = request.args.get('notice_id')
    
    query = Comment.query
    if article_id: query = query.filter_by(article_id=article_id)
    if notice_id: query = query.filter_by(notice_id=notice_id)
    
    comments = query.order_by(Comment.timestamp.desc()).all()
    return jsonify([{
        "id": c.id, "user": c.user.username, "content": c.content, "timestamp": str(c.timestamp)
    } for c in comments])


@app.route('/api/admin/change_role', methods=['POST'])
@login_required
def admin_change_role():
    if current_user.role != 'admin':
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json()
    user_id = data.get('user_id')
    new_role = data.get('role')
    
    if new_role not in ['judge', 'accuser', 'accused', 'user']:
        return jsonify({"error": "Invalid role"}), 400
        
    user = User.query.get(user_id)
    if user:
        user.role = new_role
        db.session.commit()
        return jsonify({"status": "success", "message": f"Role updated to {new_role}"})
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            print("Seeding Admin user (admin/admin123)...")
            admin = User(username='admin', role='admin', approved=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True, port=5000)
