"""
Валідатори (доповнені для бронювання)
"""

import re
from datetime import datetime
from typing import Tuple, Optional, List, Dict


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


# --- Валідатори для бронювання ---

def validate_passenger_name(name: str) -> bool:
    """Перевіряє ім'я пасажира (мінімум 2 символи, тільки літери, пробіли, дефіси)"""
    if not name or len(name.strip()) < 2:
        return False
    pattern = r'^[A-Za-zА-Яа-яЇїІіЄє\s\-\.]+$'
    return bool(re.match(pattern, name.strip()))


def validate_passport(passport: str) -> bool:
    """Перевіряє номер паспорта (2-3 літери + 6-7 цифр)"""
    if not passport:
        return False
    pattern = r'^[A-Za-z]{2,3}\d{6,7}$'
    return bool(re.match(pattern, passport.strip().upper()))


def validate_passengers(passengers: List[Dict]) -> Tuple[bool, str]:
    """
    Перевіряє список пасажирів.
    Кожен пасажир повинен мати name та passport.
    """
    if not passengers:
        return False, "Додайте хоча б одного пасажира"
    for i, p in enumerate(passengers):
        name = p.get('name', '')
        passport = p.get('passport', '')
        if not validate_passenger_name(name):
            return False, f"Пасажир #{i+1}: невірне ім'я"
        if not validate_passport(passport):
            return False, f"Пасажир #{i+1}: невірний номер паспорта (очікується: 2-3 літери + 6-7 цифр)"
    return True, "OK"


def validate_booking_data(data: dict) -> Tuple[bool, str]:
    """
    Комплексна валідація даних бронювання
    """
    required = ['flight_id', 'seats', 'passengers']
    for field in required:
        if field not in data:
            return False, f"Відсутнє поле: {field}"

    if not data['flight_id']:
        return False, "Не вказано рейс"

    seats = data.get('seats')
    if not isinstance(seats, int) or seats < 1:
        return False, "Кількість місць має бути додатним числом"

    # Перевіряємо пасажирів
    return validate_passengers(data['passengers'])
