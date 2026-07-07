"""
Сервіс для роботи з бронюваннями (оновлений з оплатою)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.booking import Booking, Passenger
from src.services.flight_service import FlightService
from src.services.payment_service import PaymentService
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class BookingService:
    """Сервіс управління бронюваннями з підтримкою оплати"""
    
    def __init__(self):
        self.bookings: List[Booking] = []
        self.flight_service = FlightService()
        self.payment_service = PaymentService()
        self._load_bookings()
    
    def _load_bookings(self):
        """Завантажити бронювання з файлу"""
        data = Config.get_bookings()
        self.bookings = [Booking.from_dict(item) for item in data]
        logger.info(f"Завантажено {len(self.bookings)} бронювань")
    
    def _save_bookings(self):
        """Зберегти бронювання у файл"""
        data = [b.to_dict() for b in self.bookings]
        Config.save_data(Config.BOOKINGS_FILE, data)
        logger.info(f"Збережено {len(self.bookings)} бронювань")
    
    def create_booking(self, user_id: str, flight_id: str, 
                       seats: int, passengers: List[dict]) -> Booking:
        """Створити нове бронювання"""
        # Перевірка рейсу
        flight = self.flight_service.get_flight_by_id(flight_id)
        if not flight:
            raise ValueError("Рейс не знайдено")
        
        if not flight.has_available_seats(seats):
            raise ValueError(f"Недостатньо місць на рейсі. Доступно: {flight.available_seats}")
        
        # Забронювати місця
        if not flight.book_seats(seats):
            raise ValueError("Не вдалося забронювати місця")
        
        # Оновити рейс
        self.flight_service.update_flight(flight_id, {
            'available_seats': flight.available_seats
        })
        
        # Створити пасажирів
        passenger_objects = [Passenger.from_dict(p) for p in passengers]
        
        # Створити бронювання
        booking = Booking(
            user_id=user_id,
            flight_id=flight_id,
            seats=seats,
            total_price=flight.price * seats,
            passengers=passenger_objects,
            payment_status='unpaid'
        )
        
        self.bookings.append(booking)
        self._save_bookings()
        
        logger.info(f"Створено бронювання {booking.booking_id} для користувача {user_id}")
        return booking
    
    def process_payment(self, booking_id: str, method: str, 
                       card_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обробка оплати для бронювання
        
        Args:
            booking_id: ID бронювання
            method: Метод оплати
            card_data: Дані картки (для card)
            
        Returns:
            dict: Результат оплати
        """
        booking = self.get_booking_by_id(booking_id)
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
    
    def get_payment_methods(self) -> Dict[str, Dict]:
        """Отримати доступні методи оплати"""
        return self.payment_service.get_available_methods()
    
    def refund_booking_payment(self, booking_id: str, reason: str = None) -> Dict[str, Any]:
        """
        Повернення коштів за бронювання
        
        Args:
            booking_id: ID бронювання
            reason: Причина повернення
            
        Returns:
            dict: Результат повернення
        """
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Бронювання не знайдено")
        
        if not booking.is_fully_paid():
            return {
                'success': False,
                'message': 'Бронювання не оплачено'
            }
        
        # Повертаємо останній платіж
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
        
        return {
            'success': False,
            'message': 'Не вдалося повернути кошти'
        }
    
    def cancel_booking(self, booking_id: str) -> bool:
        """Скасувати бронювання"""
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Бронювання не знайдено")
        
        if booking.status == 'cancelled':
            raise ValueError("Бронювання вже скасовано")
        
        # Повертаємо місця на рейс
        flight = self.flight_service.get_flight_by_id(booking.flight_id)
        if flight:
            flight.available_seats += booking.seats
            self.flight_service.update_flight(booking.flight_id, {
                'available_seats': flight.available_seats
            })
        
        # Скасовуємо бронювання
        booking.cancel()
        
        # Якщо була оплата - повертаємо
        if booking.is_fully_paid():
            self.refund_booking_payment(booking_id, 'Скасування бронювання')
        
        self._save_bookings()
        
        logger.info(f"Скасовано бронювання {booking_id}")
        return True
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        """Отримати бронювання за ID"""
        for booking in self.bookings:
            if booking.booking_id == booking_id:
                return booking
        return None
    
    def get_user_bookings(self, user_id: str) -> List[Booking]:
        """Отримати всі бронювання користувача"""
        return [b for b in self.bookings if b.user_id == user_id]
    
    def get_flight_bookings(self, flight_id: str) -> List[Booking]:
        """Отримати всі бронювання на рейс"""
        return [b for b in self.bookings if b.flight_id == flight_id]
    
    def get_active_bookings(self) -> List[Booking]:
        """Отримати активні бронювання"""
        return [b for b in self.bookings if b.status in ['pending', 'confirmed']]
    
    def get_booking_stats(self) -> dict:
        """Отримати статистику бронювань"""
        total = len(self.bookings)
        confirmed = len([b for b in self.bookings if b.status == 'confirmed'])
        pending = len([b for b in self.bookings if b.status == 'pending'])
        cancelled = len([b for b in self.bookings if b.status == 'cancelled'])
        completed = len([b for b in self.bookings if b.status == 'completed'])
        
        paid = len([b for b in self.bookings if b.is_fully_paid()])
        unpaid = len([b for b in self.bookings if not b.is_fully_paid() and b.payment_status != 'refunded'])
        refunded = len([b for b in self.bookings if b.payment_status == 'refunded'])
        
        total_revenue = sum(b.total_paid for b in self.bookings if b.is_fully_paid())
        
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
            'total_refunded': sum(b.refund_amount for b in self.bookings)
                         }
