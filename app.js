/**
 * Flight Booking – клієнтська логіка
 */

class BookingApp {
    constructor() {
        this.apiBase = ''; // можна змінити на URL бекенду
        this.selectedFlight = null;
        this.passengerCount = 1;
        this.init();
    }

    init() {
        // Пошук рейсів
        const searchForm = document.getElementById('searchForm');
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.searchFlights();
        });

        // Кнопка додати пасажира
        document.getElementById('addPassengerBtn').addEventListener('click', () => {
            this.addPassengerField();
        });

        // Форма бронювання
        document.getElementById('bookingForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitBooking();
        });

        // Закриття модалки
        document.getElementById('closeModal').addEventListener('click', () => {
            this.closeModal();
        });
        window.addEventListener('click', (e) => {
            if (e.target === document.getElementById('bookingModal')) {
                this.closeModal();
            }
        });

        // Завантажуємо демо-рейси
        this.loadDemoFlights();

        // Завантажуємо список бронювань (якщо є)
        this.loadBookings();
    }

    async searchFlights() {
        const origin = document.getElementById('origin').value.trim();
        const destination = document.getElementById('destination').value.trim();
        const date = document.getElementById('date').value;

        if (!origin || !destination) {
            alert('Введіть місто вильоту та прильоту');
            return;
        }

        try {
            const params = new URLSearchParams({ origin, destination });
            if (date) params.append('date', date);
            const url = `${this.apiBase}/api/flights/search?${params}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Помилка завантаження');
            const data = await response.json();
            this.displayFlights(data.flights || []);
        } catch (error) {
            console.error('Помилка пошуку:', error);
            this.loadDemoFlights(); // fallback
        }
    }

    displayFlights(flights) {
        const container = document.getElementById('flightList');
        const title = document.getElementById('resultsTitle');

        if (!flights || flights.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="icon">😔</span>
                    <h3>Рейсів не знайдено</h3>
                    <p>Спробуйте змінити напрямок або дату</p>
                </div>
            `;
            title.textContent = 'На жаль, рейсів немає';
            return;
        }

        title.textContent = `Знайдено ${flights.length} рейс(ів)`;

        container.innerHTML = flights.map(flight => {
            const dep = flight.departure_time ? new Date(flight.departure_time) : null;
            const arr = flight.arrival_time ? new Date(flight.arrival_time) : null;
            const depStr = dep ? dep.toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Н/Д';
            const arrStr = arr ? arr.toLocaleString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Н/Д';
            let duration = 'Н/Д';
            if (dep && arr) {
                const diff = (arr - dep) / 1000 / 60;
                const h = Math.floor(diff / 60);
                const m = Math.round(diff % 60);
                duration = h > 0 ? `${h} год ${m} хв` : `${m} хв`;
            }

            return `
                <div class="flight-card" data-flight-id="${flight.flight_id}">
                    <div class="flight-info">
                        <div class="flight-route">
                            <span>${this.escapeHtml(flight.origin)}</span>
                            <span class="arrow">✈️</span>
                            <span>${this.escapeHtml(flight.destination)}</span>
                        </div>
                        <div>
                            <span class="flight-airline">${this.escapeHtml(flight.airline)}</span>
                            <span class="flight-number">${this.escapeHtml(flight.flight_number || 'N/A')}</span>
                        </div>
                    </div>
                    <div class="flight-time">
                        <div class="time">🛫 ${depStr}</div>
                        <div class="time">🛬 ${arrStr}</div>
                        <div class="duration">⏱️ ${duration}</div>
                    </div>
                    <div class="flight-price">
                        <div class="price">${this.formatPrice(flight.price)}</div>
                        <div class="seats">${flight.available_seats} місць</div>
                        <button class="book-btn" data-flight-id="${flight.flight_id}">Забронювати</button>
                    </div>
                </div>
            `;
        }).join('');

        // Додаємо обробники для кнопок бронювання
        document.querySelectorAll('.book-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const flightId = e.target.dataset.flightId;
                const flight = flights.find(f => f.flight_id === flightId);
                if (flight) this.openBookingModal(flight);
            });
        });
    }

    loadDemoFlights() {
        // Демо-дані (як у попередній гілці)
        const demoFlights = [
            {
                flight_id: 'FL-DEMO-001',
                airline: 'Sky Airlines',
                origin: 'Київ',
                destination: 'Львів',
                departure_time: new Date(Date.now() + 3600000 * 2).toISOString(),
                arrival_time: new Date(Date.now() + 3600000 * 4).toISOString(),
                price: 2500,
                available_seats: 45,
                flight_number: 'SA-102',
                status: 'scheduled'
            },
            {
                flight_id: 'FL-DEMO-002',
                airline: 'EuroJet',
                origin: 'Київ',
                destination: 'Одеса',
                departure_time: new Date(Date.now() + 3600000 * 5).toISOString(),
                arrival_time: new Date(Date.now() + 3600000 * 7).toISOString(),
                price: 3200,
                available_seats: 32,
                flight_number: 'EJ-205',
                status: 'scheduled'
            },
            {
                flight_id: 'FL-DEMO-003',
                airline: 'Ukrainian Wings',
                origin: 'Львів',
                destination: 'Київ',
                departure_time: new Date(Date.now() + 3600000 * 8).toISOString(),
                arrival_time: new Date(Date.now() + 3600000 * 10).toISOString(),
                price: 2700,
                available_seats: 38,
                flight_number: 'UW-303',
                status: 'delayed'
            }
        ];
        this.displayFlights(demoFlights);
    }

    // ===== Бронювання =====

    openBookingModal(flight) {
        this.selectedFlight = flight;
        const modal = document.getElementById('bookingModal');
        const info = document.getElementById('bookingInfo');
        info.innerHTML = `
            <p><strong>Рейс:</strong> ${flight.flight_number} (${flight.airline})</p>
            <p><strong>Маршрут:</strong> ${flight.origin} → ${flight.destination}</p>
            <p><strong>Вартість:</strong> ${this.formatPrice(flight.price)} за 1 місце</p>
            <p><strong>Доступно місць:</strong> ${flight.available_seats}</p>
            <p><strong>Дата вильоту:</strong> ${new Date(flight.departure_time).toLocaleString('uk-UA')}</p>
        `;
        // Скидаємо форму
        document.getElementById('bookingForm').reset();
        document.getElementById('bookingResult').style.display = 'none';
        // Очищаємо пасажирів, залишаємо тільки один рядок
        const container = document.getElementById('passengersContainer');
        container.innerHTML = `
            <label>Пасажири</label>
            <div class="passenger-entry">
                <input type="text" class="passenger-name" placeholder="ПІБ пасажира" required>
                <input type="text" class="passenger-passport" placeholder="Номер паспорта (AA123456)" required>
            </div>
        `;
        this.passengerCount = 1;
        modal.style.display = 'block';
    }

    closeModal() {
        document.getElementById('bookingModal').style.display = 'none';
    }

    addPassengerField() {
        const container = document.getElementById('passengersContainer');
        const entry = document.createElement('div');
        entry.className = 'passenger-entry';
        entry.innerHTML = `
            <input type="text" class="passenger-name" placeholder="ПІБ пасажира" required>
            <input type="text" class="passenger-passport" placeholder="Номер паспорта (AA123456)" required>
        `;
        container.appendChild(entry);
        this.passengerCount++;
    }

    async submitBooking() {
        const flight = this.selectedFlight;
        if (!flight) {
            alert('Рейс не вибрано');
            return;
        }

        const userName = document.getElementById('userName').value.trim();
        const userEmail = document.getElementById('userEmail').value.trim();
        const userPhone = document.getElementById('userPhone').value.trim();
        const notes = document.getElementById('bookingNotes').value.trim();

        // Збираємо пасажирів
        const nameInputs = document.querySelectorAll('.passenger-name');
        const passportInputs = document.querySelectorAll('.passenger-passport');
        const passengers = [];
        for (let i = 0; i < nameInputs.length; i++) {
            const name = nameInputs[i].value.trim();
            const passport = passportInputs[i].value.trim().toUpperCase();
            if (name && passport) {
                passengers.push({ name, passport });
            }
        }

        if (passengers.length === 0) {
            alert('Додайте хоча б одного пасажира');
            return;
        }

        if (!userName || !userEmail) {
            alert("Введіть ваше ім'я та email");
            return;
        }

        // Перевірка кількості місць (пасажирів)
        if (passengers.length > flight.available_seats) {
            alert(`На рейсі залишилось лише ${flight.available_seats} місць. Зменшіть кількість пасажирів.`);
            return;
        }

        // Формуємо дані для відправки
        const bookingData = {
            user_id: 'user-' + Date.now(), // тимчасовий ID
            flight_id: flight.flight_id,
            seats: passengers.length,
            passengers: passengers,
            notes: notes,
            contact: { name: userName, email: userEmail, phone: userPhone }
        };

        try {
            const response = await fetch(`${this.apiBase}/api/bookings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookingData)
            });

            const result = await response.json();
            const resultDiv = document.getElementById('bookingResult');
            resultDiv.style.display = 'block';

            if (response.ok) {
                resultDiv.className = 'success';
                resultDiv.innerHTML = `
                    ✅ Бронювання успішне!<br>
                    <strong>Код підтвердження:</strong> ${result.booking.confirmation_code || 'N/A'}<br>
                    <strong>ID бронювання:</strong> ${result.booking.booking_id}
                `;
                // Оновлюємо список рейсів, щоб оновити кількість місць
                this.searchFlights();
                // через 5 секунд закриваємо модалку
                setTimeout(() => this.closeModal(), 5000);
            } else {
                resultDiv.className = 'error';
                resultDiv.textContent = '❌ ' + (result.error || 'Помилка бронювання');
            }
        } catch (error) {
            console.error('Помилка:', error);
            const resultDiv = document.getElementById('bookingResult');
            resultDiv.style.display = 'block';
            resultDiv.className = 'error';
            resultDiv.textContent = '❌ Помилка з\'єднання з сервером';
        }
    }

    async loadBookings() {
        // Завантаження історії бронювань (для демонстрації)
        // Можна додати відображення
    }

    // ===== Helpers =====
    formatPrice(price) {
        return new Intl.NumberFormat('uk-UA', {
            style: 'currency',
            currency: 'UAH',
            minimumFractionDigits: 0
        }).format(price);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Ініціалізація
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BookingApp();
});
