"""
Flask додаток з ендпоїнтами для бронювання
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from src.services.flight_service import FlightService
from src.services.booking_service import BookingService
from src.utils.validators import validate_booking_data

app = Flask(__name__)
CORS(app)

flight_service = FlightService()
booking_service = BookingService(flight_service=flight_service)


@app.route('/api/flights/search', methods=['GET'])
def search_flights():
    origin = request.args.get('origin', '').strip()
    destination = request.args.get('destination', '').strip()
    date = request.args.get('date', '').strip()
    flights = flight_service.search(origin, destination, date if date else None)
    return jsonify({'flights': [f.to_dict() for f in flights], 'count': len(flights)})


@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    is_valid, msg = validate_booking_data(data)
    if not is_valid:
        return jsonify({'error': msg}), 400

    try:
        booking = booking_service.create_booking(
            user_id=data.get('user_id', 'anonymous'),
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
        return jsonify({'error': 'Внутрішня помилка сервера'}), 500


@app.route('/api/bookings/<booking_id>/cancel', methods=['PUT'])
def cancel_booking(booking_id):
    reason = request.json.get('reason') if request.json else None
    try:
        booking_service.cancel_booking(booking_id, reason)
        return jsonify({'success': True, 'message': 'Бронювання скасовано'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/bookings/<booking_id>/confirm', methods=['PUT'])
def confirm_booking(booking_id):
    try:
        booking_service.confirm_booking(booking_id)
        return jsonify({'success': True, 'message': 'Бронювання підтверджено'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/bookings/user/<user_id>', methods=['GET'])
def get_user_bookings(user_id):
    bookings = booking_service.get_by_user(user_id)
    return jsonify({'bookings': [b.to_dict() for b in bookings]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
