"""
Модель бронювання з підтримкою оплати
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import json


@dataclass
class Passenger:
    """Модель пасажира"""
    
    passenger_id: str = field(default_factory=lambda: f"P-{uuid.uuid4().hex[:8].upper()}")
    name: str = ""
    passport: str = ""
    birth_date: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    special_needs: List[str] = field(default_factory=list)
    seat_preference: Optional[str] = None
    checked_bags: int = 0
    carry_on_bags: int = 1
    
    def to_dict(self) -> dict:
        return {
            'passenger_id': self.passenger_id,
            'name': self.name,
            'passport': self.passport,
            'birth_date': self.birth_date,
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender,
            'nationality': self.nationality,
            'special_needs': self.special_needs,
            'seat_preference': self.seat_preference,
            'checked_bags': self.checked_bags,
            'carry_on_bags': self.carry_on_bags
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Passenger':
        return cls(
            passenger_id=data.get('passenger_id', f"P-{uuid.uuid4().hex[:8].upper()}"),
            name=data.get('name', ''),
            passport=data.get('passport', ''),
            birth_date=data.get('birth_date'),
            email=data.get('email'),
            phone=data.get('phone'),
            gender=data.get('gender'),
            nationality=data.get('nationality'),
            special_needs=data.get('special_needs', []),
            seat_preference=data.get('seat_preference'),
            checked_bags=int(data.get('checked_bags', 0)),
            carry_on_bags=int(data.get('carry_on_bags', 1))
        )


@dataclass
class Payment:
    """
    Модель оплати
    
    Attributes:
        payment_id (str): Унікальний ID платежу
        booking_id (str): ID бронювання
        amount (float): Сума платежу
        currency (str): Валюта (UAH, USD, EUR)
        status (str): Статус платежу (pending, completed, failed, refunded)
        method (str): Метод оплати (card, cash, bank_transfer, google_pay, apple_pay)
        transaction_id (str): ID транзакції в платіжній системі
        payment_date (datetime): Дата оплати
        card_last_digits (str): Останні 4 цифри картки
        card_type (str): Тип картки (Visa, Mastercard, etc.)
        receipt_url (str): URL чеку
        error_message (str): Повідомлення про помилку
        metadata (Dict[str, Any]): Додаткові дані
        created_at (datetime): Дата створення
        updated_at (datetime): Дата оновлення
    """
    
    payment_id: str = field(default_factory=lambda: f"PAY-{uuid.uuid4().hex[:8].upper()}")
    booking_id: str = ""
    amount: float = 0.0
    currency: str = "UAH"
    status: str = "pending"  # pending, completed, failed, refunded
    method: str = "card"
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    card_last_digits: Optional[str] = None
    card_type: Optional[str] = None
    receipt_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'payment_id': self.payment_id,
            'booking_id': self.booking_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'method': self.method,
            'transaction_id': self.transaction_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'card_last_digits': self.card_last_digits,
            'card_type': self.card_type,
            'receipt_url': self.receipt_url,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Payment':
        payment_date = None
        created_at = None
        updated_at = None
        
        if data.get('payment_date'):
            try:
                payment_date = datetime.fromisoformat(data['payment_date'])
            except (ValueError, TypeError):
                pass
        
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                pass
        
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                pass
        
        return cls(
            payment_id=data.get('payment_id', f"PAY-{uuid.uuid4().hex[:8].upper()}"),
            booking_id=data.get('booking_id', ''),
            amount=float(data.get('amount', 0)),
            currency=data.get('currency', 'UAH'),
            status=data.get('status', 'pending'),
            method=data.get('method', 'card'),
            transaction_id=data.get('transaction_id'),
            payment_date=payment_date,
            card_last_digits=data.get('card_last_digits'),
            card_type=data.get('card_type'),
            receipt_url=data.get('receipt_url'),
            error_message=data.get('error_message'),
            metadata=data.get('metadata', {}),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )
    
    def complete(self, transaction_id: str, receipt_url: str = None):
        """Завершити оплату"""
        self.status = 'completed'
        self.transaction_id = transaction_id
        self.payment_date = datetime.now()
        self.receipt_url = receipt_url
        self.updated_at = datetime.now()
    
    def fail(self, error_message: str):
        """Відмінити оплату з помилкою"""
        self.status = 'failed'
        self.error_message = error_message
        self.updated_at = datetime.now()
    
    def refund(self):
        """Повернути оплату"""
        self.status = 'refunded'
        self.updated_at = datetime.now()
    
    def is_completed(self) -> bool:
        return self.status == 'completed'
    
    def is_failed(self) -> bool:
        return self.status == 'failed'
    
    def is_pending(self) -> bool:
        return self.status == 'pending'
    
    def is_refunded(self) -> bool:
        return self.status == 'refunded'
    
    def get_status_ukrainian(self) -> str:
        status_map = {
            'pending': 'В обробці',
            'completed': 'Оплачено',
            'failed': 'Помилка',
            'refunded': 'Повернуто'
        }
        return status_map.get(self.status, 'Невідомо')
    
    def get_status_emoji(self) -> str:
        status_emojis = {
            'pending': '⏳',
            'completed': '✅',
            'failed': '❌',
            'refunded': '↩️'
        }
        return status_emojis.get(self.status, '❓')
    
    def __str__(self) -> str:
        return f"Payment({self.payment_id}: {self.amount} {self.currency}, {self.status})"


@dataclass
class Booking:
    """
    Модель бронювання з підтримкою оплати
    """
    
    booking_id: str = field(default_factory=lambda: f"BK-{uuid.uuid4().hex[:8].upper()}")
    user_id: str = ""
    flight_id: str = ""
    seats: int = 1
    total_price: float = 0.0
    status: str = "pending"  # pending, confirmed, cancelled, completed
    booking_date: datetime = field(default_factory=datetime.now)
    passengers: List[Passenger] = field(default_factory=list)
    payment_status: str = "unpaid"  # unpaid, paid, refunded, partially_paid
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None
    confirmation_code: str = field(default_factory=lambda: uuid.uuid4().hex[:8].upper())
    seat_numbers: List[str] = field(default_factory=list)
    insurance_purchased: bool = False
    special_requests: List[str] = field(default_factory=list)
    payments: List[Payment] = field(default_factory=list)  # Історія платежів
    total_paid: float = 0.0
    refund_amount: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'flight_id': self.flight_id,
            'seats': self.seats,
            'total_price': self.total_price,
            'status': self.status,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'passengers': [p.to_dict() for p in self.passengers],
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'notes': self.notes,
            'confirmation_code': self.confirmation_code,
            'seat_numbers': self.seat_numbers,
            'insurance_purchased': self.insurance_purchased,
            'special_requests': self.special_requests,
            'payments': [p.to_dict() for p in self.payments],
            'total_paid': self.total_paid,
            'refund_amount': self.refund_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Booking':
        booking_date = None
        payment_date = None
        created_at = None
        updated_at = None
        
        if data.get('booking_date'):
            try:
                booking_date = datetime.fromisoformat(data['booking_date'])
            except (ValueError, TypeError):
                pass
        
        if data.get('payment_date'):
            try:
                payment_date = datetime.fromisoformat(data['payment_date'])
            except (ValueError, TypeError):
                pass
        
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                pass
        
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                pass
        
        passengers = [Passenger.from_dict(p) for p in data.get('passengers', [])]
        payments = [Payment.from_dict(p) for p in data.get('payments', [])]
        
        return cls(
            booking_id=data.get('booking_id', f"BK-{uuid.uuid4().hex[:8].upper()}"),
            user_id=data.get('user_id', ''),
            flight_id=data.get('flight_id', ''),
            seats=int(data.get('seats', 1)),
            total_price=float(data.get('total_price', 0)),
            status=data.get('status', 'pending'),
            booking_date=booking_date or datetime.now(),
            passengers=passengers,
            payment_status=data.get('payment_status', 'unpaid'),
            payment_method=data.get('payment_method'),
            payment_date=payment_date,
            notes=data.get('notes'),
            confirmation_code=data.get('confirmation_code', uuid.uuid4().hex[:8].upper()),
            seat_numbers=data.get('seat_numbers', []),
            insurance_purchased=bool(data.get('insurance_purchased', False)),
            special_requests=data.get('special_requests', []),
            payments=payments,
            total_paid=float(data.get('total_paid', 0)),
            refund_amount=float(data.get('refund_amount', 0)),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )
    
    def confirm(self):
        """Підтвердити бронювання"""
        self.status = 'confirmed'
        self.updated_at = datetime.now()
    
    def cancel(self):
        """Скасувати бронювання"""
        self.status = 'cancelled'
        self.updated_at = datetime.now()
    
    def complete(self):
        """Завершити бронювання"""
        self.status = 'completed'
        self.updated_at = datetime.now()
    
    def add_payment(self, payment: Payment):
        """Додати платіж"""
        self.payments.append(payment)
        self.total_paid += payment.amount
        
        if payment.is_completed():
            self.payment_status = 'paid'
            self.payment_method = payment.method
            self.payment_date = payment.payment_date
        
        self.updated_at = datetime.now()
    
    def get_remaining_amount(self) -> float:
        """Отримати залишок до оплати"""
        return self.total_price - self.total_paid
    
    def is_fully_paid(self) -> bool:
        """Перевірити чи повністю оплачено"""
        return self.total_paid >= self.total_price
    
    def is_partially_paid(self) -> bool:
        """Перевірити чи частково оплачено"""
        return 0 < self.total_paid < self.total_price
    
    def get_payment_status_ukrainian(self) -> str:
        status_map = {
            'unpaid': 'Не оплачено',
            'paid': 'Оплачено',
            'refunded': 'Повернуто',
            'partially_paid': 'Частково оплачено'
        }
        return status_map.get(self.payment_status, 'Невідомо')
    
    def get_status_ukrainian(self) -> str:
        status_map = {
            'pending': 'Очікує',
            'confirmed': 'Підтверджено',
            'cancelled': 'Скасовано',
            'completed': 'Завершено'
        }
        return status_map.get(self.status, 'Невідомо')
    
    def get_status_emoji(self) -> str:
        status_emojis = {
            'pending': '⏳',
            'confirmed': '✅',
            'cancelled': '❌',
            'completed': '🎯'
        }
        return status_emojis.get(self.status, '❓')
    
    def get_booking_summary(self) -> Dict[str, Any]:
        return {
            'booking_id': self.booking_id,
            'confirmation_code': self.confirmation_code,
            'flight_id': self.flight_id,
            'seats': self.seats,
            'passengers': len(self.passengers),
            'total_price': f"{self.total_price:,.0f} ₴",
            'total_paid': f"{self.total_paid:,.0f} ₴",
            'remaining': f"{self.get_remaining_amount():,.0f} ₴",
            'status': self.get_status_ukrainian(),
            'status_emoji': self.get_status_emoji(),
            'payment_status': self.get_payment_status_ukrainian(),
            'booking_date': self.booking_date.strftime('%d.%m.%Y %H:%M'),
            'is_fully_paid': self.is_fully_paid()
        }
    
    def __str__(self) -> str:
        return f"Booking({self.booking_id}: {self.flight_id}, {self.status})"
