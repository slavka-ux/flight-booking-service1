"""
Моделі бронювання та пасажира – ОБ'ЄДНАНА ВЕРСІЯ
Включає всі поля з усіх гілок:
- booking-system: базові поля, статуси
- user-auth: прив'язка до користувача
- payment-integration: платежі, оплата
- admin-panel: адмін-поля (confirmed_by, cancelled_by, тощо)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid


# ================================================================
#  МОДЕЛЬ ПАСАЖИРА
# ================================================================

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


# ================================================================
#  МОДЕЛЬ ПЛАТЕЖУ
# ================================================================

@dataclass
class Payment:
    """Модель платежу"""
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
        self.status = 'completed'
        self.transaction_id = transaction_id
        self.payment_date = datetime.now()
        self.receipt_url = receipt_url
        self.updated_at = datetime.now()

    def fail(self, error_message: str):
        self.status = 'failed'
        self.error_message = error_message
        self.updated_at = datetime.now()

    def refund(self):
        self.status = 'refunded'
        self.updated_at = datetime.now()

    def is_completed(self) -> bool:
        return self.status == 'completed'


# ================================================================
#  МОДЕЛЬ БРОНЮВАННЯ
# ================================================================

@dataclass
class Booking:
    """Модель бронювання (повна)"""
    # Ідентифікація
    booking_id: str = field(default_factory=lambda: f"BK-{uuid.uuid4().hex[:8].upper()}")
    user_id: str = ""
    flight_id: str = ""
    confirmation_code: str = field(default_factory=lambda: uuid.uuid4().hex[:8].upper())

    # Деталі
    seats: int = 1
    total_price: float = 0.0
    status: str = "pending"  # pending, confirmed, cancelled, completed

    # Пасажири
    passengers: List[Passenger] = field(default_factory=list)

    # Час
    booking_date: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Оплата
    payment_status: str = "unpaid"  # unpaid, paid, refunded, partially_paid
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    payments: List[Payment] = field(default_factory=list)
    total_paid: float = 0.0
    refund_amount: float = 0.0

    # Додаткове
    seat_numbers: List[str] = field(default_factory=list)
    insurance_purchased: bool = False
    special_requests: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    # Адмін-поля (хто і коли виконав дію)
    confirmed_by: Optional[str] = None
    confirmed_date: Optional[datetime] = None
    cancelled_by: Optional[str] = None
    cancellation_reason: Optional[str] = None
    cancellation_date: Optional[datetime] = None
    completed_by: Optional[str] = None
    completed_date: Optional[datetime] = None

    # ============================================================
    #  СЕРІАЛІЗАЦІЯ
    # ============================================================

    def to_dict(self) -> dict:
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'flight_id': self.flight_id,
            'confirmation_code': self.confirmation_code,
            'seats': self.seats,
            'total_price': self.total_price,
            'status': self.status,
            'passengers': [p.to_dict() for p in self.passengers],
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payments': [p.to_dict() for p in self.payments],
            'total_paid': self.total_paid,
            'refund_amount': self.refund_amount,
            'seat_numbers': self.seat_numbers,
            'insurance_purchased': self.insurance_purchased,
            'special_requests': self.special_requests,
            'notes': self.notes,
            'confirmed_by': self.confirmed_by,
            'confirmed_date': self.confirmed_date.isoformat() if self.confirmed_date else None,
            'cancelled_by': self.cancelled_by,
            'cancellation_reason': self.cancellation_reason,
            'cancellation_date': self.cancellation_date.isoformat() if self.cancellation_date else None,
            'completed_by': self.completed_by,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Booking':
        booking_date = None
        created_at = None
        updated_at = None
        payment_date = None
        confirmed_date = None
        cancellation_date = None
        completed_date = None

        if data.get('booking_date'):
            try:
                booking_date = datetime.fromisoformat(data['booking_date'])
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
        if data.get('payment_date'):
            try:
                payment_date = datetime.fromisoformat(data['payment_date'])
            except (ValueError, TypeError):
                pass
        if data.get('confirmed_date'):
            try:
                confirmed_date = datetime.fromisoformat(data['confirmed_date'])
            except (ValueError, TypeError):
                pass
        if data.get('cancellation_date'):
            try:
                cancellation_date = datetime.fromisoformat(data['cancellation_date'])
            except (ValueError, TypeError):
                pass
        if data.get('completed_date'):
            try:
                completed_date = datetime.fromisoformat(data['completed_date'])
            except (ValueError, TypeError):
                pass

        passengers = [Passenger.from_dict(p) for p in data.get('passengers', [])]
        payments = [Payment.from_dict(p) for p in data.get('payments', [])]

        return cls(
            booking_id=data.get('booking_id', f"BK-{uuid.uuid4().hex[:8].upper()}"),
            user_id=data.get('user_id', ''),
            flight_id=data.get('flight_id', ''),
            confirmation_code=data.get('confirmation_code', uuid.uuid4().hex[:8].upper()),
            seats=int(data.get('seats', 1)),
            total_price=float(data.get('total_price', 0)),
            status=data.get('status', 'pending'),
            passengers=passengers,
            booking_date=booking_date or datetime.now(),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
            payment_status=data.get('payment_status', 'unpaid'),
            payment_method=data.get('payment_method'),
            payment_date=payment_date,
            payments=payments,
            total_paid=float(data.get('total_paid', 0)),
            refund_amount=float(data.get('refund_amount', 0)),
            seat_numbers=data.get('seat_numbers', []),
            insurance_purchased=bool(data.get('insurance_purchased', False)),
            special_requests=data.get('special_requests', []),
            notes=data.get('notes'),
            confirmed_by=data.get('confirmed_by'),
            confirmed_date=confirmed_date,
            cancelled_by=data.get('cancelled_by'),
            cancellation_reason=data.get('cancellation_reason'),
            cancellation_date=cancellation_date,
            completed_by=data.get('completed_by'),
            completed_date=completed_date
        )

    # ============================================================
    #  БІЗНЕС-МЕТОДИ
    # ============================================================

    def confirm(self, admin_id: str = None):
        self.status = 'confirmed'
        self.confirmed_by = admin_id
        self.confirmed_date = datetime.now()
        self.updated_at = datetime.now()

    def cancel(self, admin_id: str = None, reason: str = None):
        self.status = 'cancelled'
        self.cancelled_by = admin_id
        self.cancellation_reason = reason
        self.cancellation_date = datetime.now()
        self.updated_at = datetime.now()

    def complete(self, admin_id: str = None):
        self.status = 'completed'
        self.completed_by = admin_id
        self.completed_date = datetime.now()
        self.updated_at = datetime.now()

    def add_payment(self, payment: Payment):
        self.payments.append(payment)
        self.total_paid += payment.amount
        if payment.is_completed():
            self.payment_status = 'paid'
            self.payment_method = payment.method
            self.payment_date = payment.payment_date
        self.updated_at = datetime.now()

    def is_fully_paid(self) -> bool:
        return self.total_paid >= self.total_price

    def is_partially_paid(self) -> bool:
        return 0 < self.total_paid < self.total_price

    def get_remaining_amount(self) -> float:
        return self.total_price - self.total_paid

    # ============================================================
    #  ДОПОМІЖНІ МЕТОДИ
    # ============================================================

    def get_status_ukrainian(self) -> str:
        status_map = {
            'pending': 'Очікує',
            'confirmed': 'Підтверджено',
            'cancelled': 'Скасовано',
            'completed': 'Завершено'
        }
        return status_map.get(self.status, 'Невідомо')

    def get_status_emoji(self) -> str:
        emojis = {
            'pending': '⏳',
            'confirmed': '✅',
            'cancelled': '❌',
            'completed': '🎯'
        }
        return emojis.get(self.status, '❓')

    def get_payment_status_ukrainian(self) -> str:
        status_map = {
            'unpaid': 'Не оплачено',
            'paid': 'Оплачено',
            'refunded': 'Повернуто',
            'partially_paid': 'Частково оплачено'
        }
        return status_map.get(self.payment_status, 'Невідомо')

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
