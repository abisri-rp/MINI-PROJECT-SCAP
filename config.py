import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "scap-career-advancement-super-secret-key-2026")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/tmp/scap_uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    
    # Database Configuration
    # DB_ENGINE can be "oracle" or "sqlite" (or "auto" which tries Oracle, then falls back to SQLite)
    DB_ENGINE = os.getenv("DB_ENGINE", "auto")
    
    # Oracle Database Settings
    ORACLE_USER = os.getenv("ORACLE_USER", "system")
    ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "oracle")
    ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
    ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
    ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "XEPDB1") # or XE
    ORACLE_DSN = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"
    
    # SQLite Fallback Settings
    SQLITE_PATH = BASE_DIR / "scap_database.db"
    
    # ML Models Folder
    ML_MODEL_DIR = BASE_DIR / "ml" / "models"
    DATASET_DIR = BASE_DIR / "ml" / "dataset"
    
    # Admin Seed Credentials
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@scap.edu")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@SCAP2026")
    ADMIN_NAME = os.getenv("ADMIN_NAME", "Platform Administrator")

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.ML_MODEL_DIR, exist_ok=True)
os.makedirs(Config.DATASET_DIR, exist_ok=True)
