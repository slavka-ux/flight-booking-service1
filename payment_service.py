"""
Сервіс для роботи з оплатами
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import logging
import random
import hashlib
import hmac
import json

from src.models.booking import Booking, Payment

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Сервіс обробки платежів
    
    Підтримує:
    - Оплату карткою
    - Google Pay
    - Apple Pay
    - Банківський переказ
    - Готівка
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        Ініціалізація платіжного сервісу
        
        Args:
            api_key: API ключ для платіжного шлюзу
            secret_key: Секретний ключ для підпису
        """
        self.api_key = api_key or "test_api_key"
        self.secret_key = secret_key or "test_secret_key"
        self.payments_db = []  # Імітація бази даних платежів
        
        # Налаштування для різних методів оплати
        self.payment_methods = {
            'card': {
                'name': 'Банківська картка',
                'icon': '💳',
                'enabled': True,
                'fee': 0.015  # 1.5% комісія
            },
            'google_pay': {
                'name': 'Google Pay',
                'icon': '📱',
                'enabled': True,
                'fee': 0.01  # 1% комісія
            },
            'apple_pay': {
                'name': 'Apple Pay',
                'icon': '🍎',
                'enabled': True,
                'fee': 0.01  # 1% комісія
            },
            'bank_transfer': {
                'name': 'Банківський переказ',
                'icon': '🏦',
                'enabled': True,
                'fee': 0.005  # 0.5% комісія
            },
            'cash': {
                'name': 'Готівка',
                'icon': '💵',
                'enabled': False,
                'fee': 0.0
            }
        }
    
    def process_payment(self, booking: Booking, method: str, 
                       card_data: Dict[str, Any] = None) -> Payment:
        """
        Обробка платежу
        
        Args:
            booking: Бронювання для оплати
            method: Метод оплати (card, google_pay, apple_pay, bank_transfer, cash)
            card_data: Дані картки (для методу 'card')
            
        Returns:
            Payment: Об'єкт платежу
        """
        # Перевірка методу оплати
        if method not in self.payment_methods:
            raise ValueError(f"Невідомий метод оплати: {method}")
        
        if not self.payment_methods[method]['enabled']:
            raise ValueError(f"Метод оплати {method} тимчасово недоступний")
        
        # Розрахунок комісії
        fee = self.payment_methods[method]['fee']
        amount = booking.total_price - booking.total_paid
        fee_amount = amount * fee
        total_amount = amount + fee_amount
        
        # Створення платежу
        payment = Payment(
            booking_id=booking.booking_id,
            amount=total_amount,
            currency='UAH',
            method=method,
            metadata={
                'booking_total': booking.total_price,
                'base_amount': amount,
                'fee': fee,
                'fee_amount': fee_amount,
                'fee_percentage': fee * 100
            }
        )
        
        # Обробка залежно від методу
        if method == 'card':
            payment = self._process_card_payment(payment, card_data)
        elif method == 'google_pay':
            payment = self._process_google_pay(payment)
        elif method == 'apple_pay':
            payment = self._process_apple_pay(payment)
        elif method == 'bank_transfer':
            payment = self._process_bank_transfer(payment)
        elif method == 'cash':
            payment = self._process_cash_payment(payment)
        
        # Збереження платежу
        self.payments_db.append(payment)
        
        # Додавання платежу до бронювання
        booking.add_payment(payment)
        
        logger.info(f"Платіж {payment.payment_id} оброблено: {payment.status}")
        
        return payment
    
    def _process_card_payment(self, payment: Payment, card_data: Dict[str, Any]) -> Payment:
        """
        Обробка оплати карткою
        """
        # Валідація даних картки
        required_fields = ['card_number', 'expiry_date', 'cvv', 'cardholder_name']
        for field in required_fields:
            if field not in card_data:
                payment.fail(f"Відсутнє поле: {field}")
                return payment
        
        # Валідація номера картки (Luhn алгоритм)
        if not self._validate_card_number(card_data['card_number']):
            payment.fail("Невірний номер картки")
            return payment
        
        # Валідація терміну дії
        if not self._validate_expiry_date(card_data['expiry_date']):
            payment.fail("Невірний термін дії картки")
            return payment
        
        # Імітація обробки платежу
        # В реальному проекті тут був би запит до платіжного шлюзу
        success = random.random() > 0.1  # 90% успішних транзакцій
        
        if success:
            transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            receipt_url = f"https://payment.flightbooking.com/receipts/{payment.payment_id}"
            
            payment.complete(
                transaction_id=transaction_id,
                receipt_url=receipt_url
            )
            
            # Збереження інформації про картку (безпечно)
            card_number = card_data['card_number'].replace(' ', '')
            payment.card_last_digits = card_number[-4:]
            payment.card_type = self._detect_card_type(card_number)
            payment.metadata['cardholder_name'] = card_data['cardholder_name']
        else:
            payment.fail("Платіж відхилено. Спробуйте пізніше або використайте іншу картку.")
        
        return payment
    
    def _process_google_pay(self, payment: Payment) -> Payment:
        """Обробка Google Pay"""
        # Імітація Google Pay
        success = random.random() > 0.05  # 95% успішних
        
        if success:
            transaction_id = f"GP-{uuid.uuid4().hex[:12].upper()}"
            payment.complete(
                transaction_id=transaction_id,
                receipt_url=f"https://payment.flightbooking.com/receipts/{payment.payment_id}"
            )
        else:
            payment.fail("Помилка Google Pay. Спробуйте інший метод оплати.")
        
        return payment
    
    def _process_apple_pay(self, payment: Payment) -> Payment:
        """Обробка Apple Pay"""
        success = random.random() > 0.05  # 95% успішних
        
        if success:
            transaction_id = f"AP-{uuid.uuid4().hex[:12].upper()}"
            payment.complete(
                transaction_id=transaction_id,
                receipt_url=f"https://payment.flightbooking.com/receipts/{payment.payment_id}"
            )
        else:
            payment.fail("Помилка Apple Pay. Спробуйте інший метод оплати.")
        
        return payment
    
    def _process_bank_transfer(self, payment: Payment) -> Payment:
        """Обробка банківського переказу"""
        # Для банківського переказу створюємо реквізити
        payment.metadata['bank_details'] = {
            'bank_name': 'ПриватБанк',
            'account': 'UA123456789012345678901234567',
            'iban': 'UA123456789012345678901234567',
            'swift': 'PBANUA2X',
            'recipient': 'Flight Booking Service LLC',
            'purpose': f'Оплата бронювання {payment.booking_id}'
        }
        
        # Банківський переказ зазвичай потребує підтвердження
        payment.status = 'pending'
        payment.transaction_id = f"BT-{uuid.uuid4().hex[:12].upper()}"
        
        return payment
    
    def _process_cash_payment(self, payment: Payment) -> Payment:
        """Обробка оплати готівкою"""
        # Готівка зазвичай не доступна онлайн
        payment.fail("Оплата готівкою недоступна для онлайн-замовлень")
        return payment
    
    def refund_payment(self, payment_id: str, reason: str = None) -> bool:
        """
        Повернення коштів за платіж
        
        Args:
            payment_id: ID платежу
            reason: Причина повернення
            
        Returns:
            bool: True якщо повернення успішне
        """
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            logger.error(f"Платіж {payment_id} не знайдено")
            return False
        
        if not payment.is_completed():
            logger.error(f"Платіж {payment_id} не можна повернути (статус: {payment.status})")
            return False
        
        # Імітація повернення
        payment.refund()
        payment.metadata['refund_reason'] = reason or 'Повернення коштів'
        payment.metadata['refund_date'] = datetime.now().isoformat()
        
        logger.info(f"Платіж {payment_id} повернуто")
        return True
    
    def get_payment_by_id(self, payment_id: str) -> Optional[Payment]:
        """Отримати платіж за ID"""
        for payment in self.payments_db:
            if payment.payment_id == payment_id:
                return payment
        return None
    
    def get_payments_by_booking(self, booking_id: str) -> list:
        """Отримати всі платежі для бронювання"""
        return [p for p in self.payments_db if p.booking_id == booking_id]
    
    def get_payment_status(self, payment_id: str) -> Optional[str]:
        """Отримати статус платежу"""
        payment = self.get_payment_by_id(payment_id)
        return payment.status if payment else None
    
    def get_available_methods(self) -> Dict[str, Dict]:
        """Отримати доступні методи оплати"""
        return {
            method: {
                'id': method,
                'name': data['name'],
                'icon': data['icon'],
                'fee': data['fee'],
                'fee_percentage': data['fee'] * 100,
                'enabled': data['enabled']
            }
            for method, data in self.payment_methods.items()
            if data['enabled']
        }
    
    def generate_payment_link(self, booking_id: str, amount: float) -> str:
        """
        Генерація посилання для оплати
        
        Args:
            booking_id: ID бронювання
            amount: Сума
            
        Returns:
            str: Посилання для оплати
        """
        token = hashlib.sha256(
            f"{booking_id}:{amount}:{self.secret_key}".encode()
        ).hexdigest()
        
        return f"https://payment.flightbooking.com/pay?booking={booking_id}&amount={amount}&token={token}"
    
    def verify_payment_signature(self, data: Dict[str, Any]) -> bool:
        """
        Перевірка підпису платежу
        
        Args:
            data: Дані з підписом
            
        Returns:
            bool: True якщо підпис вірний
        """
        signature = data.get('signature')
        if not signature:
            return False
        
        # Створення підпису
        payload = {k: v for k, v in data.items() if k != 'signature'}
        payload_str = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def _validate_card_number(self, card_number: str) -> bool:
        """
        Валідація номера картки за алгоритмом Luhn
        """
        # Видаляємо пробіли
        card_number = card_number.replace(' ', '').replace('-', '')
        
        # Перевіряємо що це цифри
        if not card_number.isdigit():
            return False
        
        # Перевіряємо довжину (16 цифр)
        if len(card_number) != 16:
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
    
    def _validate_expiry_date(self, expiry_date: str) -> bool:
        """
        Валідація терміну дії картки (MM/YY)
        """
        try:
            month, year = expiry_date.split('/')
            month = int(month)
            year = int(year) + 2000 if int(year) < 100 else int(year)
            
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
    
    def _detect_card_type(self, card_number: str) -> str:
        """
        Визначення типу картки за номером
        """
        card_number = card_number.replace(' ', '').replace('-', '')
        
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
    
    def calculate_payment_fee(self, amount: float, method: str) -> float:
        """
        Розрахунок комісії за оплату
        
        Args:
            amount: Сума
            method: Метод оплати
            
        Returns:
            float: Сума комісії
        """
        if method not in self.payment_methods:
            return 0.0
        
        fee = self.payment_methods[method]['fee']
        return amount * fee
    
    def calculate_total_with_fee(self, amount: float, method: str) -> float:
        """
        Розрахунок загальної суми з комісією
        
        Args:
            amount: Сума
            method: Метод оплати
            
        Returns:
            float: Загальна сума
        """
        fee = self.calculate_payment_fee(amount, method)
        return amount + fee
