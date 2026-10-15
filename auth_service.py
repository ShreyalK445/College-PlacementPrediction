"""
Authentication & Authorization Service — JWT & RBAC
Handles token issuance, validation, password hashing, and route decorators.
"""

from functools import wraps
import os
from datetime import datetime, timedelta, timezone
import jwt
from flask import request, jsonify, g
from models import get_db_session, User

SECRET_KEY = os.environ.get("SECRET_KEY", "career-intel-jwt-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def generate_token(user: User) -> str:
    """Generate a signed JWT token for the user."""
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.full_name,
        "role": user.role,
        "dept": user.department,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])

def get_current_user():
    """Extract authenticated user from request Authorization header or return None."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:].strip()
    try:
        payload = decode_token(token)
        session = get_db_session()
        user = session.query(User).filter_by(id=int(payload["sub"])).first()
        return user
    except Exception:
        return None

def require_jwt_auth(optional=False):
    """Decorator to require valid JWT authentication."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user and not optional:
                return jsonify({"error": "Authentication required. Please provide a valid Bearer token."}), 401
            g.current_user = user
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_role(*roles):
    """Decorator to enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"error": "Authentication required"}), 401
            if user.role not in roles and "admin" not in roles and user.role != "admin":
                return jsonify({
                    "error": f"Forbidden — requires one of roles: {', '.join(roles)}"
                }), 403
            g.current_user = user
            return f(*args, **kwargs)
        return decorated
    return decorator

def seed_default_users():
    """Seeds demo accounts (Student, Mentor, TPO Admin) if users table is empty."""
    session = get_db_session()
    if session.query(User).count() == 0:
        demo_accounts = [
            ("student@college.edu", "Student@123", "Alex Morgan", "student", "Computer Science"),
            ("mentor@college.edu", "Mentor@123", "Dr. Priya Sharma", "mentor", "Information Technology"),
            ("tpo@college.edu", "TpoAdmin@123", "Prof. R. Verma", "tpo", "Placement Cell"),
        ]
        for email, pwd, name, role, dept in demo_accounts:
            u = User(email=email, full_name=name, role=role, department=dept)
            u.set_password(pwd)
            session.add(u)
        session.commit()
