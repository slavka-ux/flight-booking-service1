"""
Валідатори для пошуку та вхідних даних
"""

import re
from datetime import datetime
from typing import Tuple, Optional


def validate_origin_destination(origin: str, destination: str) -> Tuple[bool, str]:
    """
    Перевіряє коректність введених міст
    
    Args:
        origin: Місто вильоту
        destination: Місто прильоту
        
    Returns:
        Tuple[bool, str]: (чи валідно, повідомлення)
    """
    if not origin or not origin.strip():
        return False, "Введіть місто вильоту"
    
    if not destination or not destination.strip():
        return False, "Введіть місто прильоту"
    
    if origin.strip().lower() == destination.strip().lower():
        return False, "Місто вильоту і прильоту не можуть бути однаковими"
    
    if len(origin.strip()) < 2 or len(destination.strip()) < 2:
        return False, "Назва міста має містити щонайменше 2 символи"
    
    # Дозволяємо тільки літери, пробіли, дефіси, крапки
    pattern = r'^[A-Za-zА-Яа-яЇїІіЄє\s\-\.]+$'
    if not re.match(pattern, origin.strip()):
        return False, "Назва міста вильоту містить недопустимі символи"
    
    if not re.match(pattern, destination.strip()):
        return False, "Назва міста прильоту містить недопустимі символи"
    
    return True, "OK"


def validate_date(date_str: Optional[str]) -> Tuple[bool, str]:
    """
    Перевіряє коректність дати (опціонально)
    
    Args:
        date_str: Дата у форматі YYYY-MM-DD або None
        
    Returns:
        Tuple[bool, str]: (чи валідно, повідомлення)
    """
    if not date_str:
        return True, "OK"  # Дата не обов'язкова
    
    # Перевіряємо формат
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


def validate_flight_number(flight_number: str) -> bool:
    """
    Перевіряє формат номера рейсу (наприклад, SA-102)
    """
    if not flight_number:
        return False
    pattern = r'^[A-Z]{2,3}-\d{3,4}$'
    return bool(re.match(pattern, flight_number.strip().upper()))


def validate_price(price: float) -> bool:
    """Перевіряє, чи ціна додатна"""
    return isinstance(price, (int, float)) and price > 0


def validate_seats(seats: int) -> bool:
    """Перевіряє, чи кількість місць додатна"""
    return isinstance(seats, int) and seats > 0
