let selectedSeats = [];
let seatInfo = {}; 

document.addEventListener("DOMContentLoaded", () => {
    const bookBtn = document.getElementById('btn-book');
    const discountSelect = document.getElementById('discount-select');

    if (bookBtn) bookBtn.addEventListener('click', bookTickets);
    
    // Слухаємо зміну знижки
    if (discountSelect) {
        discountSelect.addEventListener('change', handleDiscountChange);
    }
});

function handleDiscountChange() {
    const type = document.getElementById('discount-select').value;
    const studentGroup = document.getElementById('student-input-group');
    const promoGroup = document.getElementById('promo-input-group');

    // Скидаємо видимість
    studentGroup.classList.add('d-none');
    promoGroup.classList.add('d-none');

    // Показуємо потрібне поле
    if (type === 'STUDENT') {
        studentGroup.classList.remove('d-none');
    } else if (type === 'PROMO') {
        promoGroup.classList.remove('d-none');
    }

    updateTotalPrice();
}

function clearHall() {
    document.getElementById('hall-container').innerHTML = '';
    selectedSeats = [];
    seatInfo = {};
    
    // Скидаємо форми
    const discountSelect = document.getElementById('discount-select');
    if(discountSelect) {
        discountSelect.value = "NO";
        handleDiscountChange(); // Сховає поля вводу
    }
    document.getElementById('student-id-input').value = '';
    document.getElementById('promo-code-input').value = '';

    updateTotalPrice();
}

function renderComponent(component, container, occupiedSet = new Set()) {
    if (component.type === 'group') {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'seat-group';
        groupDiv.innerHTML = `<div class="small text-muted mb-1">${component.name}</div>`;
        if (component.children) {
            component.children.forEach(child => renderComponent(child, groupDiv, occupiedSet));
        }
        container.appendChild(groupDiv);
    } 
    else if (component.type === 'seat') {
        const seatBtn = document.createElement('button');
        const seatId = component.seat_details.id;
        const seatNum = component.seat_details.number;
        const type = component.seat_details.seat_type; 

        seatInfo[seatId] = { type: type };
        
        if (occupiedSet.has(seatId)) {
            seatBtn.className = 'seat occupied';
            seatBtn.disabled = true;
            seatBtn.textContent = seatNum;
        } else {
            let cssClass = 'standard';
            if (type === 'VIP') cssClass = 'vip';
            if (type === 'BLC') cssClass = 'balcony';
            
            seatBtn.className = `seat ${cssClass}`;
            seatBtn.textContent = seatNum;
            
            // Ціну в title не пишемо жорстко, бо вона залежить від знижки
            seatBtn.title = `Місце ${seatNum} (${type})`;
            seatBtn.onclick = () => toggleSeat(seatId, seatBtn);
        }
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
    const discountSelect = document.getElementById('discount-select');
    
    let total = 0;
    const basePrice = window.currentSessionBasePrice || 0;

    // Frontend розраховує ціну "оптимістично" (припускаючи, що промокод введуть правильно)
    let discountMultiplier = 1.0;
    if (discountSelect.value === 'STUDENT') discountMultiplier = 0.8;
    if (discountSelect.value === 'PROMO') discountMultiplier = 0.9;

    selectedSeats.forEach(id => {
        const info = seatInfo[id];
        if (info) {
            let seatMultiplier = 1.0;
            if (info.type === 'VIP') seatMultiplier = 1.5;
            if (info.type === 'BLC') seatMultiplier = 0.9;

            total += (basePrice * seatMultiplier) * discountMultiplier;
        }
    });

    priceSpan.innerText = total.toFixed(2);
    btn.disabled = selectedSeats.length === 0;
}

async function bookTickets() {
    const userStr = localStorage.getItem('currentUser');
    if (!userStr) {
        if(confirm("Увійдіть для бронювання.")) showView('view-login');
        return;
    }
    const user = JSON.parse(userStr);

    if (!window.currentSessionId) {
        alert("Помилка: Сеанс не обрано.");
        return;
    }
    
    const discountType = document.getElementById('discount-select').value;
    const studentId = document.getElementById('student-id-input').value;
    const promoCode = document.getElementById('promo-code-input').value;

    const body = {
        user_id: user.id,
        session_id: window.currentSessionId,
        seat_ids: selectedSeats,
        discount_type: discountType,
        // Передаємо нові поля
        student_id: studentId,
        promo_code: promoCode
    };

    const btn = document.getElementById('btn-book');
    btn.disabled = true;
    btn.innerText = "Обробка...";

    // Відправляємо запит. Якщо промокод невірний, бекенд поверне 400 і apiRequest викине alert з помилкою
    const response = await apiRequest('/bookings/create_online/', 'POST', body);

    if (response) {
        alert(`Успішно! Бронювання #${response.id}\nСума: ${response.total_price} грн`);
        showView('view-movies'); 
    }
    
    btn.disabled = false;
    btn.innerText = "Забронювати";
}