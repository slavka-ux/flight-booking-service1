"""
Допоміжні функції для аутентифікації
"""

import jwt
import datetime
import hashlib
import base64
import uuid
from typing import Optional, Dict, Any


def generate_token(user_id: str, username: str, is_admin: bool,
                   secret_key: str, expires_in: int = 3600) -> str:
    """
    Генерує JWT токен для користувача
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')


def decode_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """
    Декодує JWT токен, повертає payload або None при помилці
    """
    try:
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_password(password: str) -> str:
    """Хешує пароль (SHA-256 + Base64)"""
    salt = hashlib.sha256(password.encode()).digest()
    return base64.b64encode(salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Перевіряє пароль на відповідність хешу"""
    return hash_password(password) == password_hash


def generate_user_id() -> str:
    """Генерує унікальний ID користувача"""
    return f"USR-{uuid.uuid4().hex[:8].upper()}"


def generate_confirmation_code() -> str:
    """Генерує код підтвердження (наприклад, для email)"""
    return uuid.uuid4().hex[:8].upper()


def mask_email(email: str) -> str:
    """Маскує email (наприклад, i***n@example.com)"""
    if not email:
        return ''
    local, domain = email.split('@')
    if len(local) <= 2:
        return email
    masked = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked}@{domain}"


def get_current_timestamp() -> str:
    """Повертає поточну дату-час у ISO форматі"""
    return datetime.datetime.now().isoformat()
