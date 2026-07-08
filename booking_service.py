"""
Сервіс для роботи з бронюваннями
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.models.booking import Booking, Passenger
from src.models.flight import Flight
from src.services.flight_service import FlightService


class BookingService:
    """Сервіс управління бронюваннями"""

    def __init__(self, data_file: str = None, flight_service: FlightService = None):
        if data_file is None:
            base_dir = Path(__file__).parent.parent.parent
            data_file = base_dir / 'data' / 'bookings.json'
        self.data_file = Path(data_file)
        self.bookings: List[Booking] = []
        self.flight_service = flight_service or FlightService()
        self._load_bookings()

    def _load_bookings(self):
        if not self.data_file.exists():
            self.bookings = []
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.bookings = [Booking.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError):
            self.bookings = []

    def _save_bookings(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump([b.to_dict() for b in self.bookings], f, ensure_ascii=False, indent=2)

    def create_booking(self, user_id: str, flight_id: str, seats: int,
                       passengers_data: List[dict], notes: str = None) -> Booking:
        """
        Створює нове бронювання.
        Перевіряє наявність місць на рейсі та зменшує їх кількість.
        """
        # Отримуємо рейс
        flight = self.flight_service.get_by_id(flight_id)
        if not flight:
            raise ValueError("Рейс не знайдено")

        if not flight.has_available_seats(seats):
            raise ValueError(f"Недостатньо місць. Доступно: {flight.available_seats}")

        # Створюємо пасажирів
        passengers = [Passenger.from_dict(p) for p in passengers_data]

        # Розраховуємо загальну вартість
        total_price = flight.price * seats

        # Створюємо бронювання
        booking = Booking(
            user_id=user_id,
            flight_id=flight_id,
            seats=seats,
            total_price=total_price,
            passengers=passengers,
            notes=notes,
            status='pending'
        )

        # Зменшуємо кількість доступних місць на рейсі
        flight.book_seats(seats)
        # Оновлюємо рейс у файлі (через FlightService)
        self.flight_service._save_flights()  # якщо є такий метод

        # Зберігаємо бронювання
        self.bookings.append(booking)
        self._save_bookings()
        return booking

    def cancel_booking(self, booking_id: str, reason: str = None) -> bool:
        """Скасовує бронювання та повертає місця на рейс"""
        booking = self.get_by_id(booking_id)
        if not booking:
            raise ValueError("Бронювання не знайдено")

        if booking.status == 'cancelled':
            raise ValueError("Бронювання вже скасовано")

        # Повертаємо місця на рейс
        flight = self.flight_service.get_by_id(booking.flight_id)
        if flight:
            flight.release_seats(booking.seats)
            self.flight_service._save_flights()

        booking.cancel()
        if reason:
            booking.notes = f"Скасовано: {reason}" if not booking.notes else f"{booking.notes}\nСкасовано: {reason}"
        self._save_bookings()
        return True

    def confirm_booking(self, booking_id: str) -> bool:
        """Підтверджує бронювання (наприклад, після оплати)"""
        booking = self.get_by_id(booking_id)
        if not booking:
            raise ValueError("Бронювання не знайдено")
        if booking.status == 'confirmed':
            raise ValueError("Бронювання вже підтверджено")
        booking.confirm()
        self._save_bookings()
        return True

    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        for b in self.bookings:
            if b.booking_id == booking_id:
                return b
        return None

    def get_by_user(self, user_id: str) -> List[Booking]:
        return [b for b in self.bookings if b.user_id == user_id]

    def get_by_flight(self, flight_id: str) -> List[Booking]:
        return [b for b in self.bookings if b.flight_id == flight_id]

    def get_all(self) -> List[Booking]:
        return self.bookings.copy()

    def get_stats(self) -> dict:
        total = len(self.bookings)
        pending = len([b for b in self.bookings if b.status == 'pending'])
        confirmed = len([b for b in self.bookings if b.status == 'confirmed'])
        cancelled = len([b for b in self.bookings if b.status == 'cancelled'])
        total_revenue = sum(b.total_price for b in self.bookings if b.status == 'confirmed')
        return {
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'cancelled': cancelled,
            'total_revenue': total_revenue
        }
