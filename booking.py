"""
Модель бронювання
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class Passenger:
    """
    Модель пасажира
    """
    passenger_id: str = field(default_factory=lambda: f"P-{uuid.uuid4().hex[:8].upper()}")
    name: str = ""
    passport: str = ""
    birth_date: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'passenger_id': self.passenger_id,
            'name': self.name,
            'passport': self.passport,
            'birth_date': self.birth_date,
            'email': self.email,
            'phone': self.phone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Passenger':
        return cls(
            passenger_id=data.get('passenger_id', f"P-{uuid.uuid4().hex[:8].upper()}"),
            name=data.get('name', ''),
            passport=data.get('passport', ''),
            birth_date=data.get('birth_date'),
            email=data.get('email'),
            phone=data.get('phone')
        )


@dataclass
class Booking:
    """
    Модель бронювання
    """
    booking_id: str = field(default_factory=lambda: f"BK-{uuid.uuid4().hex[:8].upper()}")
    user_id: str = ""  # ID користувача (може бути тимчасовим)
    flight_id: str = ""
    seats: int = 1
    total_price: float = 0.0
    status: str = "pending"  # pending, confirmed, cancelled
    booking_date: datetime = field(default_factory=datetime.now)
    passengers: List[Passenger] = field(default_factory=list)
    notes: Optional[str] = None
    confirmation_code: str = field(default_factory=lambda: uuid.uuid4().hex[:8].upper())

    def to_dict(self) -> dict:
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'flight_id': self.flight_id,
            'seats': self.seats,
            'total_price': self.total_price,
            'status': self.status,
            'booking_date': self.booking_date.isoformat(),
            'passengers': [p.to_dict() for p in self.passengers],
            'notes': self.notes,
            'confirmation_code': self.confirmation_code
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Booking':
        booking_date = None
        if data.get('booking_date'):
            try:
                booking_date = datetime.fromisoformat(data['booking_date'])
            except (ValueError, TypeError):
                pass

        passengers = [Passenger.from_dict(p) for p in data.get('passengers', [])]

        return cls(
            booking_id=data.get('booking_id', f"BK-{uuid.uuid4().hex[:8].upper()}"),
            user_id=data.get('user_id', ''),
            flight_id=data.get('flight_id', ''),
            seats=int(data.get('seats', 1)),
            total_price=float(data.get('total_price', 0)),
            status=data.get('status', 'pending'),
            booking_date=booking_date or datetime.now(),
            passengers=passengers,
            notes=data.get('notes'),
            confirmation_code=data.get('confirmation_code', uuid.uuid4().hex[:8].upper())
        )

    def confirm(self):
        """Підтвердити бронювання"""
        self.status = 'confirmed'

    def cancel(self):
        """Скасувати бронювання"""
        self.status = 'cancelled'

    def get_status_ukrainian(self) -> str:
        status_map = {
            'pending': 'Очікує',
            'confirmed': 'Підтверджено',
            'cancelled': 'Скасовано'
        }
        return status_map.get(self.status, 'Невідомо')
