// Змінні стану
let currentUser = null;

document.addEventListener("DOMContentLoaded", () => {
    showView('view-login'); // Спочатку показуємо логін

    // Прив'язка кнопок навігації (якщо потрібно)
    document.getElementById('back-to-movies').onclick = () => showView('view-movies');
});

// Простий роутер для перемикання div-ів
function showView(viewId) {
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('d-none'));
    document.getElementById(viewId).classList.remove('d-none');

    if (viewId === 'view-movies') {
        loadMovies();
    }
}

async function loadMovies() {
    // Завантажуємо сеанси (в реальності треба групувати по фільмах)
    const sessions = await apiRequest('/sessions/');
    const container = document.getElementById('movies-container');
    container.innerHTML = '';

    sessions.forEach(session => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        col.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">${session.movie_title}</h5>
                    <p class="card-text">
                        Зал: ${session.hall_name}<br>
                        Час: ${new Date(session.start_time).toLocaleString()}
                    </p>
                    <button class="btn btn-primary" onclick="openHall(${session.hall}, ${session.id})">Обрати місця</button>
                </div>
            </div>
        `;
        container.appendChild(col);
    });
}

async function openHall(hallId, sessionId) {
    // Зберігаємо ID сеансу глобально, щоб hall.js його бачив
    window.currentSessionId = sessionId; 

    showView('view-hall');
    clearHall();
    
    // Завантажуємо структуру залу
    const hallData = await apiRequest(`/halls/${hallId}/`);
    const container = document.getElementById('hall-container');
    
    // Встановлюємо назву залу
    document.getElementById('session-title').innerText = `Зал: ${hallData.name}`;

    if (hallData.structure) {
        hallData.structure.forEach(rootComponent => {
            renderComponent(rootComponent, container);
        });
    }
}