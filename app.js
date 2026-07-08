/**
 * Flight Search - клієнтська логіка
 */

class FlightSearchApp {
    constructor() {
        this.apiBase = ''; // можна змінити на URL бекенду
        this.init();
    }

    init() {
        // Форма пошуку
        const form = document.getElementById('searchForm');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.searchFlights();
        });

        // Пошук по Enter на полях
        document.querySelectorAll('#origin, #destination, #date').forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.searchFlights();
                }
            });
        });

        // Завантажуємо початкові рейси (демо-дані)
        this.loadDemoFlights();
    }

    async searchFlights() {
        const origin = document.getElementById('origin').value.trim();
        const destination = document.getElementById('destination').value.trim();
        const date = document.getElementById('date').value;

        // Валідація
        if (!origin || !destination) {
            this.showError('Будь ласка, вкажіть місто вильоту та прильоту');
            return;
        }

        if (origin.toLowerCase() === destination.toLowerCase()) {
            this.showError('Місто вильоту і прильоту не можуть бути однаковими');
            return;
        }

        // Показуємо завантаження
        this.showLoading(true);

        try {
            const params = new URLSearchParams({ origin, destination });
            if (date) params.append('date', date);

            const url = `${this.apiBase}/api/flights/search?${params}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP помилка: ${response.status}`);
            }

            const data = await response.json();
            this.displayFlights(data.flights || []);
        } catch (error) {
            console.error('Помилка пошуку:', error);
            this.showError('Не вдалося завантажити рейси. Спробуйте пізніше.');
            // Якщо бекенд не доступний, показуємо демо-дані
            this.loadDemoFlights();
        } finally {
            this.showLoading(false);
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
            title.textContent = 'На жаль, рейсів за вашим запитом немає';
            return;
        }

        title.textContent = `Знайдено ${flights.length} рейс(ів)`;

        container.innerHTML = flights.map(flight => {
            const departure = flight.departure_time ? new Date(flight.departure_time) : null;
            const arrival = flight.arrival_time ? new Date(flight.arrival_time) : null;

            const departureStr = departure ? departure.toLocaleString('uk-UA', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            }) : 'Н/Д';

            const arrivalStr = arrival ? arrival.toLocaleString('uk-UA', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            }) : 'Н/Д';

            // Розрахунок тривалості
            let durationStr = 'Н/Д';
            if (departure && arrival) {
                const diff = (arrival - departure) / 1000 / 60; // хвилини
                const hours = Math.floor(diff / 60);
                const mins = Math.round(diff % 60);
                durationStr = hours > 0 ? `${hours} год ${mins} хв` : `${mins} хв`;
            }

            const statusClass = flight.status || 'scheduled';
            const statusText = this.getStatusText(statusClass);

            return `
                <div class="flight-card">
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
                        <div class="time">🛫 ${departureStr}</div>
                        <div class="time">🛬 ${arrivalStr}</div>
                        <div class="duration">⏱️ ${durationStr}</div>
                    </div>
                    <div class="flight-price">
                        <div class="price">${this.formatPrice(flight.price)}</div>
                        <div class="seats">${flight.available_seats} місць</div>
                        <div class="status ${statusClass}">${statusText}</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    loadDemoFlights() {
        // Демо-дані для першого завантаження
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

    showLoading(show) {
        const indicator = document.getElementById('loadingIndicator');
        if (indicator) {
            indicator.style.display = show ? 'block' : 'none';
        }
    }

    showError(message) {
        const container = document.getElementById('resultsContainer');
        // Видаляємо попереднє повідомлення
        const oldMsg = container.querySelector('.message');
        if (oldMsg) oldMsg.remove();

        const msg = document.createElement('div');
        msg.className = 'message error';
        msg.textContent = message;
        container.prepend(msg);

        // Автоматичне зникнення через 5 секунд
        setTimeout(() => {
            if (msg.parentNode) msg.remove();
        }, 5000);
    }

    getStatusText(status) {
        const map = {
            'scheduled': 'Заплановано',
            'delayed': 'Затримано',
            'cancelled': 'Скасовано',
            'completed': 'Завершено'
        };
        return map[status] || status;
    }

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

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FlightSearchApp();
});
