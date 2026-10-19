import os
from datetime import timedelta

class Config:
    SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///pijar.db")
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    REMEMBER_COOKIE_HTTPONLY=True
    SESSION_COOKIE_HTTPONLY=True
    SESSION_COOKIE_SAMESITE="Lax"
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8)
    WTF_CSRF_TIME_LIMIT=None
