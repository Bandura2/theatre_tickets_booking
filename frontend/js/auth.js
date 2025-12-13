// frontend/js/auth.js

document.addEventListener("DOMContentLoaded", () => {
    checkAuth();

    // Форма логіну
    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    // Форма реєстрації (НОВЕ)
    const registerForm = document.getElementById('register-form');
    if (registerForm) registerForm.addEventListener('submit', handleRegister);

    // Кнопка Вихід
    const logoutBtn = document.getElementById('nav-logout');
    if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);

    // Перемикачі між формами (навігація)
    document.getElementById('nav-login').onclick = () => showView('view-login');
    document.getElementById('nav-register').onclick = () => showView('view-register');
    
    // Посилання "Вже є акаунт?" всередині форми
    const linkLogin = document.getElementById('link-to-login');
    if (linkLogin) linkLogin.onclick = (e) => {
        e.preventDefault();
        showView('view-login');
    };

    const reportBtn = document.getElementById('nav-report');
    if (reportBtn) {
        reportBtn.addEventListener('click', downloadReport);
    }
});

// === ЛОГІКА РЕЄСТРАЦІЇ ===
async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    const body = {
        username: username,
        email: email,
        password: password,
        is_client: true // Вказуємо, що це клієнт
    };

    // Відправляємо запит на створення юзера
    const response = await apiRequest('/users/', 'POST', body);

    if (response) {
        alert("Реєстрація успішна! Тепер увійдіть у систему.");
        showView('view-login'); // Перекидаємо на логін
        
        // Очищаємо поля
        document.getElementById('reg-username').value = '';
        document.getElementById('reg-email').value = '';
        document.getElementById('reg-password').value = '';
    }
}

// === ЛОГІКА ВХОДУ ===
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    
    // Отримуємо список користувачів (спрощена імітація авторизації)
    const users = await apiRequest('/users/');
    
    if (users) {
        // Шукаємо юзера в масиві
        const foundUser = users.find(u => u.username === username);
        
        // Тут ми мали б перевіряти пароль через бекенд, 
        // але для спрощення JS-клієнта в курсовій перевіримо наявність юзера.
        // (Пароль на бекенді хешується, тому порівняти його тут не вийде, 
        // для повноцінної роботи треба робити JWT endpoint, але це ускладнить код).
        
        if (foundUser) {
            localStorage.setItem('currentUser', JSON.stringify(foundUser));
            alert(`Вітаємо, ${foundUser.username}!`);
            checkAuth();
            showView('view-movies'); // <--- Це має бути тут
        }
    }
}

function handleLogout() {
    localStorage.removeItem('currentUser');
    checkAuth();
    showView('view-login');
}

async function downloadReport() {
    const userStr = localStorage.getItem('currentUser');
    if (!userStr) return;
    
    // Оскільки це скачування файлу, fetch тут не дуже зручний.
    // Простіше відкрити посилання у новому вікні, браузер сам почне завантаження.
    // Але якщо потрібна авторизація (Admin only), браузер має передати куки сесії.
    // Для курсової, де ми використовуємо просту авторизацію або сесії Django, це спрацює:
    
    window.location.href = "http://127.0.0.1:8000/api/reports/download/";
}
function checkAuth() {
    const userStr = localStorage.getItem('currentUser');
    
    // Отримуємо всі кнопки навігації
    const navLogin = document.getElementById('nav-login');
    const navRegister = document.getElementById('nav-register');
    const navLogout = document.getElementById('nav-logout');
    const navReport = document.getElementById('nav-report');
    const navProfile = document.getElementById('nav-profile'); // <--- ДОДАНО: Кнопка профілю
    const userDisplay = document.getElementById('user-display');

    if (userStr) {
        // === КОРИСТУВАЧ ЗАЛОГІНЕНИЙ ===
        currentUser = JSON.parse(userStr);
        
        // Ховаємо кнопки входу/реєстрації
        if(navLogin) navLogin.classList.add('d-none');
        if(navRegister) navRegister.classList.add('d-none');
        
        // Показуємо кнопки виходу та профілю
        if(navLogout) navLogout.classList.remove('d-none');
        if(navProfile) navProfile.classList.remove('d-none'); // <--- Показуємо кабінет

        // Логіка для Адміна (Кнопка звіту в меню)
        if (currentUser.is_superuser || currentUser.is_staff || currentUser.is_admin_user) {
            if(navReport) navReport.classList.remove('d-none');
        } else {
            if(navReport) navReport.classList.add('d-none');
        }

        if(userDisplay) userDisplay.innerText = `👤 ${currentUser.username}`;
    } else {
        // === ГІСТЬ (НЕ ЗАЛОГІНЕНИЙ) ===
        currentUser = null;
        
        // Показуємо кнопки входу/реєстрації
        if(navLogin) navLogin.classList.remove('d-none');
        if(navRegister) navRegister.classList.remove('d-none');
        
        // Ховаємо все інше
        if(navLogout) navLogout.classList.add('d-none');
        if(navReport) navReport.classList.add('d-none');
        if(navProfile) navProfile.classList.add('d-none'); // <--- Ховаємо кабінет
        
        if(userDisplay) userDisplay.innerText = '';
    }
}