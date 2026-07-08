"""
Сервіс для роботи з рейсами (оновлений з адмін-функціями)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.flight import Flight
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class FlightService:
    """Сервіс управління рейсами з адмін-функціями"""
    
    def __init__(self):
        self.flights: List[Flight] = []
        self._load_flights()
    
    def _load_flights(self):
        data = Config.get_flights()
        self.flights = [Flight.from_dict(item) for item in data]
        logger.info(f"Завантажено {len(self.flights)} рейсів")
    
    def _save_flights(self):
        data = [f.to_dict() for f in self.flights]
        Config.save_data(Config.FLIGHTS_FILE, data)
        logger.info(f"Збережено {len(self.flights)} рейсів")
    
    def search_flights(self, origin: str, destination: str, 
                       date: Optional[str] = None) -> List[Flight]:
        results = []
        for flight in self.flights:
            if not flight.is_active:
                continue
            if flight.origin.lower() == origin.lower() and \
               flight.destination.lower() == destination.lower():
                if date:
                    try:
                        search_date = datetime.fromisoformat(date).date()
                        flight_date = flight.departure_time.date()
                        if flight_date == search_date:
                            results.append(flight)
                    except ValueError:
                        continue
                else:
                    results.append(flight)
        return results
    
    def get_flight_by_id(self, flight_id: str) -> Optional[Flight]:
        for flight in self.flights:
            if flight.flight_id == flight_id:
                return flight
        return None
    
    def get_flight_by_number(self, flight_number: str) -> Optional[Flight]:
        for flight in self.flights:
            if flight.flight_number == flight_number:
                return flight
        return None
    
    def add_flight(self, flight_data: dict, admin_id: str = None) -> Flight:
        if flight_data.get('flight_number'):
            existing = self.get_flight_by_number(flight_data['flight_number'])
            if existing:
                raise ValueError(f"Рейс з номером {flight_data['flight_number']} вже існує")
        
        flight = Flight.from_dict(flight_data)
        flight.created_by = admin_id
        flight.updated_by = admin_id
        self.flights.append(flight)
        self._save_flights()
        logger.info(f"Додано рейс: {flight.flight_number} (адмін: {admin_id})")
        return flight
    
    def update_flight(self, flight_id: str, update_data: dict, admin_id: str = None) -> Optional[Flight]:
        flight = self.get_flight_by_id(flight_id)
        if flight:
            allowed_fields = ['airline', 'origin', 'destination', 'departure_time', 
                            'arrival_time', 'price', 'available_seats', 'status',
                            'aircraft', 'terminal', 'gate', 'baggage_allowance',
                            'cabin_class', 'meal_service', 'wifi_available', 'notes']
            
            for key, value in update_data.items():
                if key in allowed_fields and hasattr(flight, key):
                    if key in ['departure_time', 'arrival_time'] and value:
                        setattr(flight, key, datetime.fromisoformat(value))
                    else:
                        setattr(flight, key, value)
            
            flight.updated_by = admin_id
            flight.updated_at = datetime.now()
            self._save_flights()
            logger.info(f"Оновлено рейс: {flight.flight_number} (адмін: {admin_id})")
            return flight
        return None
    
    def delete_flight(self, flight_id: str, admin_id: str = None) -> bool:
        flight = self.get_flight_by_id(flight_id)
        if flight:
            self.flights.remove(flight)
            self._save_flights()
            logger.info(f"Видалено рейс: {flight.flight_number} (адмін: {admin_id})")
            return True
        return False
    
    def toggle_flight_active(self, flight_id: str, admin_id: str = None) -> Optional[Flight]:
        flight = self.get_flight_by_id(flight_id)
        if flight:
            flight.is_active = not flight.is_active
            flight.updated_by = admin_id
            flight.updated_at = datetime.now()
            self._save_flights()
            status = "активовано" if flight.is_active else "деактивовано"
            logger.info(f"{status} рейс: {flight.flight_number} (адмін: {admin_id})")
            return flight
        return None
    
    def get_all_flights(self, include_inactive: bool = False) -> List[Flight]:
        if include_inactive:
            return self.flights.copy()
        return [f for f in self.flights if f.is_active]
    
    def get_available_flights(self) -> List[Flight]:
        return [f for f in self.flights if f.is_active and f.available_seats > 0]
    
    def get_flights_by_origin(self, origin: str) -> List[Flight]:
        return [f for f in self.flights if f.origin.lower() == origin.lower()]
    
    def get_flights_by_destination(self, destination: str) -> List[Flight]:
        return [f for f in self.flights if f.destination.lower() == destination.lower()]
    
    def get_flights_by_airline(self, airline: str) -> List[Flight]:
        return [f for f in self.flights if f.airline.lower() == airline.lower()]
    
    def get_flights_by_status(self, status: str) -> List[Flight]:
        return [f for f in self.flights if f.status == status]
    
    def get_flights_today(self) -> List[Flight]:
        today = datetime.now().date()
        return [f for f in self.flights if f.departure_time and f.departure_time.date() == today]
    
    def get_flights_upcoming(self, days: int = 7) -> List[Flight]:
        now = datetime.now()
        end = now + timedelta(days=days)
        return [f for f in self.flights if f.departure_time and now <= f.departure_time <= end]
    
    def get_stats(self) -> Dict[str, Any]:
        total = len(self.flights)
        active = len([f for f in self.flights if f.is_active])
        scheduled = len([f for f in self.flights if f.status == 'scheduled'])
        delayed = len([f for f in self.flights if f.status == 'delayed'])
        cancelled = len([f for f in self.flights if f.status == 'cancelled'])
        completed = len([f for f in self.flights if f.status == 'completed'])
        total_seats = sum(f.available_seats for f in self.flights if f.is_active)
        
        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'scheduled': scheduled,
            'delayed': delayed,
            'cancelled': cancelled,
            'completed': completed,
            'total_seats': total_seats,
            'avg_price': sum(f.price for f in self.flights) / total if total > 0 else 0
      }
