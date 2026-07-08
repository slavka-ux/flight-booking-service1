"""
Flask додаток з ендпоїнтами аутентифікації та бронювання
"""

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from functools import wraps
from src.services.flight_service import FlightService
from src.services.booking_service import BookingService
from src.services.user_service import UserService
from src.utils.validators import validate_register_data, validate_booking_data
import logging

app = Flask(__name__)
CORS(app)

# Сервіси
flight_service = FlightService()
booking_service = BookingService(flight_service=flight_service)
user_service = UserService()

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# === Middleware для перевірки токена ===

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Токен не надано'}), 401
        # Очікуємо "Bearer <token>"
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


# === Ендпоїнти аутентифікації ===

@app.route('/api/auth/register', methods=['POST'])
def register():
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
    """Отримує інформацію про поточного користувача (за токеном)"""
    user = user_service.get_user_by_id(g.user_id)
    if not user:
        return jsonify({'error': 'Користувача не знайдено'}), 404
    return jsonify(user.to_dict())


@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """Логаут (на клієнті просто видаляють токен)"""
    return jsonify({'success': True, 'message': 'Вихід виконано'})


# === Захищені ендпоїнти бронювання ===

@app.route('/api/bookings', methods=['POST'])
@token_required
def create_booking():
    data = request.json
    is_valid, msg = validate_booking_data(data)
    if not is_valid:
        return jsonify({'error': msg}), 400

    try:
        booking = booking_service.create_booking(
            user_id=g.user_id,  # використовуємо ID з токена
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
    return jsonify({'bookings': [b.to_dict() for b in bookings]})


@app.route('/api/bookings/<booking_id>/cancel', methods=['PUT'])
@token_required
def cancel_booking(booking_id):
    reason = request.json.get('reason') if request.json else None
    try:
        booking_service.cancel_booking(booking_id, reason)
        return jsonify({'success': True, 'message': 'Бронювання скасовано'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# === Публічні ендпоїнти (пошук рейсів) ===

@app.route('/api/flights/search', methods=['GET'])
def search_flights():
    origin = request.args.get('origin', '').strip()
    destination = request.args.get('destination', '').strip()
    date = request.args.get('date', '').strip()
    flights = flight_service.search(origin, destination, date if date else None)
    return jsonify({'flights': [f.to_dict() for f in flights], 'count': len(flights)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
