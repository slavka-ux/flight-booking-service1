"""
Модель рейсу (доповнена для бронювання)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Flight:
    flight_id: str = field(default_factory=lambda: f"FL-{uuid.uuid4().hex[:8].upper()}")
    airline: str = ""
    origin: str = ""
    destination: str = ""
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: float = 0.0
    available_seats: int = 0
    flight_number: str = ""
    aircraft: str = ""
    terminal: str = ""
    gate: str = ""
    status: str = "scheduled"

    def to_dict(self) -> dict:
        return {
            'flight_id': self.flight_id,
            'airline': self.airline,
            'origin': self.origin,
            'destination': self.destination,
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'price': self.price,
            'available_seats': self.available_seats,
            'flight_number': self.flight_number,
            'aircraft': self.aircraft,
            'terminal': self.terminal,
            'gate': self.gate,
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Flight':
        departure_time = None
        arrival_time = None
        if data.get('departure_time'):
            try:
                departure_time = datetime.fromisoformat(data['departure_time'])
            except (ValueError, TypeError):
                pass
        if data.get('arrival_time'):
            try:
                arrival_time = datetime.fromisoformat(data['arrival_time'])
            except (ValueError, TypeError):
                pass

        return cls(
            flight_id=data.get('flight_id', f"FL-{uuid.uuid4().hex[:8].upper()}"),
            airline=data.get('airline', ''),
            origin=data.get('origin', ''),
            destination=data.get('destination', ''),
            departure_time=departure_time,
            arrival_time=arrival_time,
            price=float(data.get('price', 0)),
            available_seats=int(data.get('available_seats', 0)),
            flight_number=data.get('flight_number', ''),
            aircraft=data.get('aircraft', ''),
            terminal=data.get('terminal', ''),
            gate=data.get('gate', ''),
            status=data.get('status', 'scheduled')
        )

    def has_available_seats(self, seats: int = 1) -> bool:
        return self.available_seats >= seats

    def book_seats(self, seats: int = 1) -> bool:
        if self.has_available_seats(seats):
            self.available_seats -= seats
            return True
        return False

    def release_seats(self, seats: int = 1) -> None:
        self.available_seats += seats

    def get_route(self) -> str:
        return f"{self.origin} → {self.destination}"
