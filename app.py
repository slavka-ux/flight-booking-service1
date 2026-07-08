"""
Flask додаток – ОБ'ЄДНАНА ВЕРСІЯ
Включає всі ендпоїнти з усіх гілок:
- flight-search: пошук рейсів
- booking-system: створення, скасування, підтвердження бронювань
- user-auth: реєстрація, вхід, JWT, перевірка токена
- payment-integration: обробка платежів, повернення
- admin-panel: адмін-управління (рейси, бронювання, користувачі)
"""

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from functools import wraps
import logging

from src.services.flight_service import FlightService
from src.services.booking_service import BookingService
from src.services.user_service import UserService
from src.services.payment_service import PaymentService
from src.utils.validators import (
    validate_register_data,
    validate_booking_data,
    validate_payment_data
)

# ============================================================
#  НАЛАШТУВАННЯ
# ============================================================

app = Flask(__name__)
CORS(app)  # Дозволяємо CORS для всіх доменів

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Сервіси
flight_service = FlightService()
booking_service = BookingService(flight_service=flight_service)
user_service = UserService()
payment_service = PaymentService()

# ============================================================
#  ДЕКОРАТОР ДЛЯ ПЕРЕВІРКИ ТОКЕНА
# ============================================================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Токен не надано'}), 401
        parts = token.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Невірний формат токена'}), 401
        token = parts[1]
        payload = user_service.verify_token(token)
        if not payload:
            return jsonify({'error': 'Недійсний або прострочений токен'}), 401
        g.user_id = payload.get('user_id')
        g.username = payload.get('username')
        g.is_admin = payload.get('is_admin', False)
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.get('is_admin', False):
            return jsonify({'error': 'Потрібні права адміністратора'}), 403
        return f(*args, **kwargs)
    return decorated


# ============================================================
#  ПУБЛІЧНІ ЕНДПОЇНТИ (пошук рейсів)
# ============================================================

@app.route('/api/flights/search', methods=['GET'])
def search_flights():
    """Пошук рейсів за напрямком та датою (публічний)"""
    origin = request.args.get('origin', '').strip()
    destination = request.args.get('destination', '').strip()
    date = request.args.get('date', '').strip()
    flights = flight_service.search(origin, destination, date if date else None)
    return jsonify({
        'flights': [f.to_dict() for f in flights],
        'count': len(flights)
    })


