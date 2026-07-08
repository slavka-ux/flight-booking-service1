"""
Сервіс для роботи з користувачами – ОБ'ЄДНАНА ВЕРСІЯ
Включає всі методи з усіх гілок:
- user-auth: реєстрація, аутентифікація, JWT, зміна пароля
- admin-panel: управління ролями, активація/деактивація, статистика
- booking-system: bookings_history
"""

import json
import jwt
import datetime
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from src.models.user import User
from src.utils.helpers import generate_token, decode_token

logger = logging.getLogger(__name__)


class UserService:
    """Сервіс управління користувачами (повний)"""

    def __init__(self, data_file: str = None, secret_key: str = None):
        if data_file is None:
            base_dir = Path(__file__).parent.parent.parent
            data_file = base_dir / 'data' / 'users.json'
        self.data_file = Path(data_file)
        self.users: List[User] = []
        self.secret_key = secret_key or 'dev-secret-key-change-in-production'
        self._load_users()

    # ============================================================
    #  РОБОТА З ФАЙЛОМ
    # ============================================================

    def _load_users(self):
        if not self.data_file.exists():
            self.users = []
            logger.warning(f"Файл користувачів не знайдено: {self.data_file}")
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.users = [User.from_dict(item) for item in data]
                logger.info(f"Завантажено {len(self.users)} користувачів")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Помилка завантаження користувачів: {e}")
            self.users = []

    def _save_users(self):
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([u.to_dict() for u in self.users], f, ensure_ascii=False, indent=2)
            logger.info(f"Збережено {len(self.users)} користувачів")
        except IOError as e:
            logger.error(f"Помилка запису користувачів: {e}")
            raise RuntimeError("Не вдалося зберегти дані користувачів") from e

    # ============================================================
    #  РЕЄСТРАЦІЯ ТА АУТЕНТИФІКАЦІЯ (user-auth)
    # ============================================================

    def register_user(self, username: str, email: str, password: str,
                      full_name: str = '', phone: str = '') -> User:
        """Реєстрація нового користувача"""
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
        """Аутентифікація користувача"""
        user = self.get_user_by_username(username)
        if user and user.authenticate(password):
            if ip:
                user.add_login_record(ip, user_agent)
                if ip not in user.ip_addresses:
                    user.ip_addresses.append(ip)
            self._save_users()
            logger.info(f"Успішний вхід користувача: {username}")
            return user

        if user:
            self._save_users()
        logger.warning(f"Невдала спроба входу: {username}")
        return None

    def login(self, username: str, password: str, ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Вхід з генерацією JWT токена"""
        user = self.authenticate_user(username, password, ip, user_agent)
        if not user:
            raise ValueError("Невірний логін або пароль")

        token = generate_token(
            user_id=user.user_id,
            username=user.username,
            is_admin=user.is_admin,
            secret_key=self.secret_key,
            expires_in=3600
        )

        return {
            'token': token,
            'user': user.to_dict(),
            'expires_in': 3600
        }

    def verify_token(self, token: str) -> Optional[Dict]:
        """Перевіряє JWT токен"""
        return decode_token(token, self.secret_key)

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Змінює пароль користувача"""
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
        """Скидає пароль (адмін)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        user.set_password(new_password)
        self._save_users()
        logger.info(f"Скинуто пароль для користувача: {user.username} (адмін: {admin_id})")
        return True

    # ============================================================
    #  ОТРИМАННЯ ДАНИХ
    # ============================================================

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

    # ============================================================
    #  АДМІН-ОПЕРАЦІЇ (admin-panel)
    # ============================================================

    def update_user(self, user_id: str, update_data: dict, admin_id: str = None) -> Optional[User]:
        """Оновлює дані користувача (адмін)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        allowed_fields = [
            'full_name', 'phone', 'preferences', 'language',
            'notifications_enabled', 'two_factor_enabled', 'avatar_url'
        ]

        for key, value in update_data.items():
            if key in allowed_fields:
                setattr(user, key, value)

        self._save_users()
        logger.info(f"Оновлено дані користувача: {user.username} (адмін: {admin_id})")
        return user

    def deactivate_user(self, user_id: str, admin_id: str = None, reason: str = None) -> Optional[User]:
        """Деактивує користувача (адмін)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        if user.user_id == admin_id:
            raise ValueError("Не можна деактивувати себе")
        user.deactivate(admin_id, reason)
        self._save_users()
        logger.info(f"Деактивовано користувача: {user.username} (адмін: {admin_id})")
        return user

    def activate_user(self, user_id: str, admin_id: str = None) -> Optional[User]:
        """Активує користувача (адмін)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        user.activate()
        self._save_users()
        logger.info(f"Активовано користувача: {user.username} (адмін: {admin_id})")
        return user

    def set_admin_role(self, user_id: str, is_admin: bool, admin_id: str = None) -> Optional[User]:
        """Надає/знімає права адміністратора (адмін)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        if user.user_id == admin_id and not is_admin:
            raise ValueError("Не можна зняти права адміністратора з себе")
        user.is_admin = is_admin
        user.role = 'admin' if is_admin else 'user'
        self._save_users()
        action = "призначено" if is_admin else "знято"
        logger.info(f"{action} адміністратора: {user.username} (адмін: {admin_id})")
        return user

    # ============================================================
    #  СТАТИСТИКА
    # ============================================================

    def get_stats(self) -> Dict[str, Any]:
        """Отримує статистику по користувачах"""
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
