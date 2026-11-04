"""
Authentication & Authorization Routes.
Handles user registration, password hashing, secure session management,
and role-based access control protecting User and Admin portals.
"""
import re
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Administrator login required.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') != 'admin':
            flash("Access denied. Administrator privileges required.", "danger")
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard' if session.get('role') == 'admin' else 'user.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not full_name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html', full_name=full_name, email=email)

        # Email regex
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash("Please enter a valid email address.", "danger")
            return render_template('register.html', full_name=full_name, email=email)

        # Password length and confirmation
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', full_name=full_name, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', full_name=full_name, email=email)

        # Check existing email
        existing = db.get_user_by_email(email)
        if existing:
            flash("An account with this email address already exists. Please log in.", "warning")
            return redirect(url_for('auth.login'))

        # Secure password hashing (scrypt / pbkdf2)
        pwd_hash = generate_password_hash(password)

        # Public registrations are strictly created with role="user"
        user_id = db.create_user(full_name, email, pwd_hash, role="user")

        # Set session
        session['user_id'] = user_id
        session['full_name'] = full_name
        session['email'] = email
        session['role'] = 'user'

        flash(f"Welcome to SCAP, {full_name}! Your account has been created.", "success")
        return redirect(url_for('user.dashboard'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard' if session.get('role') == 'admin' else 'user.dashboard'))

    email_error = None
    password_error = None

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        has_error = False

        # Email field validation
        if not email:
            email_error = "Email field is required. Please enter your email."
            has_error = True
        elif not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            email_error = "Invalid email address format (e.g., student@scap.edu)."
            has_error = True

        # Password field validation
        if not password:
            password_error = "Password field is required. Please enter your password."
            has_error = True
        elif len(password) < 6:
            password_error = "Password must be at least 6 characters."
            has_error = True

        if has_error:
            if email_error:
                flash(email_error, "danger")
            if password_error:
                flash(password_error, "danger")
            return render_template('login.html', email=email, email_error=email_error, password_error=password_error)

        # Check if user is registered
        user = db.get_user_by_email(email)
        if not user:
            flash("User not registered", "danger")
            return render_template('login.html', email=email, email_error="User not registered")

        # Check password correctness
        if not check_password_hash(user['password_hash'], password):
            flash("Invalid password for this account. Please try again.", "danger")
            return render_template('login.html', email=email, password_error="Invalid password for this account.")

        # Establish session
        session['user_id'] = user['user_id']
        session['full_name'] = user['full_name']
        session['email'] = user['email']
        session['role'] = user['role']

        flash(f"Welcome back, {user['full_name']}!", "success")
        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('login.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        email_error = None
        password_error = None
        confirm_error = None
        has_error = False

        if not email:
            email_error = "Email address is required."
            has_error = True
        elif not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            email_error = "Invalid email format."
            has_error = True

        if not new_password:
            password_error = "New password is required."
            has_error = True
        elif len(new_password) < 6:
            password_error = "Password must be at least 6 characters long."
            has_error = True

        if not confirm_password:
            confirm_error = "Please confirm your new password."
            has_error = True
        elif new_password != confirm_password:
            confirm_error = "Passwords do not match."
            has_error = True

        if has_error:
            if email_error:
                flash(email_error, "danger")
            if password_error:
                flash(password_error, "danger")
            if confirm_error:
                flash(confirm_error, "danger")
            return render_template(
                'forgot_password.html',
                email=email,
                email_error=email_error,
                password_error=password_error,
                confirm_error=confirm_error
            )

        # Check if user exists in the database
        user = db.get_user_by_email(email)
        if not user:
            flash("User not registered", "danger")
            return render_template('forgot_password.html', email=email, email_error="User not registered")

        # Update user password in database
        new_hash = generate_password_hash(new_password)
        db.update_user_password(email, new_hash)

        flash("Password updated successfully. Please log in with your new password.", "success")
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for('auth.login'))
