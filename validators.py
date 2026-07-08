"""
Валідатори – ОБ'ЄДНАНА ВЕРСІЯ
Включає всі перевірки з усіх гілок:
- flight-search: origin/destination, date
- booking-system: passenger name, passport, booking data
- user-auth: username, email, password, phone, registration
- payment-integration: card number, expiry, CVV, payment data
"""

import re
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any


# ================================================================
#  ВАЛІДАТОРИ ДЛЯ ПОШУКУ (flight-search)
# ================================================================

def validate_origin_destination(origin: str, destination: str) -> Tuple[bool, str]:
    """
    Перевіряє коректність введених міст
    """
    if not origin or not origin.strip():
        return False, "Введіть місто вильоту"
    if not destination or not destination.strip():
        return False, "Введіть місто прильоту"
    if origin.strip().lower() == destination.strip().lower():
        return False, "Місто вильоту і прильоту не можуть бути однаковими"
    if len(origin.strip()) < 2 or len(destination.strip()) < 2:
        return False, "Назва міста має містити щонайменше 2 символи"
    pattern = r'^[A-Za-zА-Яа-яЇїІіЄє\s\-\.]+$'
    if not re.match(pattern, origin.strip()):
        return False, "Назва міста вильоту містить недопустимі символи"
    if not re.match(pattern, destination.strip()):
        return False, "Назва міста прильоту містить недопустимі символи"
    return True, "OK"


def validate_date(date_str: Optional[str]) -> Tuple[bool, str]:
    """
    Перевіряє коректність дати (опціонально)
    """
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


# ================================================================
#  ВАЛІДАТОРИ ДЛЯ БРОНЮВАННЯ (booking-system)
# ================================================================

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

    return validate_passengers(data['passengers'])


# ================================================================
#  ВАЛІДАТОРИ ДЛЯ АУТЕНТИФІКАЦІЇ (user-auth)
# ================================================================

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
    """Перевіряє email"""
    if not email or not email.strip():
        return False, "Email не може бути порожнім"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        return False, "Невірний формат email"
    return True, "OK"


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Перевіряє надійність пароля"""
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
    """Перевіряє телефон (український формат)"""
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


# ================================================================
#  ВАЛІДАТОРИ ДЛЯ ОПЛАТИ (payment-integration)
# ================================================================

def validate_card_number(card_number: str) -> bool:
    """
    Валідація номера картки (алгоритм Luhn)
    """
    card_number = re.sub(r'[\s\-]', '', card_number)
    if not card_number.isdigit():
        return False
    if len(card_number) not in [15, 16]:
        return False

    # Алгоритм Luhn
    total = 0
    reverse_digits = card_number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def validate_card_expiry(expiry_date: str) -> bool:
    """
    Валідація терміну дії картки (MM/YY)
    """
    if not re.match(r'^\d{2}/\d{2}$', expiry_date):
        return False
    try:
        month, year = expiry_date.split('/')
        month = int(month)
        year = int(year) + 2000
        if not (1 <= month <= 12):
            return False
        now = datetime.now()
        if year < now.year:
            return False
        if year == now.year and month < now.month:
            return False
        return True
    except (ValueError, AttributeError):
        return False


def validate_card_cvv(cvv: str) -> bool:
    """Валідація CVV коду (3-4 цифри)"""
    cvv = cvv.strip()
    if not cvv.isdigit():
        return False
    if len(cvv) not in [3, 4]:
        return False
    return True


def validate_cardholder_name(name: str) -> bool:
    """Валідація імені власника картки"""
    if not name or len(name.strip()) < 2:
        return False
    pattern = r'^[A-Za-z\s\.\-]{2,100}$'
    return bool(re.match(pattern, name.strip()))


def validate_payment_method(method: str, available_methods: list = None) -> bool:
    """Перевіряє, чи метод оплати доступний"""
    if available_methods is None:
        available_methods = ['card', 'google_pay', 'apple_pay', 'bank_transfer']
    return method in available_methods


def validate_payment_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Комплексна валідація даних оплати
    """
    required = ['booking_id', 'method']
    for field in required:
        if field not in data:
            return False, f"Відсутнє поле: {field}"

    method = data['method']
    if not validate_payment_method(method):
        return False, f"Невідомий метод оплати: {method}"

    # Додаткова валідація для картки
    if method == 'card':
        card_data = data.get('card_data', {})
        if 'card_number' not in card_data:
            return False, "Відсутній номер картки"
        if not validate_card_number(card_data['card_number']):
            return False, "Невірний номер картки"
        if 'expiry_date' not in card_data:
            return False, "Відсутній термін дії картки"
        if not validate_card_expiry(card_data['expiry_date']):
            return False, "Невірний термін дії картки або картка прострочена"
        if 'cvv' not in card_data:
            return False, "Відсутній CVV код"
        if not validate_card_cvv(card_data['cvv']):
            return False, "Невірний CVV код"
        if 'cardholder_name' in card_data and card_data['cardholder_name']:
            if not validate_cardholder_name(card_data['cardholder_name']):
                return False, "Невірне ім'я власника картки"

    return True, "OK"


# ================================================================
#  ДОПОМІЖНІ ФУНКЦІЇ ДЛЯ ФОРМАТУВАННЯ
# ================================================================

def format_card_number(card_number: str) -> str:
    """Форматує номер картки (XXXX XXXX XXXX XXXX)"""
    card_number = re.sub(r'[\s\-]', '', card_number)
    return ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])


def mask_card_number(card_number: str) -> str:
    """Маскує номер картки (XXXX XXXX XXXX 1234)"""
    card_number = re.sub(r'[\s\-]', '', card_number)
    if len(card_number) >= 4:
        return f"XXXX XXXX XXXX {card_number[-4:]}"
    return "XXXX XXXX XXXX XXXX"


def detect_card_type(card_number: str) -> str:
    """Визначає тип картки за номером"""
    card_number = re.sub(r'[\s\-]', '', card_number)
    if card_number.startswith('4'):
        return 'Visa'
    elif card_number.startswith(('51', '52', '53', '54', '55')):
        return 'Mastercard'
    elif card_number.startswith(('34', '37')):
        return 'American Express'
    elif card_number.startswith('60'):
        return 'Discover'
    elif card_number.startswith('62'):
        return 'UnionPay'
    else:
        return 'Unknown'
