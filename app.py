"""
STRATEGIC CAREER ADVANCEMENT PLATFORM AND RESUME SYNTHESIZER (SCAP)
Main Flask Application Factory & Server Entrypoint.
"""
import os
import secrets
from flask import Flask, render_template, session, redirect, url_for, request
from config import Config
from database import db

# Import Blueprints
from routes.auth import auth_bp
from routes.user import user_bp
from routes.resume import resume_bp
from routes.admin import admin_bp
from routes.assessments import assessments_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Database Schema & Seed Data
    with app.app_context():
        try:
            db.init_db()
        except Exception as e:
            app.logger.error(f"Error during database initialization: {e}")

    # Register Modular Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(assessments_bp)

    # Global Context Processor
    @app.context_processor
    def inject_global_data():
        # Inject CSRF token if not present
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)

        db_status = "Oracle Database 21c (Connected)" if db.engine_type == "oracle" else "SQLite (Local Evaluation Fallback)"
        return {
            "current_user_name": session.get('full_name'),
            "current_user_role": session.get('role'),
            "is_logged_in": 'user_id' in session,
            "db_engine_name": db_status,
            "csrf_token": session.get('csrf_token')
        }

    # Public Landing Page Route
    @app.route('/')
    def index():
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        return render_template('index.html')

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', code=404, message="The requested career resource could not be found."), 404

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('error.html', code=413, message="Resume file size exceeds the 16MB limit. Please upload a smaller file."), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', code=500, message="An internal platform error occurred. Our engineers have been alerted."), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    print(f"\n========================================================")
    print(f"  STRATEGIC CAREER ADVANCEMENT PLATFORM (SCAP) ACTIVE")
    print(f"  Database Engine: {db.engine_type.upper()}")
    print(f"  Access URL:      http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)

