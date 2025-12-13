
document.addEventListener("DOMContentLoaded", () => {
    const navProfile = document.getElementById('nav-profile');
    if (navProfile) {
        navProfile.addEventListener('click', openProfile);
    }

    const reportForm = document.getElementById('report-form');
    if (reportForm) {
        reportForm.addEventListener('submit', downloadFilteredReport);
    }
});

async function openProfile() {
    showView('view-profile');
    
    const userStr = localStorage.getItem('currentUser');
    if (!userStr) return;
    const user = JSON.parse(userStr);

    document.getElementById('profile-username').innerText = user.username;
    document.getElementById('profile-email').innerText = user.email;
    
    const adminPanel = document.getElementById('admin-controls');
    const roleText = document.getElementById('profile-role');
    
    if (user.is_superuser || user.is_staff || user.is_admin_user) {
        adminPanel.classList.remove('d-none');
        roleText.innerText = "Administrator";
        roleText.className = "text-danger fw-bold";
    } else {
        adminPanel.classList.add('d-none');
        roleText.innerText = "Client";
        roleText.className = "text-muted";
    }

    loadBookings();
}

async function loadBookings() {
    const container = document.getElementById('bookings-list');
    container.innerHTML = '<div class="text-center p-3">Оновлення...</div>';

    const userStr = localStorage.getItem('currentUser');
    if (!userStr) return;
    const user = JSON.parse(userStr);

    const bookings = await apiRequest(`/bookings/?user_id=${user.id}`);

    if (!bookings || bookings.length === 0) {
        container.innerHTML = '<div class="text-center p-3 text-muted">У вас ще немає бронювань.</div>';
        return;
    }

    container.innerHTML = '';
    
    bookings.forEach(booking => {
        const firstTicket = booking.tickets[0];
        
        let sessionInfo = "Деталі недоступні (квитки видалено)";
        let seatsInfo = "";

        if (firstTicket) {
            const sessionDate = new Date(firstTicket.start_time).toLocaleString('uk-UA', {
                day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit'
            });
            
            sessionInfo = `
                <h5 class="mb-1 text-primary">${firstTicket.movie_title}</h5>
                <div class="text-muted small">
                    📅 ${sessionDate} <br>
                    📍 ${firstTicket.hall_name}
                </div>
            `;

            seatsInfo = booking.tickets.map(t => {
                const type = t.is_vip ? '<span class="badge bg-warning text-dark" style="font-size:0.7em">VIP</span>' : '';
                return `<span class="badge bg-secondary">Місце ${t.seat_number} ${type}</span>`;
            }).join(' ');
        }

        const item = document.createElement('div');
        item.className = 'list-group-item';
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <small class="text-muted">Бронювання #${booking.id}</small>
                    ${sessionInfo}
                    <div class="mt-2">
                        ${seatsInfo}
                    </div>
                </div>
                <div class="text-end">
                    <div class="fw-bold text-success mb-2">${booking.total_price} грн</div>
                    <button class="btn btn-sm btn-outline-danger" onclick="cancelBooking(${booking.id})">
                        Скасувати
                    </button>
                </div>
            </div>
        `;
        container.appendChild(item);
    });
}

async function cancelBooking(id) {
    if (!confirm("Ви впевнені, що хочете скасувати це бронювання?")) return;

    const userStr = localStorage.getItem('currentUser');
    if (!userStr) return;
    const user = JSON.parse(userStr);

    const body = {
        user_id: user.id
    };

    const response = await apiRequest(`/bookings/${id}/cancel/`, 'POST', body);
    
    if (response) {
        alert("Бронювання скасовано!");
        loadBookings();
    }
}

function downloadFilteredReport(e) {
    e.preventDefault();
    const start = document.getElementById('report-start').value;
    const end = document.getElementById('report-end').value;

    let url = "http://127.0.0.1:8000/api/reports/download/";
    
    if (start && end) {
        url += `?start_date=${start}&end_date=${end}`;
    }

    window.open(url, '_blank');
}