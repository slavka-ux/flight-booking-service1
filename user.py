"""
Модель користувача
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
import hashlib
import base64
import re


@dataclass
class User:
    """
    Модель користувача системи
    """
    user_id: str = field(default_factory=lambda: f"USR-{uuid.uuid4().hex[:8].upper()}")
    username: str = ""
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    phone: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False
    preferences: Dict[str, Any] = field(default_factory=dict)
    bookings_history: List[str] = field(default_factory=list)

    @staticmethod
    def hash_password(password: str) -> str:
        """Хешує пароль за допомогою SHA-256 + Base64"""
        salt = hashlib.sha256(password.encode()).digest()
        return base64.b64encode(salt).decode()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Перевіряє пароль на відповідність хешу"""
        return User.hash_password(password) == password_hash

    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Перевіряє чи валідне ім'я користувача (3-30 символів, літери, цифри, _)"""
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Перевіряє чи валідний email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Перевіряє чи валідний телефон (український формат)"""
        if not phone:
            return True  # телефон не обов'язковий
        phone = re.sub(r'[\s\-]', '', phone)
        pattern = r'^\+?380\d{9}$|^0\d{9}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_password(password: str) -> tuple:
        """
        Валідує пароль за вимогами безпеки
        Повертає (чи валідний, повідомлення)
        """
        if len(password) < 8:
            return False, "Пароль має містити не менше 8 символів"
        if not re.search(r'[A-Z]', password):
            return False, "Пароль має містити хоча б одну велику літеру"
        if not re.search(r'[a-z]', password):
            return False, "Пароль має містити хоча б одну маленьку літеру"
        if not re.search(r'\d', password):
            return False, "Пароль має містити хоча б одну цифру"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Пароль має містити хоча б один спеціальний символ"
        return True, "OK"

    def set_password(self, password: str):
        """Встановлює новий пароль (з валідацією)"""
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            raise ValueError(msg)
        self.password_hash = self.hash_password(password)

    def check_password(self, password: str) -> bool:
        """Перевіряє пароль"""
        if not self.password_hash:
            return False
        return self.verify_password(password, self.password_hash)

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Конвертує в словник для JSON"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'preferences': self.preferences,
            'bookings_history': self.bookings_history
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Створює користувача зі словника"""
        created_at = None
        last_login = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                pass
        if data.get('last_login'):
            try:
                last_login = datetime.fromisoformat(data['last_login'])
            except (ValueError, TypeError):
                pass

        return cls(
            user_id=data.get('user_id', f"USR-{uuid.uuid4().hex[:8].upper()}"),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            full_name=data.get('full_name', ''),
            phone=data.get('phone'),
            created_at=created_at or datetime.now(),
            last_login=last_login,
            is_active=bool(data.get('is_active', True)),
            is_admin=bool(data.get('is_admin', False)),
            is_verified=bool(data.get('is_verified', False)),
            preferences=data.get('preferences', {}),
            bookings_history=data.get('bookings_history', [])
        )

    def get_full_name(self) -> str:
        return self.full_name or self.username

    def add_booking_to_history(self, booking_id: str):
        if booking_id not in self.bookings_history:
            self.bookings_history.append(booking_id)

    def __str__(self) -> str:
        return f"User({self.username}, {self.email})"
