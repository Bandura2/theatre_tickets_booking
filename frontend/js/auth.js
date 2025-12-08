// frontend/js/auth.js

document.addEventListener("DOMContentLoaded", () => {
    checkAuth();

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const logoutBtn = document.getElementById('nav-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    
    // Отримуємо список користувачів, щоб знайти потрібного
    // (У реальному проекті тут був би POST запит на /api/token/)
    const users = await apiRequest('/users/');
    
    if (users) {
        const foundUser = users.find(u => u.username === username);
        
        if (foundUser) {
            // Зберігаємо юзера в пам'ять браузера
            localStorage.setItem('currentUser', JSON.stringify(foundUser));
            alert(`Вітаємо, ${foundUser.username}!`);
            checkAuth();
            showView('view-movies'); // Перекидаємо на афішу
        } else {
            alert('Користувача не знайдено! Спробуйте "admin" або зареєструйтесь.');
        }
    }
}

function handleLogout() {
    localStorage.removeItem('currentUser');
    checkAuth();
    showView('view-login');
}

function checkAuth() {
    const userStr = localStorage.getItem('currentUser');
    const navLogin = document.getElementById('nav-login');
    const navRegister = document.getElementById('nav-register');
    const navLogout = document.getElementById('nav-logout');
    const userDisplay = document.getElementById('user-display');

    if (userStr) {
        // Користувач залогінений
        currentUser = JSON.parse(userStr);
        if(navLogin) navLogin.classList.add('d-none');
        if(navRegister) navRegister.classList.add('d-none');
        if(navLogout) navLogout.classList.remove('d-none');
        if(userDisplay) userDisplay.innerText = `👤 ${currentUser.username}`;
    } else {
        // Гість
        currentUser = null;
        if(navLogin) navLogin.classList.remove('d-none');
        if(navRegister) navRegister.classList.remove('d-none');
        if(navLogout) navLogout.classList.add('d-none');
        if(userDisplay) userDisplay.innerText = '';
    }
}