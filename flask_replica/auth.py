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
