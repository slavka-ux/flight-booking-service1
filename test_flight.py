"""
Тести для моделі та сервісу рейсів
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from src.models.flight import Flight
from src.services.flight_service import FlightService


class TestFlight:
    """Тести для моделі Flight"""
    
    def test_flight_creation(self):
        """Тест створення рейсу"""
        flight = Flight(
            airline="Test Air",
            origin="Київ",
            destination="Львів",
            departure_time=datetime(2026, 7, 10, 10, 0),
            arrival_time=datetime(2026, 7, 10, 11, 30),
            price=2500,
            available_seats=45,
            flight_number="TA-101"
        )
        
        assert flight.airline == "Test Air"
        assert flight.origin == "Київ"
        assert flight.destination == "Львів"
        assert flight.price == 2500
        assert flight.available_seats == 45
        assert flight.flight_number == "TA-101"
        assert flight.get_route() == "Київ → Львів"
    
    def test_flight_to_dict(self):
        """Тест конвертації в словник"""
        flight = Flight(
            flight_id="FL-TEST",
            airline="Test Air",
            origin="Київ",
            destination="Львів",
            departure_time=datetime(2026, 7, 10, 10, 0),
            arrival_time=datetime(2026, 7, 10, 11, 30),
            price=2500,
            available_seats=45,
            flight_number="TA-101"
        )
        
        data = flight.to_dict()
        assert data['flight_id'] == "FL-TEST"
        assert data['airline'] == "Test Air"
        assert data['price'] == 2500
        assert data['departure_time'] == "2026-07-10T10:00:00"
    
    def test_flight_from_dict(self):
        """Тест створення зі словника"""
        data = {
            'flight_id': 'FL-TEST',
            'airline': 'Test Air',
            'origin': 'Київ',
            'destination': 'Львів',
            'departure_time': '2026-07-10T10:00:00',
            'arrival_time': '2026-07-10T11:30:00',
            'price': 2500,
            'available_seats': 45,
            'flight_number': 'TA-101'
        }
        
        flight = Flight.from_dict(data)
        assert flight.flight_id == "FL-TEST"
        assert flight.airline == "Test Air"
        assert flight.departure_time == datetime(2026, 7, 10, 10, 0)
    
    def test_flight_duration(self):
        """Тест розрахунку тривалості"""
        flight = Flight(
            departure_time=datetime(2026, 7, 10, 10, 0),
            arrival_time=datetime(2026, 7, 10, 11, 30)
        )
        assert flight.get_duration() == 90
        assert flight.get_duration_string() == "1 год 30 хв"
    
    def test_flight_has_available_seats(self):
        """Тест наявності місць"""
        flight = Flight(available_seats=10)
        assert flight.has_available_seats(5) is True
        assert flight.has_available_seats(10) is True
        assert flight.has_available_seats(11) is False
    
    def test_flight_status_ukrainian(self):
        """Тест статусів українською"""
        assert Flight(status='scheduled').get_status_ukrainian() == "Заплановано"
        assert Flight(status='delayed').get_status_ukrainian() == "Затримано"
        assert Flight(status='cancelled').get_status_ukrainian() == "Скасовано"
        assert Flight(status='completed').get_status_ukrainian() == "Завершено"


class TestFlightService:
    """Тести для FlightService"""
    
    @pytest.fixture
    def temp_data_file(self, tmp_path):
        """Створює тимчасовий файл з даними"""
        data = [
            {
                'flight_id': 'FL-001',
                'airline': 'Sky Airlines',
                'origin': 'Київ',
                'destination': 'Львів',
                'departure_time': '2026-07-10T10:00:00',
                'arrival_time': '2026-07-10T11:30:00',
                'price': 2500,
                'available_seats': 45,
                'flight_number': 'SA-102',
                'status': 'scheduled'
            },
            {
                'flight_id': 'FL-002',
                'airline': 'EuroJet',
                'origin': 'Київ',
                'destination': 'Одеса',
                'departure_time': '2026-07-11T14:00:00',
                'arrival_time': '2026-07-11T15:30:00',
                'price': 3200,
                'available_seats': 32,
                'flight_number': 'EJ-205',
                'status': 'scheduled'
            }
        ]
        file_path = tmp_path / 'flights.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path
    
    def test_search_flights(self, temp_data_file):
        """Тест пошуку рейсів"""
        service = FlightService(data_file=temp_data_file)
        
        # Пошук за напрямком
        results = service.search('Київ', 'Львів')
        assert len(results) == 1
        assert results[0].flight_number == 'SA-102'
        
        # Пошук з датою
        results = service.search('Київ', 'Львів', '2026-07-10')
        assert len(results) == 1
        
        # Пошук з невірною датою
        results = service.search('Київ', 'Львів', '2026-07-11')
        assert len(results) == 0
        
        # Пошук неіснуючого маршруту
        results = service.search('Харків', 'Дніпро')
        assert len(results) == 0
    
    def test_get_by_id(self, temp_data_file):
        """Тест отримання рейсу за ID"""
        service = FlightService(data_file=temp_data_file)
        flight = service.get_by_id('FL-001')
        assert flight is not None
        assert flight.flight_number == 'SA-102'
        
        flight = service.get_by_id('FL-XXX')
        assert flight is None
    
    def test_get_by_number(self, temp_data_file):
        """Тест отримання рейсу за номером"""
        service = FlightService(data_file=temp_data_file)
        flight = service.get_by_number('SA-102')
        assert flight is not None
        assert flight.origin == 'Київ'
        
        flight = service.get_by_number('NONEXISTENT')
        assert flight is None
    
    def test_get_all(self, temp_data_file):
        """Тест отримання всіх рейсів"""
        service = FlightService(data_file=temp_data_file)
        all_flights = service.get_all()
        assert len(all_flights) == 2
    
    def test_add_flight(self, temp_data_file):
        """Тест додавання рейсу"""
        service = FlightService(data_file=temp_data_file)
        
        new_flight_data = {
            'airline': 'New Air',
            'origin': 'Харків',
            'destination': 'Київ',
            'departure_time': '2026-07-12T08:00:00',
            'arrival_time': '2026-07-12T09:00:00',
            'price': 1800,
            'available_seats': 50,
            'flight_number': 'NA-001',
            'status': 'scheduled'
        }
        
        flight = service.add_flight(new_flight_data)
        assert flight.flight_number == 'NA-001'
        
        # Перевіряємо, що додалося
        all_flights = service.get_all()
        assert len(all_flights) == 3
        
        # Перевіряємо дублікат
        with pytest.raises(ValueError):
            service.add_flight(new_flight_data)
    
    def test_get_origins_destinations(self, temp_data_file):
        """Тест отримання списків міст"""
        service = FlightService(data_file=temp_data_file)
        origins = service.get_origins()
        assert 'Київ' in origins
        assert len(origins) == 1  # тільки Київ
        
        destinations = service.get_destinations()
        assert 'Львів' in destinations
        assert 'Одеса' in destinations
        assert len(destinations) == 2
