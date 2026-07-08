"""
Модель рейсу – ОБ'ЄДНАНА ВЕРСІЯ
Включає всі поля та методи з усіх гілок:
- flight-search: базові поля та методи
- booking-system: book_seats, release_seats
- admin-panel: created_by, updated_by, is_active, notes
- payment-integration: додаткові поля (duration, stops, baggage_allowance, тощо)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import uuid


@dataclass
class Flight:
    """
    Модель авіарейсу (повна версія)
    """
    
    # ===== Ідентифікація =====
    flight_id: str = field(default_factory=lambda: f"FL-{uuid.uuid4().hex[:8].upper()}")
    flight_number: str = ""
    airline: str = ""
    
    # ===== Маршрут =====
    origin: str = ""
    destination: str = ""
    
    # ===== Час =====
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    duration: int = 0  # хвилини (автоматично розраховується)
    
    # ===== Ціна та місця =====
    price: float = 0.0
    available_seats: int = 0
    
    # ===== Деталі рейсу =====
    aircraft: str = ""
    terminal: str = ""
    gate: str = ""
    status: str = "scheduled"  # scheduled, delayed, cancelled, completed
    cabin_class: str = "economy"  # economy, business, first
    baggage_allowance: int = 20  # кг
    meal_service: bool = True
    wifi_available: bool = False
    stops: List[str] = field(default_factory=list)
    
    # ===== Адмін-поля =====
    is_active: bool = True
    created_by: Optional[str] = None   # ID адміністратора, який створив
    updated_by: Optional[str] = None   # ID адміністратора, який оновив
    notes: Optional[str] = None        # Додаткові нотатки
    
    # ===== Службові поля =====
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # ============================================================
    #  АВТОМАТИЧНІ ДІЇ ПІСЛЯ ІНІЦІАЛІЗАЦІЇ
    # ============================================================

    def __post_init__(self):
        """Автоматично розраховує тривалість, якщо вказано час"""
        if self.departure_time and self.arrival_time and self.duration == 0:
            delta = self.arrival_time - self.departure_time
            self.duration = int(delta.total_seconds() / 60)
    
    # ============================================================
    #  СЕРІАЛІЗАЦІЯ / ДЕСЕРІАЛІЗАЦІЯ
    # ============================================================

    def to_dict(self) -> dict:
        """Конвертує модель у словник для JSON"""
        return {
            # Ідентифікація
            'flight_id': self.flight_id,
            'flight_number': self.flight_number,
            'airline': self.airline,
            
            # Маршрут
            'origin': self.origin,
            'destination': self.destination,
            
            # Час
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'arrival_time': self.arrival_time.isoformat() if self.arrival_time else None,
            'duration': self.duration,
            
            # Ціна та місця
            'price': self.price,
            'available_seats': self.available_seats,
            
            # Деталі
            'aircraft': self.aircraft,
            'terminal': self.terminal,
            'gate': self.gate,
            'status': self.status,
            'cabin_class': self.cabin_class,
            'baggage_allowance': self.baggage_allowance,
            'meal_service': self.meal_service,
            'wifi_available': self.wifi_available,
            'stops': self.stops,
            
            # Адмін-поля
            'is_active': self.is_active,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'notes': self.notes,
            
            # Службові
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Flight':
        """Створює модель зі словника"""
        # Парсинг дат
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
            # Ідентифікація
            flight_id=data.get('flight_id', f"FL-{uuid.uuid4().hex[:8].upper()}"),
            flight_number=data.get('flight_number', ''),
            airline=data.get('airline', ''),
            
            # Маршрут
            origin=data.get('origin', ''),
            destination=data.get('destination', ''),
            
            # Час
            departure_time=departure_time,
            arrival_time=arrival_time,
            duration=int(data.get('duration', 0)),
            
            # Ціна та місця
            price=float(data.get('price', 0)),
            available_seats=int(data.get('available_seats', 0)),
            
            # Деталі
            aircraft=data.get('aircraft', ''),
            terminal=data.get('terminal', ''),
            gate=data.get('gate', ''),
            status=data.get('status', 'scheduled'),
            cabin_class=data.get('cabin_class', 'economy'),
            baggage_allowance=int(data.get('baggage_allowance', 20)),
            meal_service=bool(data.get('meal_service', True)),
            wifi_available=bool(data.get('wifi_available', False)),
            stops=data.get('stops', []),
            
            # Адмін-поля
            is_active=bool(data.get('is_active', True)),
            created_by=data.get('created_by'),
            updated_by=data.get('updated_by'),
            notes=data.get('notes'),
            
            # Службові
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )
    
    # ============================================================
    #  МЕТОДИ ДЛЯ РОБОТИ З МІСЦЯМИ
    # ============================================================

    def has_available_seats(self, seats: int = 1) -> bool:
        """Перевіряє наявність вільних місць"""
        return self.available_seats >= seats
    
    def book_seats(self, seats: int = 1) -> bool:
        """
        Бронює вказану кількість місць
        Повертає True, якщо бронювання успішне
        """
        if self.has_available_seats(seats):
            self.available_seats -= seats
            self.updated_at = datetime.now()
            return True
        return False
    
    def release_seats(self, seats: int = 1) -> None:
        """Звільняє заброньовані місця (при скасуванні)"""
        self.available_seats += seats
        self.updated_at = datetime.now()
    
    # ============================================================
    #  ДОПОМІЖНІ МЕТОДИ
    # ============================================================

    def get_route(self) -> str:
        """Повертає маршрут у вигляді рядка"""
        return f"{self.origin} → {self.destination}"
    
    def get_duration_string(self) -> str:
        """Повертає тривалість у форматі '2 год 30 хв'"""
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0 and minutes > 0:
            return f"{hours} год {minutes} хв"
        elif hours > 0:
            return f"{hours} год"
        else:
            return f"{minutes} хв"
    
    def get_status_ukrainian(self) -> str:
        """Повертає статус українською"""
        status_map = {
            'scheduled': 'Заплановано',
            'delayed': 'Затримано',
            'cancelled': 'Скасовано',
            'completed': 'Завершено'
        }
        return status_map.get(self.status, 'Невідомо')
    
    def get_status_emoji(self) -> str:
        """Повертає емодзі для статусу"""
        emojis = {
            'scheduled': '✅',
            'delayed': '⏰',
            'cancelled': '❌',
            'completed': '🎯'
        }
        return emojis.get(self.status, '❓')
    
    def get_cabin_class_ukrainian(self) -> str:
        """Повертає назву класу салону українською"""
        class_map = {
            'economy': 'Економ',
            'business': 'Бізнес',
            'first': 'Перший'
        }
        return class_map.get(self.cabin_class, 'Економ')
    
    # ============================================================
    #  ПЕРЕВІРКИ СТАТУСІВ
    # ============================================================

    def is_delayed(self) -> bool:
        return self.status == 'delayed'
    
    def is_cancelled(self) -> bool:
        return self.status == 'cancelled'
    
    def is_completed(self) -> bool:
        return self.status == 'completed'
    
    def is_scheduled(self) -> bool:
        return self.status == 'scheduled'
    
    def is_active_flight(self) -> bool:
        """Перевіряє, чи активний рейс (не скасований і не завершений)"""
        return self.is_active and self.status not in ['cancelled', 'completed']
    
    # ============================================================
    #  ПРЕДСТАВЛЕННЯ ОБ'ЄКТА
    # ============================================================

    def __str__(self) -> str:
        return f"Flight({self.flight_number}: {self.origin} → {self.destination})"
    
    def __repr__(self) -> str:
        return (f"Flight(flight_id='{self.flight_id}', "
                f"flight_number='{self.flight_number}', "
                f"airline='{self.airline}', "
                f"origin='{self.origin}', "
                f"destination='{self.destination}', "
                f"price={self.price}, "
                f"available_seats={self.available_seats}, "
                f"is_active={self.is_active})")
