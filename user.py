"""
Модель користувача з адмін-функціями
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
    user_id: str = field(default_factory=lambda: f"USR-{uuid.uuid4().hex[:8].upper()}")
    username: str = ""
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False
    preferences: Dict[str, Any] = field(default_factory=dict)
    bookings_history: List[str] = field(default_factory=list)
    avatar_url: Optional[str] = None
    language: str = "uk"
    notifications_enabled: bool = True
    two_factor_enabled: bool = False
    last_password_change: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    # Адмін-поля
    role: str = "user"  # user, admin, super_admin
    permissions: List[str] = field(default_factory=list)
    last_activity: Optional[datetime] = None
    ip_addresses: List[str] = field(default_factory=list)
    login_history: List[Dict[str, Any]] = field(default_factory=list)
    deactivated_by: Optional[str] = None
    deactivated_at: Optional[datetime] = None
    deactivation_reason: Optional[str] = None
    
    @staticmethod
    def hash_password(password: str) -> str:
        salt = hashlib.sha256(password.encode()).digest()
        return base64.b64encode(salt).decode()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return User.hash_password(password) == password_hash
    
    def set_password(self, password: str):
        self.password_hash = self.hash_password(password)
        self.last_password_change = datetime.now()
    
    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return self.verify_password(password, self.password_hash)
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'birth_date': self.birth_date,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'preferences': self.preferences,
            'bookings_history': self.bookings_history,
            'avatar_url': self.avatar_url,
            'language': self.language,
            'notifications_enabled': self.notifications_enabled,
            'two_factor_enabled': self.two_factor_enabled,
            'last_password_change': self.last_password_change.isoformat() if self.last_password_change else None,
            'failed_login_attempts': self.failed_login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'role': self.role,
            'permissions': self.permissions,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
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
        locked_until = None
        last_activity = None
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
        
        if data.get('locked_until'):
            try:
                locked_until = datetime.fromisoformat(data['locked_until'])
            except (ValueError, TypeError):
                pass
        
        if data.get('last_activity'):
            try:
                last_activity = datetime.fromisoformat(data['last_activity'])
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
            created_at=created_at or datetime.now(),
            last_login=last_login,
            is_active=bool(data.get('is_active', True)),
            is_admin=bool(data.get('is_admin', False)),
            is_verified=bool(data.get('is_verified', False)),
            preferences=data.get('preferences', {}),
            bookings_history=data.get('bookings_history', []),
            avatar_url=data.get('avatar_url'),
            language=data.get('language', 'uk'),
            notifications_enabled=bool(data.get('notifications_enabled', True)),
            two_factor_enabled=bool(data.get('two_factor_enabled', False)),
            last_password_change=last_password_change,
            failed_login_attempts=int(data.get('failed_login_attempts', 0)),
            locked_until=locked_until,
            role=data.get('role', 'user'),
            permissions=data.get('permissions', []),
            last_activity=last_activity,
            ip_addresses=data.get('ip_addresses', []),
            login_history=data.get('login_history', []),
            deactivated_by=data.get('deactivated_by'),
            deactivated_at=deactivated_at,
            deactivation_reason=data.get('deactivation_reason')
        )
    
    def has_permission(self, permission: str) -> bool:
        """Перевірка наявності дозволу"""
        if self.is_admin:
            return True
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """Перевірка ролі"""
        if self.role == 'super_admin':
            return True
        return self.role == role
    
    def deactivate(self, admin_id: str = None, reason: str = None):
        """Деактивація користувача"""
        self.is_active = False
        self.deactivated_by = admin_id
        self.deactivated_at = datetime.now()
        self.deactivation_reason = reason
    
    def activate(self):
        """Активація користувача"""
        self.is_active = True
        self.deactivated_by = None
        self.deactivated_at = None
        self.deactivation_reason = None
    
    def add_login_record(self, ip: str, user_agent: str = None):
        """Додати запис про вхід"""
        self.login_history.append({
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'user_agent': user_agent
        })
        if len(self.login_history) > 100:
            self.login_history = self.login_history[-100:]
    
    def get_role_ukrainian(self) -> str:
        role_map = {
            'user': 'Користувач',
            'admin': 'Адміністратор',
            'super_admin': 'Супер-адміністратор'
        }
        return role_map.get(self.role, 'Користувач')
