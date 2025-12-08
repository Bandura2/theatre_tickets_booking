// frontend/js/hall.js

let selectedSeats = [];

document.addEventListener("DOMContentLoaded", () => {
    // Прив'язуємо подію кліку до кнопки
    const bookBtn = document.getElementById('btn-book');
    if (bookBtn) {
        bookBtn.addEventListener('click', bookTickets);
    }
});

function clearHall() {
    document.getElementById('hall-container').innerHTML = '';
    selectedSeats = [];
    updateTotalPrice();
}

function renderComponent(component, container) {
    if (component.type === 'group') {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'seat-group';
        groupDiv.innerHTML = `<div class="small text-muted mb-1">${component.name}</div>`;
        if (component.children && component.children.length > 0) {
            component.children.forEach(child => renderComponent(child, groupDiv));
        }
        container.appendChild(groupDiv);
    } else if (component.type === 'seat') {
        const seatBtn = document.createElement('button');
        const isVip = component.seat_details.is_vip;
        
        seatBtn.className = `seat ${isVip ? 'vip' : 'standard'}`;
        seatBtn.textContent = component.seat_details.number;
        
        // Передаємо ID самого місця (Seat ID), а не компонента
        seatBtn.onclick = () => toggleSeat(component.seat_details.id, seatBtn);
        
        container.appendChild(seatBtn);
    }
}

function toggleSeat(seatId, element) {
    if (selectedSeats.includes(seatId)) {
        selectedSeats = selectedSeats.filter(s => s !== seatId);
        element.classList.remove('selected');
    } else {
        selectedSeats.push(seatId);
        element.classList.add('selected');
    }
    updateTotalPrice();
}

function updateTotalPrice() {
    const btn = document.getElementById('btn-book');
    const priceSpan = document.getElementById('total-price');
    // Приблизна ціна для візуалізації
    priceSpan.innerText = selectedSeats.length * 150; 
    btn.disabled = selectedSeats.length === 0;
}

// === ФУНКЦІЯ БРОНЮВАННЯ ===
async function bookTickets() {
    const userStr = localStorage.getItem('currentUser');
    if (!userStr) {
        alert("Будь ласка, увійдіть у систему!");
        showView('view-login');
        return;
    }
    const user = JSON.parse(userStr);

    if (!window.currentSessionId) {
        alert("Помилка: Сеанс не обрано.");
        return;
    }

    const body = {
        user_id: user.id,
        session_id: window.currentSessionId, // Беремо з глобальної змінної
        seat_ids: selectedSeats
    };

    const btn = document.getElementById('btn-book');
    btn.disabled = true;
    btn.innerText = "Обробка...";

    const response = await apiRequest('/bookings/create_online/', 'POST', body);

    if (response) {
        alert(`Успішно! Номер бронювання: #${response.id}\nСума: ${response.total_price} грн`);
        showView('view-movies'); // Повертаємось на головну
    }
    
    btn.disabled = false;
    btn.innerText = "Забронювати";
}