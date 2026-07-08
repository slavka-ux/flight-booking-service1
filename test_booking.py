"""
Тести для бронювання
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from src.models.booking import Booking, Passenger
from src.services.booking_service import BookingService
from src.services.flight_service import FlightService


class TestBookingModel:
    def test_booking_creation(self):
        passenger = Passenger(name='Іван Петренко', passport='AA123456')
        booking = Booking(
            user_id='user-1',
            flight_id='FL-001',
            seats=2,
            total_price=5000,
            passengers=[passenger]
        )
        assert booking.user_id == 'user-1'
        assert booking.seats == 2
        assert booking.status == 'pending'
        assert len(booking.passengers) == 1

    def test_booking_confirm(self):
        booking = Booking(status='pending')
        booking.confirm()
        assert booking.status == 'confirmed'

    def test_booking_cancel(self):
        booking = Booking(status='pending')
        booking.cancel()
        assert booking.status == 'cancelled'

    def test_booking_to_dict(self):
        booking = Booking(
            booking_id='BK-001',
            user_id='user-1',
            flight_id='FL-001',
            seats=2,
            total_price=5000,
            status='pending'
        )
        data = booking.to_dict()
        assert data['booking_id'] == 'BK-001'
        assert data['user_id'] == 'user-1'
        assert data['total_price'] == 5000


class TestBookingService:
    @pytest.fixture
    def temp_files(self, tmp_path):
        flights_file = tmp_path / 'flights.json'
        bookings_file = tmp_path / 'bookings.json'
        # Створюємо рейс
        flight_data = {
            'flight_id': 'FL-001',
            'airline': 'Test Air',
            'origin': 'Київ',
            'destination': 'Львів',
            'departure_time': (datetime.now() + timedelta(days=1)).isoformat(),
            'arrival_time': (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            'price': 2500,
            'available_seats': 10,
            'flight_number': 'TA-101',
            'status': 'scheduled'
        }
        with open(flights_file, 'w', encoding='utf-8') as f:
            json.dump([flight_data], f, ensure_ascii=False, indent=2)

        return flights_file, bookings_file

    def test_create_booking(self, temp_files):
        flights_file, bookings_file = temp_files
        flight_service = FlightService(data_file=flights_file)
        booking_service = BookingService(data_file=bookings_file, flight_service=flight_service)

        passengers = [{'name': 'Іван Петренко', 'passport': 'AA123456'}]
        booking = booking_service.create_booking(
            user_id='user-1',
            flight_id='FL-001',
            seats=2,
            passengers_data=passengers
        )

        assert booking.flight_id == 'FL-001'
        assert booking.seats == 2
        assert booking.total_price == 5000
        assert len(booking.passengers) == 1
        assert booking.status == 'pending'

        # Перевіряємо, що місця зменшились
        flight = flight_service.get_by_id('FL-001')
        assert flight.available_seats == 8

        # Перевіряємо збереження
        booking_service._load_bookings()
        assert len(booking_service.bookings) == 1

    def test_cancel_booking(self, temp_files):
        flights_file, bookings_file = temp_files
        flight_service = FlightService(data_file=flights_file)
        booking_service = BookingService(data_file=bookings_file, flight_service=flight_service)

        passengers = [{'name': 'Іван Петренко', 'passport': 'AA123456'}]
        booking = booking_service.create_booking('user-1', 'FL-001', 1, passengers)

        booking_service.cancel_booking(booking.booking_id, 'Тестове скасування')
        updated = booking_service.get_by_id(booking.booking_id)
        assert updated.status == 'cancelled'
        assert 'Тестове скасування' in updated.notes

        # Місця повернулись
        flight = flight_service.get_by_id('FL-001')
        assert flight.available_seats == 10

    def test_confirm_booking(self, temp_files):
        flights_file, bookings_file = temp_files
        flight_service = FlightService(data_file=flights_file)
        booking_service = BookingService(data_file=bookings_file, flight_service=flight_service)

        passengers = [{'name': 'Іван Петренко', 'passport': 'AA123456'}]
        booking = booking_service.create_booking('user-1', 'FL-001', 1, passengers)

        booking_service.confirm_booking(booking.booking_id)
        updated = booking_service.get_by_id(booking.booking_id)
        assert updated.status == 'confirmed'

    def test_booking_stats(self, temp_files):
        flights_file, bookings_file = temp_files
        flight_service = FlightService(data_file=flights_file)
        booking_service = BookingService(data_file=bookings_file, flight_service=flight_service)

        passengers = [{'name': 'Іван Петренко', 'passport': 'AA123456'}]
        b1 = booking_service.create_booking('user-1', 'FL-001', 1, passengers)
        b2 = booking_service.create_booking('user-1', 'FL-001', 1, passengers)
        booking_service.confirm_booking(b1.booking_id)

        stats = booking_service.get_stats()
        assert stats['total'] == 2
        assert stats['pending'] == 1
        assert stats['confirmed'] == 1
        assert stats['total_revenue'] == 2500
