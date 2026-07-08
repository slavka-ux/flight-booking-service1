"""
Валідатори (доповнені для аутентифікації)
"""

import re
from datetime import datetime
from typing import Tuple, Optional, List, Dict


# === Існуючі валідатори (з попередніх гілок) ===

def validate_origin_destination(origin: str, destination: str) -> Tuple[bool, str]:
    if not origin or not origin.strip():
        return False, "Введіть місто вильоту"
    if not destination or not destination.strip():
        return False, "Введіть місто прильоту"
    if origin.strip().lower() == destination.strip().lower():
        return False, "Міста не можуть бути однаковими"
    if len(origin.strip()) < 2 or len(destination.strip()) < 2:
        return False, "Назва міста має містити щонайменше 2 символи"
    pattern = r'^[A-Za-zА-Яа-яЇїІіЄє\s\-\.]+$'
    if not re.match(pattern, origin.strip()):
        return False, "Назва міста вильоту містить недопустимі символи"
    if not re.match(pattern, destination.strip()):
        return False, "Назва міста прильоту містить недопустимі символи"
    return True, "OK"


def validate_date(date_str: Optional[str]) -> Tuple[bool, str]:
    if not date_str:
        return True, "OK"
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, "Невірний формат дати. Використовуйте YYYY-MM-DD"
    try:
        date_obj = datetime.fromisoformat(date_str)
        today = datetime.now().date()
        if date_obj.date() < today:
            return False, "Дата не може бути в минулому"
        return True, "OK"
    except ValueError:
        return False, "Невірна дата"


def validate_passenger_name(name: str) -> bool:
    if not name or len(name.strip()) < 2:
        return False
    pattern = r'^[A-Za-zА-Яа-яЇїІіЄє\s\-\.]+$'
    return bool(re.match(pattern, name.strip()))


def validate_passport(passport: str) -> bool:
    if not passport:
        return False
    pattern = r'^[A-Za-z]{2,3}\d{6,7}$'
    return bool(re.match(pattern, passport.strip().upper()))


def validate_passengers(passengers: List[Dict]) -> Tuple[bool, str]:
    if not passengers:
        return False, "Додайте хоча б одного пасажира"
    for i, p in enumerate(passengers):
        name = p.get('name', '')
        passport = p.get('passport', '')
        if not validate_passenger_name(name):
            return False, f"Пасажир #{i+1}: невірне ім'я"
        if not validate_passport(passport):
            return False, f"Пасажир #{i+1}: невірний номер паспорта"
    return True, "OK"


def validate_booking_data(data: dict) -> Tuple[bool, str]:
    required = ['flight_id', 'seats', 'passengers']
    for field in required:
        if field not in data:
            return False, f"Відсутнє поле: {field}"
    if not data['flight_id']:
        return False, "Не вказано рейс"
    seats = data.get('seats')
    if not isinstance(seats, int) or seats < 1:
        return False, "Кількість місць має бути додатним числом"
    return validate_passengers(data['passengers'])


# === Нові валідатори для аутентифікації ===

def validate_username(username: str) -> Tuple[bool, str]:
    """Перевіряє ім'я користувача (3-30 символів, літери, цифри, _)"""
    if not username or len(username.strip()) < 3:
        return False, "Ім'я користувача має містити не менше 3 символів"
    if len(username) > 30:
        return False, "Ім'я користувача має містити не більше 30 символів"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Ім'я користувача може містити тільки літери, цифри та символ _"
    return True, "OK"


def validate_email(email: str) -> Tuple[bool, str]:
    if not email or not email.strip():
        return False, "Email не може бути порожнім"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        return False, "Невірний формат email"
    return True, "OK"


def validate_password_strength(password: str) -> Tuple[bool, str]:
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


def validate_phone(phone: str) -> Tuple[bool, str]:
    if not phone:
        return True, "OK"  # телефон не обов'язковий
    phone = re.sub(r'[\s\-]', '', phone)
    pattern = r'^\+?380\d{9}$|^0\d{9}$'
    if not re.match(pattern, phone):
        return False, "Невірний формат телефону (очікується +380XXXXXXXXX або 0XXXXXXXXX)"
    return True, "OK"


def validate_register_data(data: dict) -> Tuple[bool, str]:
    """Комплексна валідація даних реєстрації"""
    required = ['username', 'email', 'password']
    for field in required:
        if field not in data or not data[field]:
            return False, f"Поле '{field}' є обов'язковим"

    is_valid, msg = validate_username(data['username'])
    if not is_valid:
        return False, msg

    is_valid, msg = validate_email(data['email'])
    if not is_valid:
        return False, msg

    is_valid, msg = validate_password_strength(data['password'])
    if not is_valid:
        return False, msg

    # Перевіряємо, чи пароль не містить ім'я або email
    username_lower = data['username'].lower()
    password_lower = data['password'].lower()
    if username_lower in password_lower or data['email'].lower().split('@')[0] in password_lower:
        return False, "Пароль не повинен містити ім'я користувача або частину email"

    if data.get('phone'):
        is_valid, msg = validate_phone(data['phone'])
        if not is_valid:
            return False, msg

    return True, "OK"
