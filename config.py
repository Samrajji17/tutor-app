"""Application configuration. Everything sensitive comes from environment variables."""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
try:
    (BASE_DIR / "instance").mkdir(exist_ok=True)
except OSError:
    pass


def env_bool(name, default=False):
    return os.environ.get(name, str(int(default))).strip().lower() in {"1", "true", "yes", "on"}


def _database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return f"sqlite:///{BASE_DIR / 'instance' / 'tuition.db'}"
    # Some hosts still hand out the old scheme that SQLAlchemy rejects.
    return url.replace("postgres://", "postgresql://", 1) if url.startswith("postgres://") else url


class Config:
    SECRET_KEY_FROM_ENV = bool(os.environ.get("SECRET_KEY"))
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = env_bool("FLASK_DEBUG")

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = env_bool("COOKIE_SECURE")
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 4  # admin session: 4 hours
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 4
    SEND_FILE_MAX_AGE_DEFAULT = 60 * 60 * 24 * 7
    MAX_CONTENT_LENGTH = 64 * 1024

    TRUST_PROXY = env_bool("TRUST_PROXY")
    BASE_URL = os.environ.get("BASE_URL", "").strip()
    TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")
    REFERENCE_PREFIX = os.environ.get("REFERENCE_PREFIX", "TUT")

    # Admin behaviour
    ADMIN_PER_PAGE = 20
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    # Spam protection
    MIN_FORM_SECONDS = 3  # forms submitted faster than this are treated as bots
    FORM_RATE_LIMIT = (10, 3600)  # (submissions, seconds) per IP

    # Email (optional)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "").strip()
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587") or 587)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "").strip()
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", True)
    MAIL_USE_SSL = env_bool("MAIL_USE_SSL", False)
    MAIL_SENDER = os.environ.get("MAIL_SENDER", "").strip()
    NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "").strip()
    MAIL_ASYNC = not os.environ.get("VERCEL")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    MIN_FORM_SECONDS = 0
    MAIL_ASYNC = False
    SERVER_NAME = None
