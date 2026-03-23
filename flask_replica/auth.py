from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login_submit', methods=['POST'])
def login_submit():
    # Handle form or JSON
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        if not user.approved:
            msg = "Please ask your admin to approve you before you start using this platform."
            if request.is_json:
                return jsonify({"error": msg}), 403
            flash(msg)
            return redirect(url_for('index'))
            
        login_user(user)
        if request.is_json:
            return jsonify({"status": "success", "role": user.role})
        return redirect(url_for('dashboard', role=user.role))
    
    if request.is_json:
        return jsonify({"error": "Invalid credentials"}), 401
    flash("Invalid credentials")
    return redirect(url_for('index'))

@auth_bp.route('/api/current_user', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            "is_authenticated": True,
            "username": current_user.username,
            "role": current_user.role
        })
    return jsonify({"is_authenticated": False})

@auth_bp.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

    if not username or not password:
        if request.is_json: return jsonify({"error": "Missing fields"}), 400
        flash("All fields are required.")
        return redirect(url_for('index'))

    if User.query.filter_by(username=username).first():
        if request.is_json: return jsonify({"error": "Username taken"}), 400
        flash("Username already exists.")
        return redirect(url_for('index'))

    role = 'user' # Force standard user role for public registrations
    new_user = User(username=username, role=role, approved=False)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    if request.is_json:
        return jsonify({"status": "success", "message": "Registered! Awaiting Admin Approval."})
    flash("Registered! Awaiting Admin Approval.")
    return redirect(url_for('index'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('index'))
