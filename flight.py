"""
Модель рейсу з адмін-функціями
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import uuid
import json


@dataclass
class Flight:
    """Модель авіарейсу з адмін-функціями"""
    
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
    status: str = "scheduled"  # scheduled, delayed, cancelled, completed
    duration: int = 0
    stops: List[str] = field(default_factory=list)
    baggage_allowance: int = 20
    cabin_class: str = "economy"
    meal_service: bool = True
    wifi_available: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None  # ID адміністратора, який створив
    updated_by: Optional[str] = None  # ID адміністратора, який оновив
    is_active: bool = True
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.departure_time and self.arrival_time:
            if self.duration == 0:
                delta = self.arrival_time - self.departure_time
                self.duration = int(delta.total_seconds() / 60)
    
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
            'status': self.status,
            'duration': self.duration,
            'stops': self.stops,
            'baggage_allowance': self.baggage_allowance,
            'cabin_class': self.cabin_class,
            'meal_service': self.meal_service,
            'wifi_available': self.wifi_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'is_active': self.is_active,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Flight':
        departure_time = None
        arrival_time = None
        created_at = None
        updated_at = None
        
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
            status=data.get('status', 'scheduled'),
            duration=int(data.get('duration', 0)),
            stops=data.get('stops', []),
            baggage_allowance=int(data.get('baggage_allowance', 20)),
            cabin_class=data.get('cabin_class', 'economy'),
            meal_service=bool(data.get('meal_service', True)),
            wifi_available=bool(data.get('wifi_available', False)),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
            created_by=data.get('created_by'),
            updated_by=data.get('updated_by'),
            is_active=bool(data.get('is_active', True)),
            notes=data.get('notes')
        )
    
    def has_available_seats(self, seats: int = 1) -> bool:
        return self.available_seats >= seats
    
    def book_seats(self, seats: int = 1) -> bool:
        if self.has_available_seats(seats):
            self.available_seats -= seats
            self.updated_at = datetime.now()
            return True
        return False
    
    def release_seats(self, seats: int = 1) -> bool:
        self.available_seats += seats
        self.updated_at = datetime.now()
        return True
    
    def get_status_ukrainian(self) -> str:
        status_map = {
            'scheduled': 'Заплановано',
            'delayed': 'Затримано',
            'cancelled': 'Скасовано',
            'completed': 'Завершено'
        }
        return status_map.get(self.status, 'Невідомо')
    
    def get_status_emoji(self) -> str:
        status_emojis = {
            'scheduled': '✅',
            'delayed': '⏰',
            'cancelled': '❌',
            'completed': '✅'
        }
        return status_emojis.get(self.status, '❓')
    
    def __str__(self) -> str:
        return f"Flight({self.flight_number}: {self.origin} → {self.destination})"
