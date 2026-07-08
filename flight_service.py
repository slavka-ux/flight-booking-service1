"""
Сервіс для роботи з рейсами – ОБ'ЄДНАНА ВЕРСІЯ
Включає всі методи з усіх гілок:
- flight-search: пошук, фільтрація, отримання даних
- booking-system: book_seats, release_seats (через модель)
- admin-panel: CRUD, toggle active, статистика, адмін-поля
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from src.models.flight import Flight
from src.config import Config

logger = logging.getLogger(__name__)


class FlightService:
    """Сервіс управління рейсами (повний)"""

    def __init__(self, data_file: str = None):
        if data_file is None:
            base_dir = Path(__file__).parent.parent.parent
            data_file = base_dir / 'data' / 'flights.json'
        self.data_file = Path(data_file)
        self.flights: List[Flight] = []
        self._load_flights()

    # ============================================================
    #  РОБОТА З ФАЙЛОМ
    # ============================================================

    def _load_flights(self):
        if not self.data_file.exists():
            self.flights = []
            logger.warning(f"Файл рейсів не знайдено: {self.data_file}")
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.flights = [Flight.from_dict(item) for item in data]
                logger.info(f"Завантажено {len(self.flights)} рейсів")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Помилка завантаження рейсів: {e}")
            self.flights = []

    def _save_flights(self):
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([f.to_dict() for f in self.flights], f, ensure_ascii=False, indent=2)
            logger.info(f"Збережено {len(self.flights)} рейсів")
        except IOError as e:
            logger.error(f"Помилка запису рейсів: {e}")
            raise RuntimeError("Не вдалося зберегти дані рейсів") from e

    # ============================================================
    #  ПОШУК ТА ОТРИМАННЯ ДАНИХ (flight-search)
    # ============================================================

    def search(self, origin: str, destination: str, date: Optional[str] = None) -> List[Flight]:
        """Пошук рейсів за напрямком та датою"""
        results = []
        origin_lower = origin.strip().lower()
        destination_lower = destination.strip().lower()

        for flight in self.flights:
            if not flight.is_active:
                continue
            if flight.origin.lower() != origin_lower:
                continue
            if flight.destination.lower() != destination_lower:
                continue

            if date:
                try:
                    search_date = datetime.fromisoformat(date).date()
                    flight_date = flight.departure_time.date() if flight.departure_time else None
                    if flight_date != search_date:
                        continue
                except (ValueError, AttributeError):
                    continue

            results.append(flight)

        results.sort(key=lambda f: f.departure_time or datetime.max)
        return results

    def get_by_id(self, flight_id: str) -> Optional[Flight]:
        for flight in self.flights:
            if flight.flight_id == flight_id:
                return flight
        return None

    def get_by_number(self, flight_number: str) -> Optional[Flight]:
        for flight in self.flights:
            if flight.flight_number.lower() == flight_number.lower():
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

    def get_origins(self) -> List[str]:
        return sorted(set(f.origin for f in self.flights if f.is_active))

    def get_destinations(self) -> List[str]:
        return sorted(set(f.destination for f in self.flights if f.is_active))

    # ============================================================
    #  АДМІН-ОПЕРАЦІЇ (admin-panel)
    # ============================================================

    def add_flight(self, flight_data: dict, admin_id: str = None) -> Flight:
        """Додає новий рейс (адмін)"""
        if flight_data.get('flight_number'):
            existing = self.get_by_number(flight_data['flight_number'])
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
        """Оновлює рейс (адмін)"""
        flight = self.get_by_id(flight_id)
        if not flight:
            return None

        allowed_fields = [
            'airline', 'origin', 'destination', 'departure_time', 'arrival_time',
            'price', 'available_seats', 'status', 'aircraft', 'terminal', 'gate',
            'baggage_allowance', 'cabin_class', 'meal_service', 'wifi_available',
            'notes', 'flight_number'
        ]

        for key, value in update_data.items():
            if key in allowed_fields and hasattr(flight, key):
                if key in ['departure_time', 'arrival_time'] and value:
                    try:
                        setattr(flight, key, datetime.fromisoformat(value))
                    except (ValueError, TypeError):
                        pass
                else:
                    setattr(flight, key, value)

        flight.updated_by = admin_id
        flight.updated_at = datetime.now()
        self._save_flights()
        logger.info(f"Оновлено рейс: {flight.flight_number} (адмін: {admin_id})")
        return flight

    def delete_flight(self, flight_id: str, admin_id: str = None) -> bool:
        """Видаляє рейс (адмін)"""
        flight = self.get_by_id(flight_id)
        if not flight:
            return False
        self.flights.remove(flight)
        self._save_flights()
        logger.info(f"Видалено рейс: {flight.flight_number} (адмін: {admin_id})")
        return True

    def toggle_flight_active(self, flight_id: str, admin_id: str = None) -> Optional[Flight]:
        """Активує/деактивує рейс (адмін)"""
        flight = self.get_by_id(flight_id)
        if not flight:
            return None
        flight.is_active = not flight.is_active
        flight.updated_by = admin_id
        flight.updated_at = datetime.now()
        self._save_flights()
        status = "активовано" if flight.is_active else "деактивовано"
        logger.info(f"{status} рейс: {flight.flight_number} (адмін: {admin_id})")
        return flight

    # ============================================================
    #  СТАТИСТИКА
    # ============================================================

    def get_stats(self) -> Dict[str, Any]:
        """Отримує статистику по рейсах"""
        total = len(self.flights)
        active = len([f for f in self.flights if f.is_active])
        inactive = total - active

        scheduled = len([f for f in self.flights if f.status == 'scheduled'])
        delayed = len([f for f in self.flights if f.status == 'delayed'])
        cancelled = len([f for f in self.flights if f.status == 'cancelled'])
        completed = len([f for f in self.flights if f.status == 'completed'])

        total_seats = sum(f.available_seats for f in self.flights if f.is_active)
        total_price = sum(f.price for f in self.flights)

        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'scheduled': scheduled,
            'delayed': delayed,
            'cancelled': cancelled,
            'completed': completed,
            'total_seats': total_seats,
            'avg_price': total_price / total if total > 0 else 0,
            'total_price': total_price
      }
