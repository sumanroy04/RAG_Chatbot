import os
import json
from pathlib import Path

# Base Directory path (relative to this file)
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Read .env if dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv(BACKEND_DIR / ".env")
except ImportError:
    pass

# Read config.json fallback
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip() or os.environ.get("Api_key", "").strip()
if not GROQ_API_KEY:
    config_path = BACKEND_DIR / "config" / "config.json"
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                config_data = json.load(f)
            GROQ_API_KEY = config_data.get("GROQ_API_KEY", "").strip()
        except Exception:
            pass

# Database config
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BACKEND_DIR}/mental_health.db")

# Paths for RAG files
DATA_DIR = PROJECT_ROOT / "data-storage" / "data"
VECTOR_DB_DIR = PROJECT_ROOT / "data-storage" / "vector_db_dir"
IMAGES_DIR = PROJECT_ROOT / "data-storage" / "images"

# Security
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-key-change-in-prod")
