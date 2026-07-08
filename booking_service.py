"""
Сервіс для роботи з бронюваннями (оновлений з адмін-функціями)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.models.booking import Booking, Passenger
from src.services.flight_service import FlightService
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class BookingService:
    """Сервіс управління бронюваннями з адмін-функціями"""
    
    def __init__(self):
        self.bookings: List[Booking] = []
        self.flight_service = FlightService()
        self._load_bookings()
    
    def _load_bookings(self):
        data = Config.get_bookings()
        self.bookings = [Booking.from_dict(item) for item in data]
        logger.info(f"Завантажено {len(self.bookings)} бронювань")
    
    def _save_bookings(self):
        data = [b.to_dict() for b in self.bookings]
        Config.save_data(Config.BOOKINGS_FILE, data)
        logger.info(f"Збережено {len(self.bookings)} бронювань")
    
    def create_booking(self, user_id: str, flight_id: str, 
                       seats: int, passengers: List[dict]) -> Booking:
        flight = self.flight_service.get_flight_by_id(flight_id)
        if not flight:
            raise ValueError("Рейс не знайдено")
        
        if not flight.has_available_seats(seats):
            raise ValueError(f"Недостатньо місць. Доступно: {flight.available_seats}")
        
        flight.book_seats(seats)
        self.flight_service.update_flight(flight_id, {'available_seats': flight.available_seats})
        
        passenger_objects = [Passenger.from_dict(p) for p in passengers]
        
        booking = Booking(
            user_id=user_id,
            flight_id=flight_id,
            seats=seats,
            total_price=flight.price * seats,
            passengers=passenger_objects
        )
        
        self.bookings.append(booking)
        self._save_bookings()
        
        logger.info(f"Створено бронювання {booking.booking_id}")
        return booking
    
    def confirm_booking(self, booking_id: str, admin_id: str = None) -> Optional[Booking]:
        booking = self.get_booking_by_id(booking_id)
        if booking:
            booking.confirm(admin_id)
            self._save_bookings()
            logger.info(f"Підтверджено бронювання {booking_id} (адмін: {admin_id})")
            return booking
        return None
    
    def cancel_booking(self, booking_id: str, admin_id: str = None, reason: str = None) -> bool:
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Бронювання не знайдено")
        
        if booking.status == 'cancelled':
            raise ValueError("Бронювання вже скасовано")
        
        flight = self.flight_service.get_flight_by_id(booking.flight_id)
        if flight:
            flight.available_seats += booking.seats
            self.flight_service.update_flight(booking.flight_id, {
                'available_seats': flight.available_seats
            })
        
        booking.cancel(admin_id, reason)
        self._save_bookings()
        
        logger.info(f"Скасовано бронювання {booking_id} (адмін: {admin_id}, причина: {reason})")
        return True
    
    def complete_booking(self, booking_id: str, admin_id: str = None) -> Optional[Booking]:
        booking = self.get_booking_by_id(booking_id)
        if booking:
            booking.complete(admin_id)
            self._save_bookings()
            logger.info(f"Завершено бронювання {booking_id} (адмін: {admin_id})")
            return booking
        return None
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        for booking in self.bookings:
            if booking.booking_id == booking_id:
                return booking
        return None
    
    def get_user_bookings(self, user_id: str) -> List[Booking]:
        return [b for b in self.bookings if b.user_id == user_id]
    
    def get_flight_bookings(self, flight_id: str) -> List[Booking]:
        return [b for b in self.bookings if b.flight_id == flight_id]
    
    def get_all_bookings(self) -> List[Booking]:
        return self.bookings.copy()
    
    def get_active_bookings(self) -> List[Booking]:
        return [b for b in self.bookings if b.status in ['pending', 'confirmed']]
    
    def get_pending_bookings(self) -> List[Booking]:
        return [b for b in self.bookings if b.status == 'pending']
    
    def get_completed_bookings(self) -> List[Booking]:
        return [b for b in self.bookings if b.status == 'completed']
    
    def get_cancelled_bookings(self) -> List[Booking]:
        return [b for b in self.bookings if b.status == 'cancelled']
    
    def get_bookings_by_date_range(self, start: datetime, end: datetime) -> List[Booking]:
        return [b for b in self.bookings if start <= b.booking_date <= end]
    
    def get_bookings_by_status(self, status: str) -> List[Booking]:
        return [b for b in self.bookings if b.status == status]
    
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
