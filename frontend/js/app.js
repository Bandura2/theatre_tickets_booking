let currentUser = null;
let allSessionsData = [];

document.addEventListener("DOMContentLoaded", () => {
    showView('view-movies');

    const backBtn = document.getElementById('back-to-movies');
    if (backBtn) backBtn.onclick = () => showView('view-movies');

    const logo = document.getElementById('nav-logo');
    if (logo) {
        logo.addEventListener('click', (e) => {
            e.preventDefault();
            showView('view-movies');
        });
    }

    const titleInput = document.getElementById('filter-title');
    const genreSelect = document.getElementById('filter-genre');

    const dateStartInput = document.getElementById('filter-date-start');
    const dateEndInput = document.getElementById('filter-date-end');

    if (titleInput) titleInput.addEventListener('input', filterSessions);
    if (genreSelect) genreSelect.addEventListener('change', filterSessions);
    if (dateStartInput) dateStartInput.addEventListener('change', filterSessions);
    if (dateEndInput) dateEndInput.addEventListener('change', filterSessions);
});

function showView(viewId) {
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('d-none'));
    const view = document.getElementById(viewId);
    if (view) view.classList.remove('d-none');

    if (viewId === 'view-movies') {
        loadMovies();
    }
}

async function loadMovies() {
    const sessions = await apiRequest('/sessions/');

    if (!sessions || sessions.length === 0) {
        document.getElementById('movies-container').innerHTML = '<div class="text-center w-100">Немає доступних сеансів</div>';
        return;
    }

    allSessionsData = sessions;
    allSessionsData.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

    populateGenres(allSessionsData);
    renderMovies(allSessionsData);
}

function populateGenres(sessions) {
    const genreSelect = document.getElementById('filter-genre');
    if (!genreSelect) return;

    const genres = new Set();
    sessions.forEach(s => { if (s.genre) genres.add(s.genre); });

    genreSelect.innerHTML = '<option value="">Всі жанри</option>';
    genres.forEach(g => {
        const option = document.createElement('option');
        option.value = g;
        option.textContent = g;
        genreSelect.appendChild(option);
    });
}

function filterSessions() {
    const titleQuery = document.getElementById('filter-title').value.toLowerCase();
    const genreQuery = document.getElementById('filter-genre').value;

    const dateStart = document.getElementById('filter-date-start').value;
    const dateEnd = document.getElementById('filter-date-end').value;

    const filtered = allSessionsData.filter(session => {
        const matchTitle = session.movie_title.toLowerCase().includes(titleQuery);

        const matchGenre = genreQuery === "" || session.genre === genreQuery;

        const sessionDate = session.start_time.split('T')[0];

        let matchDate = true;
        if (dateStart && sessionDate < dateStart) matchDate = false;
        if (dateEnd && sessionDate > dateEnd) matchDate = false;

        return matchTitle && matchGenre && matchDate;
    });

    renderMovies(filtered);
}

function resetFilters() {
    document.getElementById('filter-title').value = '';
    document.getElementById('filter-genre').value = '';
    document.getElementById('filter-date-start').value = '';
    document.getElementById('filter-date-end').value = '';

    renderMovies(allSessionsData);
}

