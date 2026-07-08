"""
Тести для моделі та сервісу користувачів
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from src.models.user import User
from src.services.user_service import UserService


class TestUserModel:
    def test_user_creation(self):
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User'
        )
        user.set_password('Test123!')
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('Test123!') is True
        assert user.check_password('wrong') is False

    def test_user_validation(self):
        # Валідні дані
        assert User.is_valid_username('test_user') is True
        assert User.is_valid_username('ab') is False
        assert User.is_valid_email('test@example.com') is True
        assert User.is_valid_email('invalid') is False
        assert User.is_valid_phone('+380501234567') is True
        assert User.is_valid_phone('0501234567') is True
        assert User.is_valid_phone('123') is False

    def test_password_validation(self):
        is_valid, msg = User.validate_password('Weak')
        assert is_valid is False
        assert '8 символів' in msg

        is_valid, msg = User.validate_password('Strong123!')
        assert is_valid is True

    def test_user_to_dict(self):
        user = User(username='test', email='t@t.com')
        data = user.to_dict()
        assert data['username'] == 'test'
        assert 'password_hash' not in data  # не показуємо хеш

        data_sensitive = user.to_dict(include_sensitive=True)
        assert 'password_hash' in data_sensitive


class TestUserService:
    @pytest.fixture
    def temp_users_file(self, tmp_path):
        file_path = tmp_path / 'users.json'
        # Початкові дані
        initial = [
            {
                'user_id': 'USR-001',
                'username': 'admin',
                'email': 'admin@test.com',
                'password_hash': User.hash_password('Admin123!'),
                'full_name': 'Admin',
                'is_active': True,
                'is_admin': True,
                'created_at': datetime.now().isoformat()
            }
        ]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(initial, f, ensure_ascii=False, indent=2)
        return file_path

    def test_register_user(self, temp_users_file):
        service = UserService(data_file=temp_users_file)
        user = service.register_user(
            username='newuser',
            email='new@example.com',
            password='Strong123!',
            full_name='New User'
        )
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('Strong123!') is True

        # Перевірка дублікатів
        with pytest.raises(ValueError):
            service.register_user('newuser', 'x@x.com', 'Pass123!')

    def test_authenticate_user(self, temp_users_file):
        service = UserService(data_file=temp_users_file)
        user = service.register_user('testuser', 'test@t.com', 'Strong123!')
        auth_user = service.authenticate_user('testuser', 'Strong123!')
        assert auth_user is not None
        assert auth_user.username == 'testuser'

        bad_auth = service.authenticate_user('testuser', 'wrong')
        assert bad_auth is None

    def test_login_generates_token(self, temp_users_file):
        service = UserService(data_file=temp_users_file, secret_key='test-secret')
        service.register_user('user1', 'u@u.com', 'Pass123!')
        result = service.login('user1', 'Pass123!')
        assert 'token' in result
        assert 'user' in result
        assert result['user']['username'] == 'user1'

        # Перевірка токена
        payload = service.verify_token(result['token'])
        assert payload is not None
        assert payload['username'] == 'user1'

        # Невірний пароль
        with pytest.raises(ValueError):
            service.login('user1', 'wrong')

    def test_get_user_by_id(self, temp_users_file):
        service = UserService(data_file=temp_users_file)
        user = service.get_user_by_id('USR-001')
        assert user is not None
        assert user.username == 'admin'

        assert service.get_user_by_id('USR-XXX') is None

    def test_update_user(self, temp_users_file):
        service = UserService(data_file=temp_users_file)
        user = service.register_user('test', 't@t.com', 'Pass123!')
        updated = service.update_user(user.user_id, {'full_name': 'Updated Name'})
        assert updated.full_name == 'Updated Name'

        # Перевірка заборонених полів
        updated = service.update_user(user.user_id, {'password_hash': 'hacked'})
        assert updated.password_hash != 'hacked'

    def test_change_password(self, temp_users_file):
        service = UserService(data_file=temp_users_file)
        user = service.register_user('test', 't@t.com', 'OldPass123!')
        assert service.change_password(user.user_id, 'OldPass123!', 'NewPass456!') is True
        # Перевіряємо новий пароль
        auth = service.authenticate_user('test', 'NewPass456!')
        assert auth is not None

        assert service.change_password(user.user_id, 'wrong', 'NewPass') is False

    def test_stats(self, temp_users_file):
        service = UserService(data_file=temp_users_file)
        service.register_user('u1', 'u1@x.com', 'Pass123!')
        service.register_user('u2', 'u2@x.com', 'Pass123!')
        stats = service.get_stats()
        assert stats['total'] >= 3  # admin + 2 нових
        assert stats['active'] >= 3
