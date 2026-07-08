"""
Модель користувача – ОБ'ЄДНАНА ВЕРСІЯ
Включає всі поля з усіх гілок:
- user-auth: базові поля, аутентифікація, валідація
- admin-panel: роль, permissions, деактивація, історія входів
- booking-system: bookings_history
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
    Модель користувача (повна)
    """

    # ===== Ідентифікація =====
    user_id: str = field(default_factory=lambda: f"USR-{uuid.uuid4().hex[:8].upper()}")
    username: str = ""
    email: str = ""
    password_hash: str = ""

    # ===== Особисті дані =====
    full_name: str = ""
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    avatar_url: Optional[str] = None

    # ===== Статуси =====
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False

    # ===== Роль та права (admin-panel) =====
    role: str = "user"  # user, admin, super_admin
    permissions: List[str] = field(default_factory=list)

    # ===== Час =====
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    last_password_change: Optional[datetime] = None
    last_activity: Optional[datetime] = None

    # ===== Налаштування =====
    preferences: Dict[str, Any] = field(default_factory=dict)
    language: str = "uk"
    notifications_enabled: bool = True
    two_factor_enabled: bool = False

    # ===== Історія =====
    bookings_history: List[str] = field(default_factory=list)
    login_history: List[Dict[str, Any]] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)

    # ===== Безпека =====
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

    # ===== Адмін-деактивація =====
    deactivated_by: Optional[str] = None
    deactivated_at: Optional[datetime] = None
    deactivation_reason: Optional[str] = None

    # ============================================================
    #  РОБОТА З ПАРОЛЕМ
    # ============================================================

    @staticmethod
    def hash_password(password: str) -> str:
        salt = hashlib.sha256(password.encode()).digest()
        return base64.b64encode(salt).decode()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return User.hash_password(password) == password_hash

    def set_password(self, password: str):
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            raise ValueError(msg)
        self.password_hash = self.hash_password(password)
        self.last_password_change = datetime.now()

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return self.verify_password(password, self.password_hash)

    # ============================================================
    #  ВАЛІДАЦІЯ
    # ============================================================

    @staticmethod
    def is_valid_username(username: str) -> bool:
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        if not phone:
            return True
        phone = re.sub(r'[\s\-]', '', phone)
        pattern = r'^\+?380\d{9}$|^0\d{9}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_password(password: str) -> tuple:
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

    # ============================================================
    #  АУТЕНТИФІКАЦІЯ
    # ============================================================

    def authenticate(self, password: str) -> bool:
        if not self.is_active:
            return False
        if self.is_locked():
            return False
        if self.check_password(password):
            self.failed_login_attempts = 0
            self.last_login = datetime.now()
            return True
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                self.lock_account()
            return False

    def lock_account(self, duration_minutes: int = 30):
        self.locked_until = datetime.now() + timedelta(minutes=duration_minutes)

    def unlock_account(self):
        self.locked_until = None
        self.failed_login_attempts = 0

    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until

    def add_login_record(self, ip: str, user_agent: str = None):
        self.login_history.append({
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'user_agent': user_agent
        })
        if len(self.login_history) > 100:
            self.login_history = self.login_history[-100:]

    # ============================================================
    #  АДМІН-МЕТОДИ (admin-panel)
    # ============================================================

    def has_permission(self, permission: str) -> bool:
        if self.is_admin:
            return True
        return permission in self.permissions

    def has_role(self, role: str) -> bool:
        if self.role == 'super_admin':
            return True
        return self.role == role

    def deactivate(self, admin_id: str = None, reason: str = None):
        self.is_active = False
        self.deactivated_by = admin_id
        self.deactivated_at = datetime.now()
        self.deactivation_reason = reason

    def activate(self):
        self.is_active = True
        self.deactivated_by = None
        self.deactivated_at = None
        self.deactivation_reason = None

    def add_booking_to_history(self, booking_id: str):
        if booking_id not in self.bookings_history:
            self.bookings_history.append(booking_id)

    # ============================================================
    #  СЕРІАЛІЗАЦІЯ
    # ============================================================

    def to_dict(self, include_sensitive: bool = False) -> dict:
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'birth_date': self.birth_date,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'role': self.role,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_password_change': self.last_password_change.isoformat() if self.last_password_change else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'preferences': self.preferences,
            'language': self.language,
            'notifications_enabled': self.notifications_enabled,
            'two_factor_enabled': self.two_factor_enabled,
            'bookings_history': self.bookings_history,
            'failed_login_attempts': self.failed_login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'deactivated_by': self.deactivated_by,
            'deactivated_at': self.deactivated_at.isoformat() if self.deactivated_at else None,
            'deactivation_reason': self.deactivation_reason
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        created_at = None
        last_login = None
        last_password_change = None
        last_activity = None
        locked_until = None
        deactivated_at = None

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
        if data.get('last_password_change'):
            try:
                last_password_change = datetime.fromisoformat(data['last_password_change'])
            except (ValueError, TypeError):
                pass
        if data.get('last_activity'):
            try:
                last_activity = datetime.fromisoformat(data['last_activity'])
            except (ValueError, TypeError):
                pass
        if data.get('locked_until'):
            try:
                locked_until = datetime.fromisoformat(data['locked_until'])
            except (ValueError, TypeError):
                pass
        if data.get('deactivated_at'):
            try:
                deactivated_at = datetime.fromisoformat(data['deactivated_at'])
            except (ValueError, TypeError):
                pass

        return cls(
            user_id=data.get('user_id', f"USR-{uuid.uuid4().hex[:8].upper()}"),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            full_name=data.get('full_name', ''),
            phone=data.get('phone'),
            birth_date=data.get('birth_date'),
            avatar_url=data.get('avatar_url'),
            is_active=bool(data.get('is_active', True)),
            is_admin=bool(data.get('is_admin', False)),
            is_verified=bool(data.get('is_verified', False)),
            role=data.get('role', 'user'),
            permissions=data.get('permissions', []),
            created_at=created_at or datetime.now(),
            last_login=last_login,
            last_password_change=last_password_change,
            last_activity=last_activity,
            preferences=data.get('preferences', {}),
            language=data.get('language', 'uk'),
            notifications_enabled=bool(data.get('notifications_enabled', True)),
            two_factor_enabled=bool(data.get('two_factor_enabled', False)),
            bookings_history=data.get('bookings_history', []),
            login_history=data.get('login_history', []),
            ip_addresses=data.get('ip_addresses', []),
            failed_login_attempts=int(data.get('failed_login_attempts', 0)),
            locked_until=locked_until,
            deactivated_by=data.get('deactivated_by'),
            deactivated_at=deactivated_at,
            deactivation_reason=data.get('deactivation_reason')
        )

    # ============================================================
    #  ДОПОМІЖНІ МЕТОДИ
    # ============================================================

    def get_full_name(self) -> str:
        return self.full_name or self.username

    def get_short_name(self) -> str:
        if self.full_name:
            return self.full_name.split()[0]
        return self.username

    def get_age(self) -> Optional[int]:
        if not self.birth_date:
            return None
        try:
            birth = datetime.strptime(self.birth_date, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - birth.year
            if (today.month, today.day) < (birth.month, birth.day):
                age -= 1
            return age
        except ValueError:
            return None

    def get_role_ukrainian(self) -> str:
        role_map = {
            'user': 'Користувач',
            'admin': 'Адміністратор',
            'super_admin': 'Супер-адміністратор'
        }
        return role_map.get(self.role, 'Користувач')

    def get_language_name(self) -> str:
        language_map = {
            'uk': 'Українська',
            'en': 'English',
            'ru': 'Русский'
        }
        return language_map.get(self.language, 'Українська')

    def is_profile_complete(self) -> bool:
        required = [self.email, self.full_name, self.phone]
        return all(required) and self.is_verified

    def __str__(self) -> str:
        return f"User({self.username}, {self.email})"
