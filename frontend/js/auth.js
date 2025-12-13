document.addEventListener("DOMContentLoaded", () => {
    checkAuth();

    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const registerForm = document.getElementById('register-form');
    if (registerForm) registerForm.addEventListener('submit', handleRegister);

    const logoutBtn = document.getElementById('nav-logout');
    if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);

    document.getElementById('nav-login').onclick = () => showView('view-login');
    document.getElementById('nav-register').onclick = () => showView('view-register');
    
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

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    const body = {
        username: username,
        email: email,
        password: password,
        is_client: true 
    };

    const response = await apiRequest('/users/', 'POST', body);

    if (response) {
        alert("Реєстрація успішна! Тепер увійдіть у систему.");
        showView('view-login');
        
        document.getElementById('reg-username').value = '';
        document.getElementById('reg-email').value = '';
        document.getElementById('reg-password').value = '';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    
    const users = await apiRequest('/users/');
    
    if (users) {
        const foundUser = users.find(u => u.username === username);
        
        if (foundUser) {
            localStorage.setItem('currentUser', JSON.stringify(foundUser));
            alert(`Вітаємо, ${foundUser.username}!`);
            checkAuth();
            showView('view-movies');
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
    window.location.href = "http://127.0.0.1:8000/api/reports/download/";
}

function checkAuth() {
    const userStr = localStorage.getItem('currentUser');
    
    const navLogin = document.getElementById('nav-login');
    const navRegister = document.getElementById('nav-register');
    const navLogout = document.getElementById('nav-logout');
    const navReport = document.getElementById('nav-report');
    const navProfile = document.getElementById('nav-profile'); 
    const userDisplay = document.getElementById('user-display');

    if (userStr) {
        currentUser = JSON.parse(userStr);
        
        if(navLogin) navLogin.classList.add('d-none');
        if(navRegister) navRegister.classList.add('d-none');
        if(navLogout) navLogout.classList.remove('d-none');
        if(navProfile) navProfile.classList.remove('d-none');

        if (currentUser.is_superuser || currentUser.is_staff || currentUser.is_admin_user) {
            if(navReport) navReport.classList.remove('d-none');
        } else {
            if(navReport) navReport.classList.add('d-none');
        }

        if(userDisplay) userDisplay.innerText = `👤 ${currentUser.username}`;
    } else {
        currentUser = null;
        
        if(navLogin) navLogin.classList.remove('d-none');
        if(navRegister) navRegister.classList.remove('d-none');
        if(navLogout) navLogout.classList.add('d-none');
        if(navReport) navReport.classList.add('d-none');
        if(navProfile) navProfile.classList.add('d-none');
        if(userDisplay) userDisplay.innerText = '';
    }
}