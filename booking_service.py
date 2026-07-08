"""
Сервіс бронювань – ОБ'ЄДНАНА ВЕРСІЯ
Включає всі методи з усіх гілок:
- booking-system: create, cancel, confirm, get_by_*
- payment-integration: process_payment, refund
- admin-panel: complete, статистика, адмін-дії
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.models.booking import Booking, Passenger, Payment
from src.services.flight_service import FlightService
from src.services.payment_service import PaymentService
from src.config import Config

logger = logging.getLogger(__name__)


class BookingService:
    """Сервіс управління бронюваннями (повний)"""

    def __init__(self, data_file: str = None, flight_service: FlightService = None):
        if data_file is None:
            base_dir = Path(__file__).parent.parent.parent
            data_file = base_dir / 'data' / 'bookings.json'
        self.data_file = Path(data_file)
        self.bookings: List[Booking] = []
        self.flight_service = flight_service or FlightService()
        self.payment_service = PaymentService()
        self._load_bookings()

    # ============================================================
    #  РОБОТА З ФАЙЛОМ
    # ============================================================

    def _load_bookings(self):
        if not self.data_file.exists():
            self.bookings = []
            logger.warning(f"Файл бронювань не знайдено: {self.data_file}")
            return
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.bookings = [Booking.from_dict(item) for item in data]
                logger.info(f"Завантажено {len(self.bookings)} бронювань")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Помилка завантаження бронювань: {e}")
            self.bookings = []

    def _save_bookings(self):
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([b.to_dict() for b in self.bookings], f, ensure_ascii=False, indent=2)
            logger.info(f"Збережено {len(self.bookings)} бронювань")
        except IOError as e:
            logger.error(f"Помилка запису бронювань: {e}")
            raise RuntimeError("Не вдалося зберегти дані бронювань") from e

    # ============================================================
    #  СТВОРЕННЯ ТА ОСНОВНІ ОПЕРАЦІЇ
    # ============================================================

    def create_booking(self, user_id: str, flight_id: str, seats: int,
                       passengers_data: List[dict], notes: str = None) -> Booking:
        """Створює нове бронювання"""
        flight = self.flight_service.get_by_id(flight_id)
        if not flight:
            raise ValueError("Рейс не знайдено")
        if flight.status in ['cancelled', 'completed']:
            raise ValueError(f"Рейс {flight.status}, бронювання неможливе")
        if not flight.has_available_seats(seats):
            raise ValueError(f"Недостатньо місць. Доступно: {flight.available_seats}")

        passengers = [Passenger.from_dict(p) for p in passengers_data]
        total_price = flight.price * seats

        booking = Booking(
            user_id=user_id,
            flight_id=flight_id,
            seats=seats,
            total_price=total_price,
            passengers=passengers,
            notes=notes,
            status='pending'
        )

        if not flight.book_seats(seats):
            raise ValueError("Не вдалося забронювати місця")
        self.flight_service._save_flights()

        self.bookings.append(booking)
        self._save_bookings()
        logger.info(f"Створено бронювання {booking.booking_id} для користувача {user_id}")
        return booking

    def cancel_booking(self, booking_id: str, reason: str = None, admin_id: str = None) -> bool:
        """Скасовує бронювання та повертає місця на рейс"""
        booking = self.get_by_id(booking_id)
        if not booking:
            raise ValueError("Бронювання не знайдено")
        if booking.status == 'cancelled':
            raise ValueError("Бронювання вже скасовано")

        flight = self.flight_service.get_by_id(booking.flight_id)
        if flight:
            flight.release_seats(booking.seats)
            self.flight_service._save_flights()

        booking.cancel(admin_id, reason)
        self._save_bookings()
        logger.info(f"Скасовано бронювання {booking_id} (адмін: {admin_id})")
        return True

    def confirm_booking(self, booking_id: str, admin_id: str = None) -> Optional[Booking]:
        """Підтверджує бронювання (адмін)"""
        booking = self.get_by_id(booking_id)
        if not booking:
            return None
        if booking.status == 'confirmed':
            raise ValueError("Бронювання вже підтверджено")
        booking.confirm(admin_id)
        self._save_bookings()
        logger.info(f"Підтверджено бронювання {booking_id} (адмін: {admin_id})")
        return booking

    def complete_booking(self, booking_id: str, admin_id: str = None) -> Optional[Booking]:
        """Завершує бронювання (адмін)"""
        booking = self.get_by_id(booking_id)
        if not booking:
            return None
        if booking.status == 'completed':
            raise ValueError("Бронювання вже завершено")
        booking.complete(admin_id)
        self._save_bookings()
        logger.info(f"Завершено бронювання {booking_id} (адмін: {admin_id})")
        return booking

    # ============================================================
    #  ОПЛАТА
    # ============================================================

    def process_payment(self, booking_id: str, method: str,
                        card_data: Dict[str, Any] = None,
                        admin_id: str = None) -> Dict[str, Any]:
        """Обробляє оплату для бронювання"""
        booking = self.get_by_id(booking_id)
        if not booking:
            raise ValueError("Бронювання не знайдено")
        if booking.is_fully_paid():
            return {
                'success': True,
                'message': 'Бронювання вже оплачено',
                'booking': booking.get_booking_summary()
            }

        try:
            payment = self.payment_service.process_payment(booking, method, card_data)
            booking.add_payment(payment)
            self._save_bookings()
            return {
                'success': payment.is_completed(),
                'payment': payment.to_dict(),
                'booking': booking.get_booking_summary(),
                'message': 'Оплата успішна' if payment.is_completed() else payment.error_message,
                'payment_status': payment.get_status_ukrainian(),
                'payment_status_emoji': payment.get_status_emoji()
            }
        except Exception as e:
            logger.error(f"Помилка оплати: {e}")
            return {
                'success': False,
                'message': str(e),
                'error': str(e)
            }

    def refund_booking_payment(self, booking_id: str, reason: str = None,
                               admin_id: str = None) -> Dict[str, Any]:
        """Повертає кошти за бронювання"""
        booking = self.get_by_id(booking_id)
        if not booking:
            raise ValueError("Бронювання не знайдено")
        if not booking.is_fully_paid():
            return {'success': False, 'message': 'Бронювання не оплачено'}

        if booking.payments:
            last_payment = booking.payments[-1]
            success = self.payment_service.refund_payment(last_payment.payment_id, reason)
            if success:
                booking.payment_status = 'refunded'
                booking.refund_amount += last_payment.amount
                booking.total_paid -= last_payment.amount
                self._save_bookings()
                return {
                    'success': True,
                    'message': 'Кошти повернуто',
                    'refund_amount': last_payment.amount,
                    'booking': booking.get_booking_summary()
                }

        return {'success': False, 'message': 'Не вдалося повернути кошти'}

    # ============================================================
    #  ОТРИМАННЯ ДАНИХ
    # ============================================================

    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        for b in self.bookings:
            if b.booking_id == booking_id:
                return b
        return None

    def get_by_user(self, user_id: str) -> List[Booking]:
        return [b for b in self.bookings if b.user_id == user_id]

    def get_by_flight(self, flight_id: str) -> List[Booking]:
        return [b for b in self.bookings if b.flight_id == flight_id]

    def get_all_bookings(self) -> List[Booking]:
        return self.bookings.copy()

    def get_pending_bookings(self) -> List[Booking]:
        return [b for b in self.bookings if b.status == 'pending']

    def get_confirmed_bookings(self) -> List[Booking]:
        return [b for b in self.bookings if b.status == 'confirmed']

    def get_cancelled_bookings(self) -> List[Booking]:
        return [b for b in self.bookings if b.status == 'cancelled']

    def get_completed_bookings(self) -> List[Booking]:
        return [b for b in self.bookings if b.status == 'completed']

    def get_bookings_by_date_range(self, start: datetime, end: datetime) -> List[Booking]:
        return [b for b in self.bookings if start <= b.booking_date <= end]

    # ============================================================
    #  СТАТИСТИКА
    # ============================================================

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.bookings)
        confirmed = len([b for b in self.bookings if b.status == 'confirmed'])
        pending = len([b for b in self.bookings if b.status == 'pending'])
        cancelled = len([b for b in self.bookings if b.status == 'cancelled'])
        completed = len([b for b in self.bookings if b.status == 'completed'])

        paid = len([b for b in self.bookings if b.is_fully_paid()])
        unpaid = len([b for b in self.bookings if not b.is_fully_paid() and b.payment_status != 'refunded'])
        refunded = len([b for b in self.bookings if b.payment_status == 'refunded'])

        total_revenue = sum(b.total_paid for b in self.bookings if b.is_fully_paid())
        total_refunded = sum(b.refund_amount for b in self.bookings)

        today = datetime.now().date()
        today_bookings = len([b for b in self.bookings if b.booking_date.date() == today])

        return {
            'total': total,
            'confirmed': confirmed,
            'pending': pending,
            'cancelled': cancelled,
            'completed': completed,
            'paid': paid,
            'unpaid': unpaid,
            'refunded': refunded,
            'total_revenue': total_revenue,
            'total_refunded': total_refunded,
            'net_revenue': total_revenue - total_refunded,
            'today_bookings': today_bookings,
            'avg_price': sum(b.total_price for b in self.bookings) / total if total > 0 else 0
                                 }
