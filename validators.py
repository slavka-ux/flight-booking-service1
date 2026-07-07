"""
Валідатори даних (оновлені для оплати)
"""

import re
from datetime import datetime
from typing import Tuple, Any, Optional, Dict

# ============ Існуючі валідатори ============

def validate_email(email: str) -> bool:
    """Перевірка email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Перевірка телефону (український формат)"""
    pattern = r'^\+?380\d{9}$|^0\d{9}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))

def validate_password(password: str) -> Tuple[bool, str]:
    """Перевірка паролю"""
    if len(password) < 8:
        return False, "Пароль має містити не менше 8 символів"
    if not re.search(r'[A-Z]', password):
        return False, "Пароль має містити хоча б одну велику літеру"
    if not re.search(r'[a-z]', password):
        return False, "Пароль має містити хоча б одну маленьку літеру"
    if not re.search(r'\d', password):
        return False, "Пароль має містити хоча б одну цифру"
    return True, "OK"

def validate_date(date_str: str) -> Optional[datetime]:
    """Перевірка та парсинг дати"""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None

def validate_flight_data(data: dict) -> Tuple[bool, str]:
    """Перевірка даних рейсу"""
    required_fields = ['airline', 'origin', 'destination', 
                      'departure_time', 'arrival_time', 'price', 'available_seats']
    
    for field in required_fields:
        if field not in data:
            return False, f"Відсутнє поле: {field}"
    
    if data['price'] <= 0:
        return False, "Ціна має бути більшою за 0"
    
    if data['available_seats'] < 0:
        return False, "Кількість місць не може бути від'ємною"
    
    dep_time = validate_date(data['departure_time'])
    arr_time = validate_date(data['arrival_time'])
    
    if not dep_time:
        return False, "Невірний формат дати вильоту"
    if not arr_time:
        return False, "Невірний формат дати прильоту"
    if arr_time <= dep_time:
        return False, "Час прильоту має бути пізніше часу вильоту"
    
    return True, "OK"

def validate_booking_data(data: dict) -> Tuple[bool, str]:
    """Перевірка даних бронювання"""
    required_fields = ['user_id', 'flight_id', 'seats']
    
    for field in required_fields:
        if field not in data:
            return False, f"Відсутнє поле: {field}"
    
    if data['seats'] < 1:
        return False, "Кількість місць має бути не менше 1"
    
    if data.get('passengers'):
        if len(data['passengers']) != data['seats']:
            return False, "Кількість пасажирів має відповідати кількості місць"
        
        for passenger in data['passengers']:
            if 'name' not in passenger or 'passport' not in passenger:
                return False, "У кожного пасажира мають бути ім'я та паспорт"
    
    return True, "OK"

def validate_user_data(data: dict) -> Tuple[bool, str]:
    """Перевірка даних користувача"""
    required_fields = ['username', 'email', 'password']
    
    for field in required_fields:
        if field not in data:
            return False, f"Відсутнє поле: {field}"
    
    if not validate_email(data['email']):
        return False, "Невірний формат email"
    
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        return False, message
    
    if len(data.get('username', '')) < 3:
        return False, "Ім'я користувача має містити не менше 3 символів"
    
    return True, "OK"

# ============ Нові валідатори для оплати ============

