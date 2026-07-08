"""
Сервіс для роботи з користувачами (оновлений з адмін-функціями)
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from src.models.user import User
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Сервіс управління користувачами з адмін-функціями"""
    
    def __init__(self):
        self.users: List[User] = []
        self._load_users()
    
    def _load_users(self):
        data = Config.get_users()
        self.users = [User.from_dict(item) for item in data]
        logger.info(f"Завантажено {len(self.users)} користувачів")
    
    def _save_users(self):
        data = [u.to_dict() for u in self.users]
        Config.save_data(Config.USERS_FILE, data)
        logger.info(f"Збережено {len(self.users)} користувачів")
    
    def register_user(self, username: str, email: str, password: str, 
                      full_name: str = '', phone: str = '') -> User:
        if self.get_user_by_username(username):
            raise ValueError(f"Користувач з іменем '{username}' вже існує")
        
        if self.get_user_by_email(email):
            raise ValueError(f"Користувач з email '{email}' вже існує")
        
        user = User(
            username=username,
            email=email,
            full_name=full_name or username,
            phone=phone
        )
        user.set_password(password)
        
        self.users.append(user)
        self._save_users()
        
        logger.info(f"Зареєстровано нового користувача: {username}")
        return user
    
    def authenticate_user(self, username: str, password: str, 
                          ip: str = None, user_agent: str = None) -> Optional[User]:
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            user.last_login = datetime.now()
            user.failed_login_attempts = 0
            if ip:
                user.add_login_record(ip, user_agent)
                if ip not in user.ip_addresses:
                    user.ip_addresses.append(ip)
            self._save_users()
            logger.info(f"Успішний вхід користувача: {username}")
            return user
        
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.lock_account()
            self._save_users()
        
        logger.warning(f"Невдала спроба входу: {username}")
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users:
            if user.username.lower() == username.lower():
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        for user in self.users:
            if user.email.lower() == email.lower():
                return user
        return None
    
    def update_user(self, user_id: str, update_data: dict, admin_id: str = None) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        allowed_fields = ['full_name', 'phone', 'preferences', 'is_active', 
                         'language', 'notifications_enabled', 'two_factor_enabled']
        
        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(user, key, value)
        
        self._save_users()
        logger.info(f"Оновлено дані користувача: {user.username} (адмін: {admin_id})")
        return user
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        if not user.check_password(old_password):
            return False
        
        user.set_password(new_password)
        self._save_users()
        logger.info(f"Змінено пароль для користувача: {user.username}")
        return True
    
    def reset_password(self, user_id: str, new_password: str, admin_id: str = None) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.set_password(new_password)
        self._save_users()
        logger.info(f"Скинуто пароль для користувача: {user.username} (адмін: {admin_id})")
        return True
    
    def deactivate_user(self, user_id: str, admin_id: str = None, reason: str = None) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.deactivate(admin_id, reason)
        self._save_users()
        logger.info(f"Деактивовано користувача: {user.username} (адмін: {admin_id}, причина: {reason})")
        return user
    
    def activate_user(self, user_id: str, admin_id: str = None) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.activate()
        self._save_users()
        logger.info(f"Активовано користувача: {user.username} (адмін: {admin_id})")
        return user
    
    def set_admin_role(self, user_id: str, is_admin: bool, admin_id: str = None) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_admin = is_admin
        user.role = 'admin' if is_admin else 'user'
        self._save_users()
        action = "призначено" if is_admin else "знято"
        logger.info(f"{action} адміністратора: {user.username} (адмін: {admin_id})")
        return user
    
    def get_all_users(self, include_inactive: bool = False) -> List[User]:
        if include_inactive:
            return self.users.copy()
        return [u for u in self.users if u.is_active]
    
    def get_active_users(self) -> List[User]:
        return [u for u in self.users if u.is_active]
    
    def get_inactive_users(self) -> List[User]:
        return [u for u in self.users if not u.is_active]
    
    def get_admin_users(self) -> List[User]:
        return [u for u in self.users if u.is_admin and u.is_active]
    
    def get_stats(self) -> Dict[str, Any]:
        total = len(self.users)
        active = len([u for u in self.users if u.is_active])
        inactive = total - active
        admins = len([u for u in self.users if u.is_admin])
        verified = len([u for u in self.users if u.is_verified])
        
        today = datetime.now().date()
        new_today = len([u for u in self.users if u.created_at.date() == today])
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'admins': admins,
            'verified': verified,
            'new_today': new_today
        }