# ============================================================
#  АУТЕНТИФІКАЦІЯ
# ============================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Реєстрація нового користувача"""
    data = request.json
    is_valid, msg = validate_register_data(data)
    if not is_valid:
        return jsonify({'error': msg}), 400

    try:
        user = user_service.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', ''),
            phone=data.get('phone', '')
        )
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': 'Реєстрація успішна'
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Помилка реєстрації: {e}")
        return jsonify({'error': 'Внутрішня помилка сервера'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Вхід користувача (повертає JWT)"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'error': 'Введіть логін та пароль'}), 400

    try:
        result = user_service.login(username, password)
        return jsonify({
            'success': True,
            'token': result['token'],
            'user': result['user'],
            'expires_in': result['expires_in']
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 401


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Отримує дані поточного користувача за токеном"""
    user = user_service.get_user_by_id(g.user_id)
    if not user:
        return jsonify({'error': 'Користувача не знайдено'}), 404
    return jsonify(user.to_dict())


@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """Вихід (на клієнті видаляють токен)"""
    return jsonify({'success': True, 'message': 'Вихід виконано'})


# ============================================================
#  БРОНЮВАННЯ (захищені)
# ============================================================

@app.route('/api/bookings', methods=['POST'])
@token_required
def create_booking():
    """Створення нового бронювання"""
    data = request.json
    is_valid, msg = validate_booking_data(data)
    if not is_valid:
        return jsonify({'error': msg}), 400

    try:
        booking = booking_service.create_booking(
            user_id=g.user_id,
            flight_id=data['flight_id'],
            seats=data['seats'],
            passengers_data=data['passengers'],
            notes=data.get('notes')
        )
        return jsonify({
            'success': True,
            'booking': booking.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Помилка створення бронювання: {e}")
        return jsonify({'error': 'Внутрішня помилка сервера'}), 500


@app.route('/api/bookings/user', methods=['GET'])
@token_required
def get_user_bookings():
    """Отримує всі бронювання поточного користувача"""
    bookings = booking_service.get_by_user(g.user_id)
    return jsonify({
        'bookings': [b.to_dict() for b in bookings],
        'count': len(bookings)
    })


@app.route('/api/bookings/<booking_id>', methods=['GET'])
@token_required
def get_booking(booking_id):
    """Отримує деталі конкретного бронювання"""
    booking = booking_service.get_by_id(booking_id)
    if not booking:
        return jsonify({'error': 'Бронювання не знайдено'}), 404
    # Перевіряємо, чи належить бронювання користувачеві або він адмін
    if booking.user_id != g.user_id and not g.is_admin:
        return jsonify({'error': 'Доступ заборонено'}), 403
    return jsonify(booking.to_dict())


@app.route('/api/bookings/<booking_id>/cancel', methods=['PUT'])
@token_required
def cancel_booking(booking_id):
    """Скасування бронювання (користувач або адмін)"""
    booking = booking_service.get_by_id(booking_id)
    if not booking:
        return jsonify({'error': 'Бронювання не знайдено'}), 404
    if booking.user_id != g.user_id and not g.is_admin:
        return jsonify({'error': 'Доступ заборонено'}), 403

    reason = request.json.get('reason') if request.json else None
    try:
        booking_service.cancel_booking(booking_id, reason, g.user_id)
        return jsonify({'success': True, 'message': 'Бронювання скасовано'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ============================================================
#  ОПЛАТА
# ============================================================

@app.route('/api/payments/process', methods=['POST'])
@token_required
def process_payment():
    """Обробка платежу за бронювання"""
    data = request.json
    is_valid, msg = validate_payment_data(data)
    if not is_valid:
        return jsonify({'error': msg}), 400

    booking_id = data['booking_id']
    booking = booking_service.get_by_id(booking_id)
    if not booking:
        return jsonify({'error': 'Бронювання не знайдено'}), 404
    if booking.user_id != g.user_id and not g.is_admin:
        return jsonify({'error': 'Доступ заборонено'}), 403

    try:
        result = booking_service.process_payment(
            booking_id=booking_id,
            method=data['method'],
            card_data=data.get('card_data'),
            admin_id=g.user_id if g.is_admin else None
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Помилка оплати: {e}")
        return jsonify({'error': 'Внутрішня помилка сервера'}), 500


@app.route('/api/payments/methods', methods=['GET'])
@token_required
def get_payment_methods():
    """Отримує список доступних методів оплати"""
    methods = payment_service.get_available_methods()
    return jsonify({'methods': methods})


# ============================================================
#  АДМІН-ПАНЕЛЬ
# ============================================================

# ----- Рейси -----
@app.route('/api/admin/flights', methods=['GET'])
@token_required
@admin_required
def admin_get_flights():
    """Отримати всі рейси (адмін)"""
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    flights = flight_service.get_all_flights(include_inactive=include_inactive)
    return jsonify({'flights': [f.to_dict() for f in flights], 'count': len(flights)})


@app.route('/api/admin/flights', methods=['POST'])
@token_required
@admin_required
def admin_add_flight():
    """Додати новий рейс (адмін)"""
    data = request.json
    try:
        flight = flight_service.add_flight(data, admin_id=g.user_id)
        return jsonify(flight.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/admin/flights/<flight_id>', methods=['PUT'])
@token_required
@admin_required
def admin_update_flight(flight_id):
    """Оновити рейс (адмін)"""
    data = request.json
    try:
        flight = flight_service.update_flight(flight_id, data, admin_id=g.user_id)
        if not flight:
            return jsonify({'error': 'Рейс не знайдено'}), 404
        return jsonify(flight.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/admin/flights/<flight_id>', methods=['DELETE'])
@token_required
@admin_required
def admin_delete_flight(flight_id):
    """Видалити рейс (адмін)"""
    if flight_service.delete_flight(flight_id, admin_id=g.user_id):
        return jsonify({'success': True, 'message': 'Рейс видалено'})
    return jsonify({'error': 'Рейс не знайдено'}), 404


@app.route('/api/admin/flights/<flight_id>/toggle', methods=['PUT'])
@token_required
@admin_required
def admin_toggle_flight(flight_id):
    """Активувати/деактивувати рейс (адмін)"""
    flight = flight_service.toggle_flight_active(flight_id, admin_id=g.user_id)
    if not flight:
        return jsonify({'error': 'Рейс не знайдено'}), 404
    return jsonify(flight.to_dict())


@app.route('/api/admin/flights/stats', methods=['GET'])
@token_required
@admin_required
def admin_flight_stats():
    """Статистика по рейсах (адмін)"""
    stats = flight_service.get_stats()
    return jsonify(stats)


# ----- Бронювання -----
@app.route('/api/admin/bookings', methods=['GET'])
@token_required
@admin_required
def admin_get_bookings():
    """Отримати всі бронювання (адмін)"""
    status = request.args.get('status')
    bookings = booking_service.get_all_bookings()
    if status:
        bookings = [b for b in bookings if b.status == status]
    return jsonify({'bookings': [b.to_dict() for b in bookings], 'count': len(bookings)})


@app.route('/api/admin/bookings/<booking_id>/confirm', methods=['PUT'])
@token_required
@admin_required
def admin_confirm_booking(booking_id):
    """Підтвердити бронювання (адмін)"""
    booking = booking_service.confirm_booking(booking_id, admin_id=g.user_id)
    if not booking:
        return jsonify({'error': 'Бронювання не знайдено'}), 404
    return jsonify(booking.to_dict())


@app.route('/api/admin/bookings/<booking_id>/complete', methods=['PUT'])
@token_required
@admin_required
def admin_complete_booking(booking_id):
    """Завершити бронювання (адмін)"""
    booking = booking_service.complete_booking(booking_id, admin_id=g.user_id)
    if not booking:
        return jsonify({'error': 'Бронювання не знайдено'}), 404
    return jsonify(booking.to_dict())


@app.route('/api/admin/bookings/<booking_id>/cancel', methods=['PUT'])
@token_required
@admin_required
def admin_cancel_booking(booking_id):
    """Скасувати бронювання (адмін)"""
    reason = request.json.get('reason') if request.json else None
    try:
        booking_service.cancel_booking(booking_id, reason, admin_id=g.user_id)
        return jsonify({'success': True, 'message': 'Бронювання скасовано'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/admin/bookings/stats', methods=['GET'])
@token_required
@admin_required
def admin_booking_stats():
    """Статистика по бронюваннях (адмін)"""
    stats = booking_service.get_stats()
    return jsonify(stats)


# ----- Користувачі -----
@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def admin_get_users():
    """Отримати всіх користувачів (адмін)"""
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    users = user_service.get_all_users(include_inactive=include_inactive)
    return jsonify({'users': [u.to_dict() for u in users], 'count': len(users)})


@app.route('/api/admin/users/<user_id>/admin', methods=['PUT'])
@token_required
@admin_required
def admin_toggle_admin(user_id):
    """Надати/зняти права адміністратора (адмін)"""
    data = request.json
    is_admin = data.get('is_admin', False)
    user = user_service.set_admin_role(user_id, is_admin, admin_id=g.user_id)
    if not user:
        return jsonify({'error': 'Користувача не знайдено'}), 404
    return jsonify(user.to_dict())


@app.route('/api/admin/users/<user_id>/active', methods=['PUT'])
@token_required
@admin_required
def admin_toggle_active(user_id):
    """Активувати/деактивувати користувача (адмін)"""
    data = request.json
    is_active = data.get('is_active', True)
    if is_active:
        user = user_service.activate_user(user_id, admin_id=g.user_id)
    else:
        reason = data.get('reason')
        user = user_service.deactivate_user(user_id, admin_id=g.user_id, reason=reason)
    if not user:
        return jsonify({'error': 'Користувача не знайдено'}), 404
    return jsonify(user.to_dict())


@app.route('/api/admin/users/stats', methods=['GET'])
@token_required
@admin_required
def admin_user_stats():
    """Статистика по користувачах (адмін)"""
    stats = user_service.get_stats()
    return jsonify(stats)


# ============================================================
#  ОБРОБНИКИ ПОМИЛОК
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Ресурс не знайдено', 'status': 404}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Метод не дозволено', 'status': 405}), 405


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Внутрішня помилка сервера: {e}")
    return jsonify({'error': 'Внутрішня помилка сервера', 'status': 500}), 500


# ============================================================
#  ЗАПУСК
# ============================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