function renderMovies(sessions) {
    const container = document.getElementById('movies-container');
    container.innerHTML = '';

    if (sessions.length === 0) {
        container.innerHTML = '<div class="text-center w-100 text-muted mt-5"><h5>На жаль, нічого не знайдено 😢</h5></div>';
        return;
    }

    sessions.forEach(session => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4 fade-in';

        const posterUrl = session.movie_poster
            ? session.movie_poster
            : 'https://via.placeholder.com/300x450?text=No+Poster';

        col.innerHTML = `
            <div class="card h-100 shadow-sm border-0">
                <div style="position: relative; height: 350px; overflow: hidden; border-radius: 5px 5px 0 0; background-color: #f8f9fa;">
                    <img src="${posterUrl}" style="position: absolute; width: 100%; height: 100%; object-fit: cover; filter: blur(15px); opacity: 0.6; transform: scale(1.2);">
                    <img src="${posterUrl}" alt="${session.movie_title}" style="position: relative; width: 100%; height: 100%; object-fit: contain; z-index: 1;">
                </div>
                
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title text-primary">${session.movie_title}</h5>
                    <div class="mb-2">
                        <span class="badge bg-info text-dark">${session.genre || 'Фільм'}</span>
                        <small class="text-muted ms-2">📍 ${session.hall_name}</small>
                    </div>
                    
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

    const session = await apiRequest(`/sessions/${sessionId}/`);
    if (!session) { alert("Помилка"); return; }

    const basePrice = parseFloat(session.price_base);
    window.currentSessionBasePrice = basePrice;

    showView('view-hall');

    const viewHall = document.getElementById('view-hall');

    const pStd = Math.round(basePrice);          
    const pVip = Math.round(basePrice * 1.5);    
    const pBlc = Math.round(basePrice * 0.9);

    const dateStr = new Date(session.start_time).toLocaleString('uk-UA', {
        day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit'
    });

    viewHall.innerHTML = `
        <button id="back-to-movies" class="btn btn-outline-secondary mb-3">← Назад до афіші</button>
        
        <div class="row">
            <div class="col-lg-9">
                <div class="mb-3">
                    <h2 class="text-primary fw-bold mb-0">${session.movie_title}</h2>
                    <p class="text-muted">📍 ${session.hall_name} | 📅 ${dateStr}</p>
                </div>
                <div class="card border-0 shadow-sm">
                    <div class="card-body bg-dark rounded text-center p-4">
                        <div class="screen mb-5">ЕКРАН</div>
                        <div id="hall-container" class="hall-wrapper"></div>
                    </div>
                </div>
            </div>

            <div class="col-lg-3 mt-4 mt-lg-0">
                <div class="card shadow-sm sticky-top" style="top: 20px;">
                    <div class="card-header bg-white fw-bold">▼ Інформація</div>
                    <div class="card-body">
                        <div class="legend-item">
                            <div class="legend-color standard"></div>
                            <div>Standard: <b>${pStd} ₴</b></div>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color balcony"></div>
                            <div>Балкон: <b>${pBlc} ₴</b></div>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color vip"></div>
                            <div>VIP: <b>${pVip} ₴</b></div>
                        </div>
                        <hr>
                        <div class="legend-item">
                            <div class="legend-color selected"></div>
                            <div>Ваш вибір</div>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color occupied"></div>
                            <div>Заброньовано (Резерв)</div>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color sold"></div>
                            <div>Продано (Оплачено)</div>
                        </div>
                        
                        <hr>
                        <div class="mb-3">
                            <label class="small text-muted mb-1">Знижка:</label>
                            <select id="discount-select" class="form-select form-select-sm">
                                <option value="NO">Без знижки</option>
                                <option value="STUDENT">🎓 Студент (-20%)</option>
                                <option value="PROMO">🔥 Промо (-10%)</option>
                            </select>
                        </div>
                        <div id="student-input-group" class="mb-2 d-none">
                            <input type="text" id="student-id-input" class="form-control form-control-sm" placeholder="№ Студентського">
                        </div>
                        <div id="promo-input-group" class="mb-2 d-none">
                            <input type="text" id="promo-code-input" class="form-control form-control-sm" placeholder="Промокод">
                        </div>

                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="text-muted">Разом:</span>
                            <span class="h4 mb-0 text-primary fw-bold"><span id="total-price">0</span> ₴</span>
                        </div>

                        <button id="btn-book" class="btn btn-success w-100 py-2" disabled>Забронювати</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.getElementById('back-to-movies').onclick = () => showView('view-movies');
    clearHall();

    const hallData = await apiRequest(`/halls/${hallId}/`);
    const tickets = await apiRequest(`/tickets/?session_id=${sessionId}`);

    const occupiedMap = new Map();
    if (tickets) {
        tickets.forEach(t => {
            if (t.status === 'BOOKED' || t.status === 'SOLD') {
                occupiedMap.set(t.seat, t.status);
            }
        });
    }

    const container = document.getElementById('hall-container');
    if (hallData.structure) {
        hallData.structure.forEach(rootComponent => {
            renderComponent(rootComponent, container, occupiedMap);
        });
    }

    const discountSelect = document.getElementById('discount-select');
    if (discountSelect) discountSelect.addEventListener('change', handleDiscountChange);

    const btnBook = document.getElementById('btn-book');
    if (btnBook) btnBook.addEventListener('click', bookTickets);
}

function renderMovies(sessions) {
    const container = document.getElementById('movies-container');
    container.innerHTML = '';

    if (sessions.length === 0) {
        container.innerHTML = '<div class="text-center w-100 text-muted mt-5"><h5>На жаль, нічого не знайдено 😢</h5></div>';
        return;
    }

    sessions.forEach(session => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4 fade-in';

        const posterUrl = session.movie_poster
            ? session.movie_poster
            : 'https://via.placeholder.com/300x450?text=No+Poster';

        const description = session.description || "Опис відсутній.";
        const genre = session.genre || "Кіно";

        col.innerHTML = `
            <div class="card h-100 shadow-sm border-0">
                
                <div class="poster-container">
                    
                    <img src="${posterUrl}" style="position: absolute; width: 100%; height: 100%; object-fit: cover; filter: blur(15px); opacity: 0.6; transform: scale(1.2);">
                    
                    <img src="${posterUrl}" alt="${session.movie_title}" style="position: relative; width: 100%; height: 100%; object-fit: contain; z-index: 1;">

                    <div class="movie-overlay">
                        <span class="badge bg-warning text-dark mb-2">${genre}</span>
                        <div class="overlay-desc">
                            ${description}
                        </div>
                    </div>

                </div>
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title text-primary text-truncate">${session.movie_title}</h5>
                    
                    <div class="mb-2">
                        <small class="text-muted">📍 ${session.hall_name}</small>
                    </div>
                    
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