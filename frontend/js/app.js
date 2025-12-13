// frontend/js/app.js

// Змінні стану
let currentUser = null;

document.addEventListener("DOMContentLoaded", () => {
    // === ЗМІНА 1: За замовчуванням показуємо Афішу, а не Логін ===
    showView('view-movies'); 

    // Кнопка "Назад" на екрані залу
    const backBtn = document.getElementById('back-to-movies');
    if (backBtn) backBtn.onclick = () => showView('view-movies');

    // Клік по логотипу
    const logo = document.getElementById('nav-logo');
    if (logo) {
        logo.addEventListener('click', (e) => {
            e.preventDefault();
            // === ЗМІНА 2: Логотип завжди веде на афішу, навіть для гостей ===
            showView('view-movies');
        });
    }
});

// Простий роутер для перемикання div-ів
function showView(viewId) {
    // Ховаємо всі секції
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('d-none'));
    
    // Показуємо потрібну
    const view = document.getElementById(viewId);
    if (view) view.classList.remove('d-none');

    // Якщо відкрили афішу - завантажуємо фільми
    if (viewId === 'view-movies') {
        loadMovies();
    }
}

async function loadMovies() {
    const sessions = await apiRequest('/sessions/');
    const container = document.getElementById('movies-container');
    
    if (!container) return;
    container.innerHTML = '';

    if (!sessions || sessions.length === 0) {
        container.innerHTML = '<div class="text-center w-100">Немає доступних сеансів</div>';
        return;
    }

    sessions.forEach(session => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4';
        
        const posterUrl = session.movie_poster 
            ? session.movie_poster 
            : 'https://via.placeholder.com/300x450?text=No+Poster';

        col.innerHTML = `
            <div class="card h-100 shadow-sm border-0">
                <div style="position: relative; height: 350px; overflow: hidden; border-radius: 5px 5px 0 0; background-color: #f8f9fa;">
                    
                    <img src="${posterUrl}" 
                         alt="" 
                         style="position: absolute; width: 100%; height: 100%; object-fit: cover; filter: blur(15px); opacity: 0.6; transform: scale(1.2);">
                    
                    <img src="${posterUrl}" 
                         alt="${session.movie_title}" 
                         style="position: relative; width: 100%; height: 100%; object-fit: contain; z-index: 1;">
                </div>
                
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title text-primary">${session.movie_title}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">📍 ${session.hall_name}</h6>
                    
                    <div class="mt-auto">
                        <p class="card-text small text-secondary mb-2">
                            📅 ${new Date(session.start_time).toLocaleString('uk-UA', { dateStyle: 'short', timeStyle: 'short' })} <br>
                            💰 від ${session.price_base} грн
                        </p>
                        <button class="btn btn-outline-primary w-100" onclick="openHall(${session.hall}, ${session.id})">
                            Обрати місця
                        </button>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(col);
    });
}

async function openHall(hallId, sessionId) {
    window.currentSessionId = sessionId; 

    // 1. Отримуємо деталі сеансу (щоб знати ЦІНУ)
    const session = await apiRequest(`/sessions/${sessionId}/`);
    // Зберігаємо базову ціну глобально
    window.currentSessionBasePrice = parseFloat(session.price_base); 

    showView('view-hall');
    clearHall();
    
    // 2. Завантажуємо структуру залу
    const hallData = await apiRequest(`/halls/${hallId}/`);
    
    // 3. Завантажуємо зайняті місця
    const tickets = await apiRequest(`/tickets/?session_id=${sessionId}`);
    const occupiedSet = new Set();
    if (tickets) {
        tickets.forEach(t => {
            if (t.status === 'BOOKED' || t.status === 'SOLD') {
                occupiedSet.add(t.seat);
            }
        });
    }

    const container = document.getElementById('hall-container');
    
    if (document.getElementById('session-title')) {
        document.getElementById('session-title').innerText = `Зал: ${hallData.name}`;
    }

    if (hallData.structure) {
        hallData.structure.forEach(rootComponent => {
            renderComponent(rootComponent, container, occupiedSet);
        });
    }
}

