async function getCurrentUser() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    try {
        const res = await fetch(`${API}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) return await res.json();
        return null;
    } catch {
        return null;
    }
}


async function renderNav(activePage) {
    window._activePage = activePage;
    const user = await getCurrentUser();

    let navItems = '';

    if (!user) {
        navItems = `
            <a href="/predict" class="nav-item ${activePage === 'index' ? 'active' : ''}">
                <i class="bi bi-speedometer2"></i> Оценка авто
            </a>
            <a href="/about" class="nav-item ${activePage === 'about' ? 'active' : ''}">
                <i class="bi bi-info-circle"></i> О проекте
            </a>`;
    } else if (user.role === 'admin') {
        navItems = `
            <a href="/admin" class="nav-item ${activePage === 'admin' ? 'active' : ''}">
                <i class="bi bi-people"></i> Пользователи
            </a>
            <a href="/profile" class="nav-item ${activePage === 'profile' ? 'active' : ''}">
                <i class="bi bi-person"></i> Профиль
            </a>`;
    } else {
        navItems = `
            <a href="/predict" class="nav-item ${activePage === 'index' ? 'active' : ''}">
                <i class="bi bi-speedometer2"></i> Оценка авто
            </a>
            <a href="/history" class="nav-item ${activePage === 'history' ? 'active' : ''}">
                <i class="bi bi-clock-history"></i> История оценок
            </a>
            <a href="/profile" class="nav-item ${activePage === 'profile' ? 'active' : ''}">
                <i class="bi bi-person"></i> Профиль
            </a>
            <a href="/about" class="nav-item ${activePage === 'about' ? 'active' : ''}">
                <i class="bi bi-info-circle"></i> О проекте
            </a>`;
    }

    // Кнопка внизу
    const footerBtn = user
        ? `<button class="nav-item" onclick="logout()">
                <i class="bi bi-box-arrow-right"></i> Выйти
           </button>`
        : `<button class="nav-item" onclick="openAuthModal()">
                <i class="bi bi-box-arrow-in-right"></i> Войти
           </button>`;

    document.getElementById('nav-section').innerHTML = `
        <div class="nav-label">Навигация</div>
        ${navItems}`;
    document.getElementById('auth-btn-container').innerHTML = footerBtn;
}


function openAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) {
        document.getElementById('login-password').value = '';
        document.getElementById('login-error').textContent = '';

        document.getElementById('reg-email').value = '';
        document.getElementById('reg-password').value = '';
        document.getElementById('reg-password2').value = '';
        document.getElementById('register-error').textContent = '';

        bootstrap.Modal.getOrCreateInstance(modal).show();
    }
}

async function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}