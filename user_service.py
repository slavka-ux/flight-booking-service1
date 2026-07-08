"""
Сервіс для роботи з користувачами (аутентифікація)
"""

import json
import jwt
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from src.models.user import User
from src.utils.helpers import generate_token, decode_token, hash_password, verify_password
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Сервіс управління користувачами"""

    def __init__(self, data_file: str = None, secret_key: str = None):
        if data_file is None:
            base_dir = Path(__file__).parent.parent.parent
            data_file = base_dir / 'data' / 'users.json'
        self.data_file = Path(data_file)
        self.users: List[User] = []
        self.secret_key = secret_key or 'dev-secret-key-change-in-production'
        self._load_users()

    def _load_users(self):
        if not self.data_file.exists():
            self.users = []
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.users = [User.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Помилка завантаження користувачів: {e}")
            self.users = []

    def _save_users(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([u.to_dict() for u in self.users], f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error(f"Помилка збереження користувачів: {e}")

    def register_user(self, username: str, email: str, password: str,
                      full_name: str = '', phone: str = '') -> User:
        """Реєстрація нового користувача"""
        # Перевірка унікальності
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

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентифікація користувача (перевірка пароля)"""
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            user.last_login = datetime.datetime.now()
            self._save_users()
            logger.info(f"Успішний вхід користувача: {username}")
            return user
        logger.warning(f"Невдала спроба входу: {username}")
        return None

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Вхід користувача з генерацією JWT токена
        Повертає словник з токеном та даними користувача
        """
        user = self.authenticate_user(username, password)
        if not user:
            raise ValueError("Невірний логін або пароль")

        # Генеруємо JWT токен
        token = generate_token(
            user_id=user.user_id,
            username=user.username,
            is_admin=user.is_admin,
            secret_key=self.secret_key,
            expires_in=3600  # 1 година
        )

        return {
            'token': token,
            'user': user.to_dict(),
            'expires_in': 3600
        }

    def verify_token(self, token: str) -> Optional[Dict]:
        """Перевіряє JWT токен та повертає payload"""
        return decode_token(token, self.secret_key)

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

    def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        allowed_fields = ['full_name', 'phone', 'preferences', 'is_active', 'is_admin']
        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(user, key, value)
        self._save_users()
        logger.info(f"Оновлено дані користувача: {user.username}")
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

    def get_all_users(self) -> List[User]:
        return self.users.copy()

    def get_active_users(self) -> List[User]:
        return [u for u in self.users if u.is_active]

    def get_stats(self) -> dict:
        total = len(self.users)
        active = len([u for u in self.users if u.is_active])
        admins = len([u for u in self.users if u.is_admin])
        verified = len([u for u in self.users if u.is_verified])
        return {
            'total': total,
            'active': active,
            'admins': admins,
            'verified': verified
      }
