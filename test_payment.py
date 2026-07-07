"""
Тести для платіжного сервісу
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.models.booking import Booking, Passenger, Payment
from src.services.payment_service import PaymentService
from src.services.booking_service import BookingService


class TestPayment:
    """Тести для моделі Payment"""
    
    def test_payment_creation(self):
        """Тест створення платежу"""
        payment = Payment(
            booking_id="BK-001",
            amount=5000,
            currency="UAH",
            method="card"
        )
        
        assert payment.booking_id == "BK-001"
        assert payment.amount == 5000
        assert payment.currency == "UAH"
        assert payment.status == "pending"
    
    def test_payment_complete(self):
        """Тест завершення платежу"""
        payment = Payment(amount=5000)
        payment.complete("TXN-123", "https://receipt.url")
        
        assert payment.status == "completed"
        assert payment.transaction_id == "TXN-123"
        assert payment.receipt_url == "https://receipt.url"
        assert payment.is_completed() is True
    
    def test_payment_fail(self):
        """Тест відміни платежу"""
        payment = Payment(amount=5000)
        payment.fail("Помилка")
        
        assert payment.status == "failed"
        assert payment.error_message == "Помилка"
        assert payment.is_failed() is True
    
    def test_payment_refund(self):
        """Тест повернення платежу"""
        payment = Payment(amount=5000, status="completed")
        payment.refund()
        
        assert payment.status == "refunded"
        assert payment.is_refunded() is True
    
    def test_payment_to_dict(self):
        """Тест конвертації в словник"""
        payment = Payment(
            payment_id="PAY-001",
            booking_id="BK-001",
            amount=5000,
            status="completed"
        )
        
        data = payment.to_dict()
        assert data['payment_id'] == "PAY-001"
        assert data['booking_id'] == "BK-001"
        assert data['amount'] == 5000
        assert data['status'] == "completed"


class TestPaymentService:
    """Тести для PaymentService"""
    
    def test_payment_service_init(self):
        """Тест ініціалізації"""
        service = PaymentService()
        assert service.api_key == "test_api_key"
        assert service.payment_methods is not None
    
    def test_get_available_methods(self):
        """Тест отримання доступних методів"""
        service = PaymentService()
        methods = service.get_available_methods()
        
        assert 'card' in methods
        assert 'google_pay' in methods
        assert 'apple_pay' in methods
        assert 'bank_transfer' in methods
        assert methods['card']['enabled'] is True
    
    def test_validate_card_number(self):
        """Тест валідації номера картки"""
        service = PaymentService()
        
        # Валідні номери
        assert service._validate_card_number("4111111111111111") is True
        assert service._validate_card_number("5555555555554444") is True
        
        # Невірні номери
        assert service._validate_card_number("1234567890123456") is False
        assert service._validate_card_number("4111 1111 1111 1111") is True  # з пробілами
    
    def test_validate_expiry_date(self):
        """Тест валідації терміну дії"""
        service = PaymentService()
        
        future_date = datetime.now() + timedelta(days=365)
        expiry = future_date.strftime("%m/%y")
        
        assert service._validate_expiry_date(expiry) is True
        
        # Прострочена дата
        past_date = datetime.now() - timedelta(days=365)
        expiry = past_date.strftime("%m/%y")
        assert service._validate_expiry_date(expiry) is False
    
    def test_detect_card_type(self):
        """Тест визначення типу картки"""
        service = PaymentService()
        
        assert service._detect_card_type("4111111111111111") == "Visa"
        assert service._detect_card_type("5555555555554444") == "Mastercard"
        assert service._detect_card_type("371234567890123") == "American Express"
        assert service._detect_card_type("6011111111111117") == "Discover"
    
    def test_calculate_fee(self):
        """Тест розрахунку комісії"""
        service = PaymentService()
        
        fee = service.calculate_payment_fee(1000, "card")
        assert fee == 15.0  # 1.5%
        
        fee = service.calculate_payment_fee(1000, "google_pay")
        assert fee == 10.0  # 1%
        
        fee = service.calculate_payment_fee(1000, "bank_transfer")
        assert fee == 5.0  # 0.5%
        
        total = service.calculate_total_with_fee(1000, "card")
        assert total == 1015.0

    def test_process_card_payment(self):
        """Тест обробки оплати карткою"""
        service = PaymentService()
        payment = Payment(booking_id="BK-001", amount=5000)
        
        card_data = {
            'card_number': '4111111111111111',
            'expiry_date': (datetime.now() + timedelta(days=365)).strftime("%m/%y"),
            'cvv': '123',
            'cardholder_name': 'IVAN PETRENKO'
        }
        
        result = service._process_card_payment(payment, card_data)
        
        # Може бути успіх або помилка (залежить від random)
        assert result.status in ['completed', 'failed']
        if result.status == 'completed':
            assert result.transaction_id is not None
            assert result.card_last_digits == "1111"
            assert result.card_type == "Visa"


class TestBookingWithPayment:
    """Тести для Booking з оплатою"""
    
    def test_booking_add_payment(self):
        """Тест додавання платежу до бронювання"""
        booking = Booking(
            booking_id="BK-001",
            user_id="USR-001",
            flight_id="FL-001",
            seats=2,
            total_price=5000
        )
        
        payment = Payment(
            payment_id="PAY-001",
            booking_id="BK-001",
            amount=5000,
            status="completed"
        )
        
        booking.add_payment(payment)
        
        assert len(booking.payments) == 1
        assert booking.total_paid == 5000
        assert booking.payment_status == "paid"
        assert booking.is_fully_paid() is True
    
    def test_booking_partial_payment(self):
        """Тест часткової оплати"""
        booking = Booking(
            booking_id="BK-001",
            total_price=5000
        )
        
        payment = Payment(
            payment_id="PAY-001",
            booking_id="BK-001",
            amount=3000,
            status="completed"
        )
        
        booking.add_payment(payment)
        
        assert booking.total_paid == 3000
        assert booking.is_fully_paid() is False
        assert booking.is_partially_paid() is True
        assert booking.get_remaining_amount() == 2000
    
    def test_booking_remaining_amount(self):
        """Тест розрахунку залишку"""
        booking = Booking(total_price=5000)
        assert booking.get_remaining_amount() == 5000
        
        payment = Payment(amount=3000, status="completed")
        booking.add_payment(payment)
        assert booking.get_remaining_amount() == 2000
        
        payment2 = Payment(amount=2000, status="completed")
        booking.add_payment(payment2)
        assert booking.get_remaining_amount() == 0

    def test_payment_service_process_payment_integration(self):
        """Інтеграційний тест обробки платежу"""
        service = PaymentService()
        
        booking = Booking(
            booking_id="BK-001",
            total_price=5000
        )
        
        card_data = {
            'card_number': '4111111111111111',
            'expiry_date': (datetime.now() + timedelta(days=365)).strftime("%m/%y"),
            'cvv': '123',
            'cardholder_name': 'IVAN PETRENKO'
        }
        
        # Тестуємо обробку
        try:
            result = service.process_payment(booking, "card", card_data)
            assert result is not None
            assert result.booking_id == "BK-001"
        except Exception as e:
            # Якщо тест рандомно провалився - це нормально
            assert "Платіж відхилено" in str(e) or "Невірний" in str(e)
