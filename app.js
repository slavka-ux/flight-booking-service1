/**
 * Flight Booking – клієнтська логіка для GitHub Pages
 * API_URL можна змінити на адресу вашого бекенду
 */

class BookingApp {
    constructor() {
        // === НАЛАШТУЙТЕ СЮДИ URL ВАШОГО API ===
        this.API_URL = 'https://your-backend.onrender.com'; // замініть на реальний URL
        // Якщо бекенд запущено локально – використовуйте 'http://localhost:5000'

        this.token = localStorage.getItem('auth_token') || null;
        this.currentUser = null;
        this.selectedFlight = null;
        this.init();
    }

    init() {
        // Перевірка токена при завантаженні
        if (this.token) {
            this.fetchCurrentUser();
        } else {
            this.updateUIForGuest();
        }

        // Пошук рейсів
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.searchFlights();
        });

        // Кнопки аутентифікації
        document.getElementById('loginBtn').addEventListener('click', () => this.openModal('login'));
        document.getElementById('registerBtn').addEventListener('click', () => this.openModal('register'));
        document.getElementById('logoutBtn').addEventListener('click', () => this.logout());

        // Закриття модалок
        const closeMap = {
            'closeLogin': 'login',
            'closeRegister': 'register',
            'closeBooking': 'booking'
        };
        Object.keys(closeMap).forEach(id => {
            document.getElementById(id).addEventListener('click', () => {
                this.closeModal(closeMap[id]);
            });
        });
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                const id = e.target.id.replace('Modal', '').toLowerCase();
                this.closeModal(id);
            }
        });

        // Перемикання між формами
        document.getElementById('switchToRegister').addEventListener('click', (e) => {
            e.preventDefault();
            this.closeModal('login');
            this.openModal('register');
        });
        document.getElementById('switchToLogin').addEventListener('click', (e) => {
            e.preventDefault();
            this.closeModal('register');
            this.openModal('login');
        });

        // Форми
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });
        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.register();
        });

        // Бронювання
        document.getElementById('addPassengerBtn').addEventListener('click', () => {
            this.addPassengerField();
        });
        document.getElementById('bookingForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitBooking();
        });

        // Завантажуємо демо-рейси при старті
        this.loadDemoFlights();
    }

    // ===== Аутентифікація =====

    async fetchCurrentUser() {
        try {
            const res = await fetch(`${this.API_URL}/api/auth/me`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (res.ok) {
                const user = await res.json();
                this.currentUser = user;
                this.updateUIForAuth(user);
                this.loadUserBookings();
            } else {
                this.token = null;
                localStorage.removeItem('auth_token');
                this.updateUIForGuest();
            }
        } catch (e) {
            console.error('Помилка перевірки токена:', e);
            this.token = null;
            localStorage.removeItem('auth_token');
            this.updateUIForGuest();
        }
    }

    async login() {
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;
        const resultDiv = document.getElementById('loginResult');

        if (!username || !password) {
            resultDiv.className = 'auth-result error';
            resultDiv.textContent = 'Введіть логін та пароль';
            return;
        }

        try {
            const res = await fetch(`${this.API_URL}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (res.ok) {
                this.token = data.token;
                localStorage.setItem('auth_token', this.token);
                this.currentUser = data.user;
                this.updateUIForAuth(data.user);
                resultDiv.className = 'auth-result success';
                resultDiv.textContent = '✅ Вхід успішний!';
                setTimeout(() => this.closeModal('login'), 1000);
                this.loadUserBookings();
                this.searchFlights(); // оновити рейси
            } else {
                resultDiv.className = 'auth-result error';
                resultDiv.textContent = '❌ ' + (data.error || 'Помилка входу');
            }
        } catch (e) {
            resultDiv.className = 'auth-result error';
            resultDiv.textContent = '❌ Помилка з\'єднання з сервером';
            console.error(e);
        }
    }

    async register() {
        const username = document.getElementById('regUsername').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value;
        const fullName = document.getElementById('regFullName').value.trim();
        const phone = document.getElementById('regPhone').value.trim();
        const resultDiv = document.getElementById('registerResult');

        if (!username || !email || !password) {
            resultDiv.className = 'auth-result error';
            resultDiv.textContent = 'Заповніть всі обов\'язкові поля';
            return;
        }

        try {
            const res = await fetch(`${this.API_URL}/api/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password, full_name: fullName, phone })
            });
            const data = await res.json();

            if (res.ok) {
                resultDiv.className = 'auth-result success';
                resultDiv.textContent = '✅ Реєстрація успішна! Тепер увійдіть.';
                setTimeout(() => {
                    this.closeModal('register');
                    this.openModal('login');
                }, 1500);
            } else {
                resultDiv.className = 'auth-result error';
                resultDiv.textContent = '❌ ' + (data.error || 'Помилка реєстрації');
            }
        } catch (e) {
            resultDiv.className = 'auth-result error';
            resultDiv.textContent = '❌ Помилка з\'єднання з сервером';
            console.error(e);
        }
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        localStorage.removeItem('auth_token');
        this.updateUIForGuest();
        alert('Ви вийшли з системи');
    }

    updateUIForAuth(user) {
        document.getElementById('loginBtn').style.display = 'none';
        document.getElementById('registerBtn').style.display = 'none';
        document.getElementById('logoutBtn').style.display = 'inline-block';
        document.getElementById('userDisplay').style.display = 'inline';
        document.getElementById('userDisplay').textContent = `👤 ${user.full_name || user.username}`;
    }

    updateUIForGuest() {
        document.getElementById('loginBtn').style.display = 'inline-block';
        document.getElementById('registerBtn').style.display = 'inline-block';
        document.getElementById('logoutBtn').style.display = 'none';
        document.getElementById('userDisplay').style.display = 'none';
    }

    openModal(type) {
        const map = { 'login': 'loginModal', 'register': 'registerModal', 'booking': 'bookingModal' };
        const el = document.getElementById(map[type]);
        if (el) {
            el.style.display = 'block';
            // Очищаємо результати
            if (type === 'login') document.getElementById('loginResult').textContent = '';
            if (type === 'register') document.getElementById('registerResult').textContent = '';
        }
    }

    closeModal(type) {
        const map = { 'login': 'loginModal', 'register': 'registerModal', 'booking': 'bookingModal' };
        const el = document.getElementById(map[type]);
        if (el) el.style.display = 'none';
    }

    // ===== Пошук рейсів =====

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
            const url = `${this.API_URL}/api/flights/search?${params}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error('Помилка завантаження');
            const data = await res.json();
            this.displayFlights(data.flights || []);
        } catch (e) {
            console.error('Помилка пошуку:', e);
            this.loadDemoFlights(); // fallback на демо-дані
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
            const depStr = dep ? dep.toLocaleString('uk-UA', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            }) : 'Н/Д';
            const arrStr = arr ? arr.toLocaleString('uk-UA', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            }) : 'Н/Д';
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

        // Обробники для кнопок бронювання
        document.querySelectorAll('.book-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const flightId = e.target.dataset.flightId;
                const flight = flights.find(f => f.flight_id === flightId);
                if (flight) this.openBookingModal(flight);
            });
        });
    }

    loadDemoFlights() {
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
        if (!this.token) {
            alert('Щоб забронювати квиток, увійдіть в систему.');
            this.openModal('login');
            return;
        }
        this.selectedFlight = flight;
        const info = document.getElementById('bookingInfo');
        info.innerHTML = `
            <p><strong>Рейс:</strong> ${flight.flight_number} (${flight.airline})</p>
            <p><strong>Маршрут:</strong> ${flight.origin} → ${flight.destination}</p>
            <p><strong>Вартість:</strong> ${this.formatPrice(flight.price)} за 1 місце</p>
            <p><strong>Доступно місць:</strong> ${flight.available_seats}</p>
            <p><strong>Дата вильоту:</strong> ${new Date(flight.departure_time).toLocaleString('uk-UA')}</p>
        `;
        document.getElementById('bookingForm').reset();
        document.getElementById('bookingResult').style.display = 'none';
        document.getElementById('bookingResult').className = '';
        // Скидаємо пасажирів до одного
        const container = document.getElementById('passengersContainer');
        container.innerHTML = `
            <label>Пасажири</label>
            <div class="passenger-entry">
                <input type="text" class="passenger-name" placeholder="ПІБ пасажира" required>
                <input type="text" class="passenger-passport" placeholder="Номер паспорта (AA123456)" required>
            </div>
        `;
        this.openModal('booking');
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
    }

    async submitBooking() {
        const flight = this.selectedFlight;
        if (!flight) return;

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
        if (passengers.length > flight.available_seats) {
            alert(`На рейсі залишилось лише ${flight.available_seats} місць.`);
            return;
        }

        const notes = document.getElementById('bookingNotes').value.trim();
        const bookingData = {
            flight_id: flight.flight_id,
            seats: passengers.length,
            passengers: passengers,
            notes: notes
        };

        try {
            const res = await fetch(`${this.API_URL}/api/bookings`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(bookingData)
            });
            const data = await res.json();
            const resultDiv = document.getElementById('bookingResult');
            resultDiv.style.display = 'block';

            if (res.ok) {
                resultDiv.className = 'success';
                resultDiv.innerHTML = `
                    ✅ Бронювання успішне!<br>
                    <strong>Код:</strong> ${data.booking.confirmation_code || 'N/A'}<br>
                    <strong>ID:</strong> ${data.booking.booking_id}
                `;
                this.searchFlights(); // оновлюємо кількість місць
                this.loadUserBookings();
                setTimeout(() => this.closeModal('booking'), 4000);
            } else {
                resultDiv.className = 'error';
                resultDiv.textContent = '❌ ' + (data.error || 'Помилка бронювання');
            }
        } catch (e) {
            console.error(e);
            const resultDiv = document.getElementById('bookingResult');
            resultDiv.style.display = 'block';
            resultDiv.className = 'error';
            resultDiv.textContent = '❌ Помилка з\'єднання з сервером';
        }
    }

    async loadUserBookings() {
        if (!this.token) return;
        try {
            const res = await fetch(`${this.API_URL}/api/bookings/user`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (res.ok) {
                const data = await res.json();
                // Можна відобразити список бронювань у консолі або на сторінці
                console.log('Мої бронювання:', data.bookings);
            }
        } catch (e) {
            console.error('Помилка завантаження бронювань:', e);
        }
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

// Ініціалізація після завантаження DOM
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BookingApp();
});
