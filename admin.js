/**
 * Admin Panel - Flight Booking Service
 */

class AdminPanel {
    constructor() {
        this.currentUser = null;
        this.flights = [];
        this.bookings = [];
        this.users = [];
        this.currentSection = 'dashboard';
        this.init();
    }

    async init() {
        // Перевірка авторизації
        await this.checkAuth();
        
        // Навігація
        this.setupNavigation();
        
        // Завантаження даних
        await this.loadDashboard();
        await this.loadFlights();
        await this.loadBookings();
        await this.loadUsers();
        
        // Форми
        this.setupForms();
        
        // Пошук і фільтри
        this.setupFilters();
    }

    setupNavigation() {
        const links = document.querySelectorAll('.admin-nav .nav-links a');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('href').substring(1);
                this.showSection(section);
                
                // Оновлення активного посилання
                links.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    showSection(sectionId) {
        this.currentSection = sectionId;
        
        // Показати відповідну секцію
        document.querySelectorAll('.admin-section').forEach(s => {
            s.classList.remove('active');
        });
        
        const target = document.getElementById(sectionId);
        if (target) {
            target.classList.add('active');
        }
    }

    async checkAuth() {
        const saved = localStorage.getItem('user');
        if (!saved) {
            window.location.href = '/';
            return;
        }
        
        try {
            this.currentUser = JSON.parse(saved);
            if (!this.currentUser.is_admin) {
                window.location.href = '/';
                return;
            }
        } catch (e) {
            window.location.href = '/';
        }
    }

    // ============ Dashboard ============

    async loadDashboard() {
        try {
            // Отримуємо статистику
            const [flightStats, bookingStats, userStats] = await Promise.all([
                this.fetchData('/api/v1/admin/flights/stats'),
                this.fetchData('/api/v1/admin/bookings/stats'),
                this.fetchData('/api/v1/admin/users/stats')
            ]);

            this.renderStats(flightStats, bookingStats, userStats);
            this.renderCharts(flightStats, bookingStats);
            this.renderRecentActivity();
        } catch (error) {
            console.error('Помилка завантаження дашборду:', error);
        }
    }

    renderStats(flightStats, bookingStats, userStats) {
        const grid = document.getElementById('statsGrid');
        if (!grid) return;

        const stats = [
            { icon: '✈️', value: flightStats.total || 0, label: 'Всього рейсів', change: '+12%' },
            { icon: '📋', value: bookingStats.total || 0, label: 'Всього бронювань', change: '+8%' },
            { icon: '👤', value: userStats.total || 0, label: 'Користувачів', change: '+5%' },
            { icon: '💰', value: (bookingStats.total_revenue || 0).toLocaleString(), label: 'Дохід (₴)', change: '+15%' },
            { icon: '✅', value: bookingStats.confirmed || 0, label: 'Підтверджено бронювань', change: '' },
            { icon: '⏳', value: bookingStats.pending || 0, label: 'Очікують', change: '' }
        ];

        grid.innerHTML = stats.map(stat => `
            <div class="stat-card">
                <span class="icon">${stat.icon}</span>
                <div class="value">${stat.value}</div>
                <div class="label">${stat.label}</div>
                ${stat.change ? `<div class="change positive">${stat.change}</div>` : ''}
            </div>
        `).join('');
    }

    renderCharts(flightStats, bookingStats) {
        // Діаграма статусів рейсів
        const flightChart = document.getElementById('flightStatusChart');
        if (flightChart) {
            const data = [
                { label: 'Заплановано', value: flightStats.scheduled || 0, color: '#27ae60' },
                { label: 'Затримано', value: flightStats.delayed || 0, color: '#f39c12' },
                { label: 'Скасовано', value: flightStats.cancelled || 0, color: '#e74c3c' },
                { label: 'Завершено', value: flightStats.completed || 0, color: '#3498db' }
            ];
            
            const maxValue = Math.max(...data.map(d => d.value), 1);
            flightChart.innerHTML = `
                <div class="bar-chart">
                    ${data.map(d => `
                        <div class="bar" style="height: ${(d.value / maxValue * 100)}%; background: ${d.color};">
                            <span class="value">${d.value}</span>
                            <span class="label">${d.label}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // Діаграма статусів бронювань
        const bookingChart = document.getElementById('bookingStatusChart');
        if (bookingChart) {
            const data = [
                { label: 'Очікує', value: bookingStats.pending || 0, color: '#f39c12' },
                { label: 'Підтверджено', value: bookingStats.confirmed || 0, color: '#27ae60' },
                { label: 'Скасовано', value: bookingStats.cancelled || 0, color: '#e74c3c' },
                { label: 'Завершено', value: bookingStats.completed || 0, color: '#3498db' }
            ];
            
            const maxValue = Math.max(...data.map(d => d.value), 1);
            bookingChart.innerHTML = `
                <div class="bar-chart">
                    ${data.map(d => `
                        <div class="bar" style="height: ${(d.value / maxValue * 100)}%; background: ${d.color};">
                            <span class="value">${d.value}</span>
                            <span class="label">${d.label}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    renderRecentActivity() {
        const container = document.getElementById('recentActivity');
        if (!container) return;

        // Імітація активності
        const activities = [
            { text: 'Користувач Іван Петренко забронював рейс SA-102', time: '5 хв тому' },
            { text: 'Додано новий рейс EJ-205 до Одеси', time: '15 хв тому' },
            { text: 'Підтверджено бронювання BK-003', time: '1 год тому' },
            { text: 'Скасовано рейс UW-303 через погодні умови', time: '2 год тому' },
            { text: 'Зареєстровано нового користувача: Maria_Shevchenko', time: '3 год тому' }
        ];

        container.innerHTML = activities.map(a => `
            <div class="activity-item">
                <span class="activity-text">${a.text}</span>
                <span class="activity-time">${a.time}</span>
            </div>
        `).join('');
    }

    // ============ Flights Management ============

    async loadFlights() {
        try {
            const data = await this.fetchData('/api/v1/admin/flights');
            this.flights = data.flights || [];
            this.renderFlights();
        } catch (error) {
            console.error('Помилка завантаження рейсів:', error);
        }
    }

    renderFlights(flights = null) {
        const container = document.getElementById('flightsList');
        if (!container) return;

        const list = flights || this.flights;
        
        if (list.length === 0) {
            container.innerHTML = '<p class="empty">🚫 Немає рейсів</p>';
            return;
        }

        container.innerHTML = list.map(flight => `
            <div class="admin-item">
                <div class="info">
                    <div class="title">${flight.flight_number} - ${flight.airline}</div>
                    <div class="subtitle">${flight.origin} → ${flight.destination}</div>
                    <div class="details">
                        ${new Date(flight.departure_time).toLocaleString()} | 
                        ${flight.available_seats} місць | 
                        ${flight.price.toLocaleString()} ₴
                        ${!flight.is_active ? ' | ⛔ Неактивний' : ''}
                    </div>
                </div>
                <div class="status-badge ${flight.status}">${this.getStatusText(flight.status)}</div>
                <div class="actions">
                    <button class="edit-btn" onclick="admin.editFlight('${flight.flight_id}')">✏️</button>
                    <button class="toggle-btn" onclick="admin.toggleFlight('${flight.flight_id}')">
                        ${flight.is_active ? '⏸️' : '▶️'}
                    </button>
                    <button class="delete-btn" onclick="admin.deleteFlight('${flight.flight_id}')">🗑️</button>
                </div>
            </div>
        `).join('');
    }

    filterFlights() {
        const search = document.getElementById('flightSearch')?.value?.toLowerCase() || '';
        const status = document.getElementById('flightStatusFilter')?.value || '';

        let filtered = this.flights.filter(f => {
            const matchSearch = f.flight_number.toLowerCase().includes(search) ||
                              f.airline.toLowerCase().includes(search) ||
                              f.origin.toLowerCase().includes(search) ||
                              f.destination.toLowerCase().includes(search);
            const matchStatus = !status || f.status === status;
            return matchSearch && matchStatus;
        });

        this.renderFlights(filtered);
    }

    // ============ Bookings Management ============

    async loadBookings() {
        try {
            const data = await this.fetchData('/api/v1/admin/bookings');
            this.bookings = data.bookings || [];
            this.renderBookings();
        } catch (error) {
            console.error('Помилка завантаження бронювань:', error);
        }
    }

    renderBookings(bookings = null) {
        const container = document.getElementById('bookingsList');
        if (!container) return;

        const list = bookings || this.bookings;
        
        if (list.length === 0) {
            container.innerHTML = '<p class="empty">📭 Немає бронювань</p>';
            return;
        }

        container.innerHTML = list.map(booking => `
            <div class="admin-item">
                <div class="info">
                    <div class="title">${booking.booking_id}</div>
                    <div class="subtitle">Користувач: ${booking.user_id} | Рейс: ${booking.flight_id}</div>
                    <div class="details">
                        ${booking.seats} місць | 
                        ${booking.total_price.toLocaleString()} ₴ | 
                        ${new Date(booking.booking_date).toLocaleString()}
                        ${booking.is_fully_paid() ? ' | ✅ Оплачено' : ' | ⏳ Очікує оплату'}
                    </div>
                </div>
                <div class="status-badge ${booking.status}">${this.getBookingStatusText(booking.status)}</div>
                <div class="actions">
                    ${booking.status === 'pending' ? 
                        `<button class="edit-btn" onclick="admin.confirmBooking('${booking.booking_id}')">✅</button>` : ''}
                    ${booking.status === 'confirmed' ? 
                        `<button class="edit-btn" onclick="admin.completeBooking('${booking.booking_id}')">🎯</button>` : ''}
                    ${booking.status !== 'cancelled' && booking.status !== 'completed' ? 
                        `<button class="delete-btn" onclick="admin.cancelBooking('${booking.booking_id}')">❌</button>` : ''}
                </div>
            </div>
        `).join('');
    }

    filterBookings() {
        const search = document.getElementById('bookingSearch')?.value?.toLowerCase() || '';
        const status = document.getElementById('bookingStatusFilter')?.value || '';

        let filtered = this.bookings.filter(b => {
            const matchSearch = b.booking_id.toLowerCase().includes(search) ||
                              b.user_id.toLowerCase().includes(search) ||
                              b.flight_id.toLowerCase().includes(search);
            const matchStatus = !status || b.status === status;
            return matchSearch && matchStatus;
        });

        this.renderBookings(filtered);
    }

    // ============ Users Management ============

    async loadUsers() {
        try {
            const data = await this.fetchData('/api/v1/admin/users');
            this.users = data.users || [];
            this.renderUsers();
        } catch (error) {
            console.error('Помилка завантаження користувачів:', error);
        }
    }

    renderUsers(users = null) {
        const container = document.getElementById('usersList');
        if (!container) return;

        const list = users || this.users;
        
        if (list.length === 0) {
            container.innerHTML = '<p class="empty">👤 Немає користувачів</p>';
            return;
        }

        container.innerHTML = list.map(user => `
            <div class="admin-item">
                <div class="info">
                    <div class="title">${user.username}</div>
                    <div class="subtitle">${user.full_name || 'Немає імені'}</div>
                    <div class="details">
                        ${user.email} | ${user.phone || 'Немає телефону'} 
                        ${user.is_active ? '' : ' | ⛔ Неактивний'}
                        ${user.is_verified ? ' | ✅ Підтверджений' : ' | ⏳ Не підтверджений'}
                    </div>
                </div>
                <div class="role-badge ${user.is_admin ? 'admin' : ''}">
                    ${user.is_admin ? '👑 Адмін' : '👤 Користувач'}
                </div>
                <div class="actions">
                    <button class="edit-btn" onclick="admin.toggleAdmin('${user.user_id}')">
                        ${user.is_admin ? '⬇️' : '⬆️'}
                    </button>
                    <button class="toggle-btn" onclick="admin.toggleUserActive('${user.user_id}')">
                        ${user.is_active ? '⏸️' : '▶️'}
                    </button>
                </div>
            </div>
        `).join('');
    }

    filterUsers() {
        const search = document.getElementById('userSearch')?.value?.toLowerCase() || '';
        const role = document.getElementById('userRoleFilter')?.value || '';

        let filtered = this.users.filter(u => {
            const matchSearch = u.username.toLowerCase().includes(search) ||
                              u.email.toLowerCase().includes(search) ||
                              (u.full_name && u.full_name.toLowerCase().includes(search));
            const matchRole = !role || (role === 'admin' ? u.is_admin : !u.is_admin);
            return matchSearch && matchRole;
        });

        this.renderUsers(filtered);
    }

    // ============ Admin Actions ============

    showAddFlightModal() {
        document.getElementById('addFlightModal').style.display = 'block';
    }

    closeAddFlightModal() {
        document.getElementById('addFlightModal').style.display = 'none';
    }

    async editFlight(flightId) {
        const flight = this.flights.find(f => f.flight_id === flightId);
        if (!flight) return;

        const modal = document.getElementById('editFlightModal');
        document.getElementById('e_flight_id').value = flight.flight_id;
        document.getElementById('e_airline').value = flight.airline;
        document.getElementById('e_flight_number').value = flight.flight_number;
        document.getElementById('e_origin').value = flight.origin;
        document.getElementById('e_destination').value = flight.destination;
        document.getElementById('e_departure').value = flight.departure_time?.slice(0, 16);
        document.getElementById('e_arrival').value = flight.arrival_time?.slice(0, 16);
        document.getElementById('e_price').value = flight.price;
        document.getElementById('e_seats').value = flight.available_seats;
        document.getElementById('e_status').value = flight.status;
        
        modal.style.display = 'block';
    }

    closeEditFlightModal() {
        document.getElementById('editFlightModal').style.display = 'none';
    }

    async deleteFlight(flightId) {
        if (!confirm('Ви впевнені, що хочете видалити цей рейс?')) return;

        try {
            const response = await fetch(`/api/v1/admin/flights/${flightId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.user_id}`
                }
            });

            if (response.ok) {
                this.showMessage('✅ Рейс видалено', 'success');
                this.loadFlights();
                this.loadDashboard();
            } else {
                const data = await response.json();
                this.showMessage(`❌ ${data.error || 'Помилка видалення'}`, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Помилка при видаленні', 'error');
        }
    }

    async toggleFlight(flightId) {
        try {
            const response = await fetch(`/api/v1/admin/flights/${flightId}/toggle`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.user_id}`
                }
            });

            if (response.ok) {
                this.showMessage('✅ Статус рейсу змінено', 'success');
                this.loadFlights();
                this.loadDashboard();
            } else {
                const data = await response.json();
                this.showMessage(`❌ ${data.error || 'Помилка'}`, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Помилка при зміні статусу', 'error');
        }
    }

    async confirmBooking(bookingId) {
        try {
            const response = await fetch(`/api/v1/admin/bookings/${bookingId}/confirm`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.user_id}`
                }
            });

            if (response.ok) {
                this.showMessage('✅ Бронювання підтверджено', 'success');
                this.loadBookings();
                this.loadDashboard();
            } else {
                const data = await response.json();
                this.showMessage(`❌ ${data.error || 'Помилка'}`, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Помилка при підтвердженні', 'error');
        }
    }

    async completeBooking(bookingId) {
        try {
            const response = await fetch(`/api/v1/admin/bookings/${bookingId}/complete`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.user_id}`
                }
            });

            if (response.ok) {
                this.showMessage('✅ Бронювання завершено', 'success');
                this.loadBookings();
                this.loadDashboard();
            } else {
                const data = await response.json();
                this.showMessage(`❌ ${data.error || 'Помилка'}`, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Помилка при завершенні', 'error');
        }
    }

    async cancelBooking(bookingId) {
        const reason = prompt('Введіть причину скасування:');
        if (reason === null) return;

        try {
            const response = await fetch(`/api/v1/admin/bookings/${bookingId}/cancel`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.user_id}`
                },
                body: JSON.stringify({ reason })
            });

            if (response.ok) {
                this.showMessage('✅ Бронювання скасовано', 'success');
                this.loadBookings();
                this.loadDashboard();
            } else {
                const data = await response.json();
                this.showMessage(`❌ ${data.error || 'Помилка'}`, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Помилка при скасуванні', 'error');
        }
    }

    async toggleAdmin(userId) {
        const user = this.users.find(u => u.user_id === userId);
        if (!user) return;

        try {
            const response = await fetch(`/api/v1/admin/users/${userId}/admin`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.user_id}`
                },
                body: JSON.stringify({ is_admin: !user.is_admin })
            });

            if (response.ok) {
                this.showMessage(`✅ Права ${!user.is_admin ? 'надано' : 'знято'}`, 'success');
                this.loadUsers();
            } else {
                const data = await response.json();
                this.showMessage(`❌ ${data.error || 'Помилка'}`, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Помилка при зміні прав', 'error');
        }
    }

    async toggleUserActive(userId) {
        const user = this.users.find(u => u.user_id === userId);
        if (!user) return;

        try {
            const response = await fetch(`/api/v1/admin/users/${userId}/active`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentUser.user_id}`
                },
                body: JSON.stringify({ is_active: !user.is_active })
            });

            if (response.ok) {
                this.showMessage(`✅ Користувача ${!user.is_active ? 'активовано' : 'деактивовано'}`, 'success');
                this.loadUsers();
            } else {
                const data = await response.json();
                this.showMessage(`❌ ${data.error || 'Помилка'}`, 'error');
            }
        } catch (error) {
            this.showMessage('❌ Помилка при зміні статусу', 'error');
        }
    }

    // ============ Forms ============

    setupForms() {
        // Додавання рейсу
        document.getElementById('addFlightForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const data = {
                airline: document.getElementById('f_airline').value,
                flight_number: document.getElementById('f_flight_number').value,
                origin: document.getElementById('f_origin').value,
                destination: document.getElementById('f_destination').value,
                departure_time: document.getElementById('f_departure').value,
                arrival_time: document.getElementById('f_arrival').value,
                price: parseFloat(document.getElementById('f_price').value),
                available_seats: parseInt(document.getElementById('f_seats').value),
                aircraft: document.getElementById('f_aircraft').value,
                terminal: document.getElementById('f_terminal').value,
                gate: document.getElementById('f_gate').value
            };

            try {
                const response = await fetch('/api/v1/admin/flights', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.currentUser.user_id}`
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    this.showMessage('✅ Рейс додано успішно!', 'success');
                    this.closeAddFlightModal();
                    this.loadFlights();
                    this.loadDashboard();
                    document.getElementById('addFlightForm').reset();
                } else {
                    const error = await response.json();
                    this.showMessage(`❌ ${error.error || 'Помилка додавання'}`, 'error');
                }
            } catch (error) {
                this.showMessage('❌ Помилка при додаванні рейсу', 'error');
            }
        });

        // Редагування рейсу
        document.getElementById('editFlightForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const flightId = document.getElementById('e_flight_id').value;
            const data = {
                airline: document.getElementById('e_airline').value,
                flight_number: document.getElementById('e_flight_number').value,
                origin: document.getElementById('e_origin').value,
                destination: document.getElementById('e_destination').value,
                departure_time: document.getElementById('e_departure').value,
                arrival_time: document.getElementById('e_arrival').value,
                price: parseFloat(document.getElementById('e_price').value),
                available_seats: parseInt(document.getElementById('e_seats').value),
                status: document.getElementById('e_status').value
            };

            try {
                const response = await fetch(`/api/v1/admin/flights/${flightId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.currentUser.user_id}`
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    this.showMessage('✅ Рейс оновлено!', 'success');
                    this.closeEditFlightModal();
                    this.loadFlights();
                    this.loadDashboard();
                } else {
                    const error = await response.json();
                    this.showMessage(`❌ ${error.error || 'Помилка оновлення'}`, 'error');
                }
            } catch (error) {
                this.showMessage('❌ Помилка при оновленні рейсу', 'error');
            }
        });
    }

    setupFilters() {
        // Фільтри для рейсів
        document.getElementById('flightSearch')?.addEventListener('input', () => this.filterFlights());
        document.getElementById('flightStatusFilter')?.addEventListener('change', () => this.filterFlights());
        
        // Фільтри для бронювань
        document.getElementById('bookingSearch')?.addEventListener('input', () => this.filterBookings());
        document.getElementById('bookingStatusFilter')?.addEventListener('change', () => this.filterBookings());
        
        // Фільтри для користувачів
        document.getElementById('userSearch')?.addEventListener('input', () => this.filterUsers());
        document.getElementById('userRoleFilter')?.addEventListener('change', () => this.filterUsers());
    }

    // ============ Helpers ============

    async fetchData(url) {
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${this.currentUser?.user_id || ''}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    }

    getStatusText(status) {
        const statuses = {
            'scheduled': 'Заплановано',
            'delayed': 'Затримано',
            'cancelled': 'Скасовано',
            'completed': 'Завершено'
        };
        return statuses[status] || status;
    }

    getBookingStatusText(status) {
        const statuses = {
            'pending': 'Очікує',
            'confirmed': 'Підтверджено',
            'cancelled': 'Скасовано',
            'completed': 'Завершено'
        };
        return statuses[status] || status;
    }

    showMessage(text, type = 'info') {
        const existing = document.querySelector('.message-popup');
        if (existing) existing.remove();

        const popup = document.createElement('div');
        popup.className = `message-popup ${type}`;
        popup.textContent = text;
        document.body.appendChild(popup);

        setTimeout(() => {
            popup.style.opacity = '0';
            setTimeout(() => popup.remove(), 300);
        }, 4000);
    }
}

// Ініціалізація
const admin = new AdminPanel();

// Глобальні функції для HTML
window.admin = admin;
window.showAddFlightModal = () => admin.showAddFlightModal();
window.closeAddFlightModal = () => admin.closeAddFlightModal();
window.closeEditFlightModal = () => admin.closeEditFlightModal();
window.filterFlights = () => admin.filterFlights();
window.filterBookings = () => admin.filterBookings();
window.filterUsers = () => admin.filterUsers();
