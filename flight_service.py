"""
Сервіс для роботи з рейсами (пошук)
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.models.flight import Flight


class FlightService:
    """Сервіс пошуку рейсів"""
    
    def __init__(self, data_file: str = None):
        """
        Ініціалізація сервісу
        
        Args:
            data_file: Шлях до файлу з даними рейсів (JSON)
        """
        if data_file is None:
            # За замовчуванням використовуємо файл у папці data
            base_dir = Path(__file__).parent.parent.parent
            data_file = base_dir / 'data' / 'flights.json'
        
        self.data_file = Path(data_file)
        self.flights: List[Flight] = []
        self._load_flights()
    
    def _load_flights(self):
        """Завантажує рейси з JSON файлу"""
        if not self.data_file.exists():
            # Якщо файлу немає, створюємо порожній список
            self.flights = []
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.flights = [Flight.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError):
            self.flights = []
    
    def _save_flights(self):
        """Зберігає рейси у JSON файл (для адміністрування)"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump([f.to_dict() for f in self.flights], f, ensure_ascii=False, indent=2)
    
    def search(self, origin: str, destination: str, date: Optional[str] = None) -> List[Flight]:
        """
        Пошук рейсів за напрямком та датою
        
        Args:
            origin: Місто вильоту
            destination: Місто прильоту
            date: Дата у форматі YYYY-MM-DD (опціонально)
            
        Returns:
            List[Flight]: Список знайдених рейсів
        """
        results = []
        origin_lower = origin.strip().lower()
        destination_lower = destination.strip().lower()
        
        for flight in self.flights:
            # Перевіряємо напрямок (ігноруємо регістр)
            if flight.origin.lower() != origin_lower:
                continue
            if flight.destination.lower() != destination_lower:
                continue
            
            # Якщо дата вказана, перевіряємо
            if date:
                try:
                    search_date = datetime.fromisoformat(date).date()
                    flight_date = flight.departure_time.date() if flight.departure_time else None
                    if flight_date != search_date:
                        continue
                except (ValueError, AttributeError):
                    # Якщо дата невалідна або немає часу вильоту, пропускаємо
                    continue
            
            results.append(flight)
        
        # Сортуємо за часом вильоту
        results.sort(key=lambda f: f.departure_time or datetime.max)
        return results
    
    def get_by_id(self, flight_id: str) -> Optional[Flight]:
        """Отримує рейс за ID"""
        for flight in self.flights:
            if flight.flight_id == flight_id:
                return flight
        return None
    
    def get_by_number(self, flight_number: str) -> Optional[Flight]:
        """Отримує рейс за номером"""
        for flight in self.flights:
            if flight.flight_number.lower() == flight_number.lower():
                return flight
        return None
    
    def get_all(self) -> List[Flight]:
        """Повертає всі рейси"""
        return self.flights.copy()
    
    def add_flight(self, flight_data: dict) -> Flight:
        """Додає новий рейс (для тестування або адміністрування)"""
        flight = Flight.from_dict(flight_data)
        # Перевірка на дублікат за номером
        if self.get_by_number(flight.flight_number):
            raise ValueError(f"Рейс з номером {flight.flight_number} вже існує")
        self.flights.append(flight)
        self._save_flights()
        return flight
    
    def get_origins(self) -> List[str]:
        """Повертає список унікальних міст вильоту"""
        return sorted(set(f.origin for f in self.flights))
    
    def get_destinations(self) -> List[str]:
        """Повертає список унікальних міст прильоту"""
        return sorted(set(f.destination for f in self.flights))