def validate_card_number(card_number: str) -> bool:
    """
    Валідація номера картки (алгоритм Luhn)
    
    Args:
        card_number: Номер картки (з пробілами або без)
        
    Returns:
        bool: True якщо номер валідний
    """
    # Видаляємо пробіли та дефіси
    card_number = re.sub(r'[\s\-]', '', card_number)
    
    # Перевіряємо що це цифри
    if not card_number.isdigit():
        return False
    
    # Перевіряємо довжину
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
    
    Args:
        expiry_date: Дата у форматі MM/YY
        
    Returns:
        bool: True якщо дата валідна
    """
    try:
        # Перевіряємо формат
        if not re.match(r'^\d{2}/\d{2}$', expiry_date):
            return False
        
        month, year = expiry_date.split('/')
        month = int(month)
        year = int(year) + 2000
        
        # Перевіряємо місяць
        if not (1 <= month <= 12):
            return False
        
        # Перевіряємо дату
        now = datetime.now()
        if year < now.year:
            return False
        if year == now.year and month < now.month:
            return False
        
        return True
    except (ValueError, AttributeError):
        return False

def validate_card_cvv(cvv: str) -> bool:
    """
    Валідація CVV коду
    
    Args:
        cvv: CVV код (3-4 цифри)
        
    Returns:
        bool: True якщо CVV валідний
    """
    cvv = cvv.strip()
    if not cvv.isdigit():
        return False
    if len(cvv) not in [3, 4]:
        return False
    return True

def validate_payment_amount(amount: float, min_amount: float = 1.0, max_amount: float = 1000000.0) -> Tuple[bool, str]:
    """
    Валідація суми платежу
    
    Args:
        amount: Сума
        min_amount: Мінімальна сума
        max_amount: Максимальна сума
        
    Returns:
        tuple: (чи валідна, повідомлення)
    """
    if amount <= 0:
        return False, "Сума має бути більшою за 0"
    
    if amount < min_amount:
        return False, f"Мінімальна сума платежу: {min_amount} ₴"
    
    if amount > max_amount:
        return False, f"Максимальна сума платежу: {max_amount} ₴"
    
    # Перевіряємо кількість знаків після коми
    if len(str(amount).split('.')[-1]) > 2:
        return False, "Сума може мати не більше 2 знаків після коми"
    
    return True, "OK"

def validate_cardholder_name(name: str) -> bool:
    """
    Валідація імені власника картки
    
    Args:
        name: Ім'я власника
        
    Returns:
        bool: True якщо ім'я валідне
    """
    if not name or len(name.strip()) < 2:
        return False
    
    # Дозволені тільки літери, пробіли, крапки та дефіси
    pattern = r'^[A-Za-z\s\.\-]{2,100}$'
    return bool(re.match(pattern, name.strip()))

def validate_payment_method(method: str, available_methods: list) -> bool:
    """
    Валідація методу оплати
    
    Args:
        method: Метод оплати
        available_methods: Список доступних методів
        
    Returns:
        bool: True якщо метод доступний
    """
    return method in available_methods

def validate_payment_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Комплексна валідація даних оплати
    
    Args:
        data: Дані оплати
        
    Returns:
        tuple: (чи валідні, повідомлення)
    """
    # Перевіряємо обов'язкові поля
    required_fields = ['booking_id', 'method', 'amount']
    for field in required_fields:
        if field not in data:
            return False, f"Відсутнє поле: {field}"
    
    # Валідація суми
    is_valid, message = validate_payment_amount(data['amount'])
    if not is_valid:
        return False, message
    
    # Валідація методу
    available = ['card', 'google_pay', 'apple_pay', 'bank_transfer', 'cash']
    if not validate_payment_method(data['method'], available):
        return False, f"Невідомий метод оплати: {data['method']}"
    
    # Додаткова валідація для картки
    if data['method'] == 'card':
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
        
        if 'cardholder_name' in card_data:
            if not validate_cardholder_name(card_data['cardholder_name']):
                return False, "Невірне ім'я власника картки"
    
    return True, "OK"

def format_card_number(card_number: str) -> str:
    """
    Форматування номера картки (XXXX XXXX XXXX XXXX)
    
    Args:
        card_number: Номер картки
        
    Returns:
        str: Відформатований номер
    """
    card_number = re.sub(r'[\s\-]', '', card_number)
    return ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])

def mask_card_number(card_number: str) -> str:
    """
    Маскування номера картки (XXXX XXXX XXXX 1234)
    
    Args:
        card_number: Номер картки
        
    Returns:
        str: Замаскований номер
    """
    card_number = re.sub(r'[\s\-]', '', card_number)
    if len(card_number) >= 4:
        return f"XXXX XXXX XXXX {card_number[-4:]}"
    return "XXXX XXXX XXXX XXXX"

def detect_card_type(card_number: str) -> str:
    """
    Визначення типу картки за номером
    
    Args:
        card_number: Номер картки
        
    Returns:
        str: Тип картки
    """
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
    elif card_number.startswith('50'):
        return 'Maestro'
    else:
        return 'Unknown'
