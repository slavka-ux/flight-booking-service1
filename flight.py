"""
Модель рейсу для пошуку
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Flight:
    """
    Модель авіарейсу
    
    Attributes:
        flight_id (str): Унікальний ідентифікатор
        airline (str): Авіакомпанія
        origin (str): Місто вильоту
        destination (str): Місто прильоту
        departure_time (datetime): Час вильоту
        arrival_time (datetime): Час прильоту
        price (float): Ціна квитка
        available_seats (int): Доступні місця
        flight_number (str): Номер рейсу
        aircraft (str): Тип літака
        terminal (str): Термінал
        gate (str): Вихід
        status (str): Статус рейсу
    """
    
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
    
    def to_dict(self) -> dict:
        """Конвертує модель у словник для JSON"""
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
        """Створює модель зі словника"""
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
        """Перевіряє наявність вільних місць"""
        return self.available_seats >= seats
    
    def get_route(self) -> str:
        """Повертає маршрут у вигляді рядка"""
        return f"{self.origin} → {self.destination}"
    
    def get_duration(self) -> int:
        """Повертає тривалість польоту в хвилинах"""
        if self.departure_time and self.arrival_time:
            delta = self.arrival_time - self.departure_time
            return int(delta.total_seconds() / 60)
        return 0
    
    def get_duration_string(self) -> str:
        """Повертає тривалість у форматі '2 год 30 хв'"""
        minutes = self.get_duration()
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0 and mins > 0:
            return f"{hours} год {mins} хв"
        elif hours > 0:
            return f"{hours} год"
        else:
            return f"{mins} хв"
    
    def get_status_ukrainian(self) -> str:
        """Повертає статус українською"""
        status_map = {
            'scheduled': 'Заплановано',
            'delayed': 'Затримано',
            'cancelled': 'Скасовано',
            'completed': 'Завершено'
        }
        return status_map.get(self.status, 'Невідомо')
