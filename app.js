/**
 * Flight Booking Service - Client Application with Payment
 */

class FlightBookingApp {
    constructor() {
        this.apiBase = '';
        this.currentUser = null;
        this.selectedMethod = 'card';
        this.bookingData = null;
        this.initializeEventListeners();
        this.loadDemoFlights();
        this.checkAuthStatus();
        this.loadPaymentMethods();
        this.setupPaymentListeners();
    }

    initializeEventListeners() {
        // Пошук
        document.getElementById('searchBtn')?.addEventListener('click', () => {
            this.searchFlights();
        });

        // Логін
        document.getElementById('loginBtn')?.addEventListener('click', () => {
            this.showLoginModal();
        });

        // Enter для пошуку
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const searchForm = document.querySelector('.search-form');
                if (searchForm && searchForm.contains(e.target)) {
                    this.searchFlights();
                }
            }
        });

        // Кнопки бронювання
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('book-btn')) {
                const flightId = e.target.dataset.flightId;
                if (flightId) {
                    this.bookFlight(flightId);
                }
            }
        });

        // Закриття модалки
        document.querySelector('.close')?.addEventListener('click', () => {
            document.getElementById('loginModal').style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === document.getElementById('loginModal')) {
                document.getElementById('loginModal').style.display = 'none';
            }
        });

        // Форма логіну
        document.getElementById('loginForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });
    }

    // ============ Payment Methods ============

    setupPaymentListeners() {
        const payBtn = document.getElementById('payBtn');
        if (payBtn) {
            payBtn.addEventListener('click', () => {
                this.processPayment();
            });
        }

        // Автоформатування картки
        const cardNumber = document.getElementById('cardNumber');
        if (cardNumber) {
            cardNumber.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 16) value = value.slice(0, 16);
                value = value.replace(/(.{4})/g, '$1 ').trim();
                e.target.value = value;
                this.detectCardType(value);
            });
        }

        // Форматування дати
        const cardExpiry = document.getElementById('cardExpiry');
        if (cardExpiry) {
            cardExpiry.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 4) value = value.slice(0, 4);
                if (value.length >= 2) {
                    value = value.slice(0, 2) + '/' + value.slice(2);
                }
                e.target.value = value;
            });
        }

        // CVV - тільки цифри
        const cardCvv = document.getElementById('cardCvv');
        if (cardCvv) {
            cardCvv.addEventListener('input', (e) => {
                e.target.value = e.target.value.replace(/\D/g, '').slice(0, 4);
            });
        }
    }

    loadPaymentMethods() {
        const container = document.getElementById('paymentMethods');
        if (!container) return;

        const methods = [
            { id: 'card', name: 'Банківська картка', icon: '💳', fee: '1.5%' },
            { id: 'google_pay', name: 'Google Pay', icon: '📱', fee: '1%' },
            { id: 'apple_pay', name: 'Apple Pay', icon: '🍎', fee: '1%' },
            { id: 'bank_transfer', name: 'Банківський переказ', icon: '🏦', fee: '0.5%' }
        ];

        container.innerHTML = methods.map(method => `
            <button class="payment-method-btn ${method.id === this.selectedMethod ? 'active' : ''}" 
                    data-method="${method.id}">
                <span class="icon">${method.icon}</span>
                ${method.name}
                <div class="fee">Комісія: ${method.fee}</div>
            </button>
        `).join('');

        // Обробники кліків
        container.querySelectorAll('.payment-method-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectPaymentMethod(btn.dataset.method);
            });
        });
    }

    selectPaymentMethod(methodId) {
        this.selectedMethod = methodId;
        
        // Оновлення кнопок
        document.querySelectorAll('.payment-method-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.method === methodId);
        });

        // Показ форми для картки
        const cardForm = document.getElementById('cardForm');
        if (cardForm) {
            cardForm.classList.toggle('active', methodId === 'card');
        }

        // Оновлення комісії
        this.updateFee(methodId);
    }

    updateFee(methodId) {
        const feeDisplay = document.getElementById('feeDisplay');
        const totalDisplay = document.getElementById('totalAmount');
        if (!feeDisplay || !totalDisplay) return;

        const fees = {
            'card': 0.015,
            'google_pay': 0.01,
            'apple_pay': 0.01,
            'bank_transfer': 0.005
        };

        const price = parseFloat(this.bookingData?.totalPrice || 5000);
        const fee = fees[methodId] || 0;
        const feeAmount = price * fee;
        const total = price + feeAmount;

        feeDisplay.textContent = `${feeAmount.toFixed(0)} ₴ (${(fee * 100).toFixed(1)}%)`;
        totalDisplay.textContent = `${total.toFixed(0)} ₴`;
    }

    detectCardType(cardNumber) {
        const clean = cardNumber.replace(/\s/g, '');
        let type = 'Unknown';
        
        if (clean.startsWith('4')) type = 'Visa';
        else if (clean.startsWith('5')) type = 'Mastercard';
        else if (clean.startsWith('3')) type = 'American Express';
        else if (clean.startsWith('6')) type = 'Discover';
        
        // Оновлення іконок
        document.querySelectorAll('.card-icons span').forEach(el => {
            el.classList.toggle('active', el.textContent.includes(type));
        });
    }

    // ============ Payment Processing ============

    async processPayment() {
        const payBtn = document.getElementById('payBtn');
        const statusDiv = document.getElementById('paymentStatus');
        
        if (!this.bookingData) {
            this.showMessage('Бронювання не знайдено', 'error');
            return;
        }

        // Валідація для картки
        if (this.selectedMethod === 'card') {
            const cardNumber = document.getElementById('cardNumber').value;
            const cardExpiry = document.getElementById('cardExpiry').value;
            const cardCvv = document.getElementById('cardCvv').value;
            const cardholderName = document.getElementById('cardholderName').value;

            if (!cardNumber || cardNumber.replace(/\s/g, '').length < 16) {
                this.showMessage('Введіть правильний номер картки', 'error');
                return;
            }

            if (!cardExpiry || cardExpiry.length < 5) {
                this.showMessage('Введіть термін дії картки (MM/YY)', 'error');
                return;
            }

            if (!cardCvv || cardCvv.length < 3) {
                this.showMessage('Введіть CVV код', 'error');
                return;
            }

            if (!cardholderName || cardholderName.length < 2) {
                this.showMessage('Введіть ім\'я власника картки', 'error');
                return;
            }
        }

        // Показуємо завантаження
        payBtn.disabled = true;
        payBtn.textContent = '⏳ Обробка...';
        statusDiv.className = 'payment-status show pending';
        document.getElementById('statusIcon').textContent = '⏳';
        document.getElementById('statusMessage').textContent = 'Обробка платежу...';

        try {
            const payload = {
                booking_id: this.bookingData.bookingId,
                method: this.selectedMethod,
                amount: this.bookingData.totalPrice
            };

            // Додаємо дані картки якщо потрібно
            if (this.selectedMethod === 'card') {
                payload.card_data = {
                    card_number: document.getElementById('cardNumber').value,
                    expiry_date: document.getElementById('cardExpiry').value,
                    cvv: document.getElementById('cardCvv').value,
                    cardholder_name: document.getElementById('cardholderName').value
                };
            }

            const response = await fetch(`${this.apiBase}/api/v1/payments/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            // Оновлюємо статус
            if (data.success) {
                statusDiv.className = 'payment-status show success';
                document.getElementById('statusIcon').textContent = '✅';
                document.getElementById('statusMessage').textContent = data.message || 'Оплата успішна!';
                this.showMessage('✅ Оплата пройшла успішно!', 'success');
                
                // Оновлюємо бронювання
                if (data.booking) {
                    this.updateBookingSummary(data.booking);
                }
            } else {
                statusDiv.className = 'payment-status show error';
                document.getElementById('statusIcon').textContent = '❌';
                document.getElementById('statusMessage').textContent = data.message || 'Помилка оплати';
                this.showMessage(`❌ ${data.message || 'Помилка оплати'}`, 'error');
            }

        } catch (error) {
            console.error('Помилка оплати:', error);
            statusDiv.className = 'payment-status show error';
            document.getElementById('statusIcon').textContent = '❌';
            document.getElementById('statusMessage').textContent = 'Помилка з\'єднання з сервером';
            this.showMessage('❌ Помилка при обробці платежу', 'error');
        } finally {
            payBtn.disabled = false;
            payBtn.textContent = '💳 Оплатити';
        }
    }

    updateBookingSummary(booking) {
        if (!booking) return;
        
        document.getElementById('bookingId').textContent = booking.booking_id;
        document.getElementById('seatsCount').textContent = booking.seats || 2;
        document.getElementById('bookingPrice').textContent = `${booking.total_price || 5000} ₴`;
        
        // Оновлюємо загальну суму
        const total = booking.total_price || 5000;
        this.bookingData = {
            bookingId: booking.booking_id,
            totalPrice: total
        };
        
        this.updateFee(this.selectedMethod);
    }

    // ============ Booking Methods ============

    async bookFlight(flightId) {
        if (!this.currentUser) {
            this.showMessage('Будь ласка, увійдіть в систему', 'warning');
            document.getElementById('loginBtn').click();
            return;
        }

        const seats = 1;
        const passengers = [{
            name: this.currentUser.full_name || this.currentUser.username,
            passport: 'DEMO123456'
        }];

        try {
            const response = await fetch(`${this.apiBase}/api/v1/bookings`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.currentUser.user_id,
                    flight_id: flightId,
                    seats: seats,
                    passengers: passengers
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.showMessage(`✅ Бронювання ${data.booking_id} створено!`, 'success');
                
                // Зберігаємо дані для оплати
                this.bookingData = {
                    bookingId: data.booking_id,
                    totalPrice: data.total_price || 5000
                };
                
                // Переходимо до оплати
                this.showPaymentPage(data);
                this.searchFlights();
            } else {
                this.showMessage(data.error || 'Помилка бронювання', 'error');
            }
        } catch (error) {
            console.error('Помилка бронювання:', error);
            this.showMessage('Помилка при бронюванні', 'error');
        }
    }

    showPaymentPage(booking) {
        // Оновлюємо дані на сторінці оплати
        document.getElementById('bookingId').textContent = booking.booking_id;
        document.getElementById('seatsCount').textContent = booking.seats || 1;
        document.getElementById('bookingPrice').textContent = `${booking.total_price || 5000} ₴`;
        
        // Прокручуємо до оплати
        document.querySelector('.payment-section')?.scrollIntoView({ behavior: 'smooth' });
        
        // Оновлюємо комісію
        this.bookingData = {
            bookingId: booking.booking_id,
            totalPrice: booking.total_price || 5000
        };
        this.updateFee(this.selectedMethod);
    }

    // ============ Search Methods ============

    async searchFlights() {
        const origin = document.getElementById('origin')?.value?.trim() || 'Київ';
        const destination = document.getElementById('destination')?.value?.trim() || 'Львів';
        const date = document.getElementById('date')?.value || '';

        try {
            const params = new URLSearchParams({ origin, destination });
            if (date) params.append('date', date);

            const response = await fetch(`${this.apiBase}/api/v1/flights/search?${params}`);
            const data = await response.json();

            if (data.error) {
                this.showMessage(data.error, 'error');
                return;
            }

            this.displayFlights(data.flights);
        } catch (error) {
            console.error('Помилка пошуку:', error);
            this.showMessage('Помилка при пошуку рейсів', 'error');
        }
    }

    displayFlights(flights) {
        const container = document.getElementById('flightList');
        if (!container) return;
        
        if (!flights || flights.length === 0) {
            container.innerHTML = `
                <div class="no-flights" style="text-align:center;padding:3rem;background:white;border-radius:10px;">
                    <p style="font-size:3rem;margin-bottom:1rem;">😔</p>
                    <p style="font-size:1.2rem;color:#666;">Рейсів за цим напрямком не знайдено</p>
                </div>
            `;
            return;
        }

        container.innerHTML = flights.map(flight => `
            <div class="flight-card">
                <div class="flight-info">
                    <div class="flight-route">
                        <strong>${this.escapeHtml(flight.origin)}</strong>
                        <span class="arrow">✈️</span>
                        <strong>${this.escapeHtml(flight.destination)}</strong>
                    </div>
                    <div class="flight-details">
                        <span>Рейс: ${this.escapeHtml(flight.flight_number || 'N/A')}</span>
                        <span>Авіакомпанія: ${this.escapeHtml(flight.airline)}</span>
                    </div>
                </div>
                <div class="flight-time">
                    <div>🛫 Виліт: ${this.formatDate(flight.departure_time)}</div>
                    <div>🛬 Прибуття: ${this.formatDate(flight.arrival_time)}</div>
                </div>
                <div class="flight-price">
                    <div class="price">${this.formatPrice(flight.price)}</div>
                    <div class="seats">${flight.available_seats} місць</div>
                    <button class="book-btn" data-flight-id="${flight.flight_id}">
                        Забронювати
                    </button>
                </div>
            </div>
        `).join('');
    }

    // ============ User Methods ============

    async login() {
        const username = document.getElementById('loginUsername')?.value?.trim();
        const password = document.getElementById('loginPassword')?.value;

        if (!username || !password) {
            this.showMessage('Введіть логін та пароль', 'warning');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/api/v1/users/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentUser = data.user;
                localStorage.setItem('user', JSON.stringify(this.currentUser));
                this.showMessage(`👋 Вітаємо, ${this.currentUser.full_name || this.currentUser.username}!`, 'success');
                document.getElementById('loginModal').style.display = 'none';
                document.getElementById('loginBtn').textContent = '👤 Профіль';
                this.loadUserBookings();
            } else {
                this.showMessage(data.error || 'Невірний логін або пароль', 'error');
            }
        } catch (error) {
            console.error('Помилка входу:', error);
            this.showMessage('Помилка при вході', 'error');
        }
    }

    showLoginModal() {
        document.getElementById('loginModal').style.display = 'block';
    }

    checkAuthStatus() {
        const saved = localStorage.getItem('user');
        if (saved) {
            try {
                this.currentUser = JSON.parse(saved);
                document.getElementById('loginBtn').textContent = '👤 Профіль';
                this.loadUserBookings();
            } catch (e) {
                localStorage.removeItem('user');
            }
        }
    }

    async loadUserBookings() {
        if (!this.currentUser) return;

        try {
            const response = await fetch(`${this.apiBase}/api/v1/bookings/user/${this.currentUser.user_id}`);
            const data = await response.json();

            if (response.ok) {
                this.displayBookings(data.bookings);
            }
        } catch (error) {
            console.error('Помилка завантаження бронювань:', error);
        }
    }

    displayBookings(bookings) {
        const container = document.getElementById('bookingList');
        if (!container) return;
        
        if (!bookings || bookings.length === 0) {
            container.innerHTML = '<p class="empty-message">📭 У вас немає активних бронювань</p>';
            return;
        }

        container.innerHTML = bookings.map(booking => `
            <div class="booking-card">
                <div>
                    <strong>Бронювання: ${booking.booking_id}</strong>
                    <div style="color:#666;font-size:0.9rem;">
                        Рейс: ${booking.flight_id}
                    </div>
                </div>
                <div>
                    <span class="booking-status ${booking.status}">
                        ${this.getStatusText(booking.status)}
                    </span>
                    <div style="font-size:0.9rem;color:#66
