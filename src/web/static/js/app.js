// State management
let appState = {
    currentTab: 'gallery',
    isAuthorized: false,
    taskRunning: false,
    taskType: null
};

// Category icon map for clean UI without emojis
const categoryIcons = {
    dashboard: 'layout-dashboard',
    time: 'clock',
    style: 'sparkles',
    social: 'users'
};

function refreshIcons() {
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initStatusPolling();
    initLogStream();
    loadGallery();
    loadReport();
    refreshIcons();
});

// Tab Navigation
function initNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const tabId = tab.dataset.tab;
            appState.currentTab = tabId;

            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
            const target = document.getElementById(`tab-${tabId}`);
            if (target) target.style.display = 'block';

            if (tabId === 'gallery') loadGallery();
            if (tabId === 'report') loadReport();
            refreshIcons();
        });
    });
}

// Status Polling
async function initStatusPolling() {
    await updateStatus();
    setInterval(updateStatus, 3000);
}

async function updateStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();

        appState.isAuthorized = data.is_authorized;
        appState.taskRunning = data.task_running;
        appState.taskType = data.task_type;

        // Header status badge
        const badge = document.getElementById('auth-badge');
        const dot = document.getElementById('status-dot');
        const text = document.getElementById('status-text');

        if (data.task_running) {
            dot.className = 'status-dot working';
            text.textContent = data.task_type === 'fetch' ? 'Синхронізація...' : 'Аналіз...';
        } else if (data.is_authorized) {
            dot.className = 'status-dot online';
            const u = data.user_info;
            text.textContent = u ? `${u.first_name} (@${u.username || 'user'})` : 'Підключено';
        } else {
            dot.className = 'status-dot offline';
            text.textContent = 'Не авторизовано';
        }

        // Dashboard metric cards
        document.getElementById('stat-chats').textContent = data.total_chats || 0;
        document.getElementById('stat-messages').textContent = (data.total_messages || 0).toLocaleString('uk-UA');
        document.getElementById('stat-infographics').textContent = data.infographics_count || 0;

        if (data.min_date && data.max_date) {
            const y1 = data.min_date.substring(0, 4);
            const y2 = data.max_date.substring(0, 4);
            document.getElementById('stat-period').textContent = `${y1} — ${y2}`;
        } else {
            document.getElementById('stat-period').textContent = '—';
        }

        // Button states
        const btnFetch = document.getElementById('btn-fetch');
        const btnAnalyze = document.getElementById('btn-analyze');
        if (btnFetch) btnFetch.disabled = data.task_running || !data.is_authorized;
        if (btnAnalyze) btnAnalyze.disabled = data.task_running || data.total_messages === 0;

        // Auth container logic
        const authContainer = document.getElementById('auth-actions-container');
        if (authContainer) {
            if (!data.is_authorized && data.auth_status === 'need_2fa') {
                authContainer.innerHTML = `
                    <div style="display:flex; gap:0.5rem; align-items:center;">
                        <input type="password" id="input-2fa" placeholder="Введіть 2FA пароль"
                               style="padding:0.6rem 1rem; border-radius:8px; border:1px solid var(--card-border); background:#1e293b; color:#fff;">
                        <button class="btn btn-primary" onclick="submit2FA()">
                            <i data-lucide="check"></i>
                            <span>Підтвердити</span>
                        </button>
                    </div>
                `;
                refreshIcons();
            } else if (!data.is_authorized) {
                authContainer.innerHTML = `
                    <button class="btn btn-secondary" onclick="startQRLogin()">
                        <i data-lucide="key"></i>
                        <span>Увійти через QR</span>
                    </button>
                `;
                refreshIcons();
            } else {
                authContainer.innerHTML = ``;
            }
        }
    } catch (e) {
        console.error('Status fetch failed:', e);
    }
}

// Log streaming via SSE
function initLogStream() {
    const logsContainer = document.getElementById('logs-terminal');
    const evtSource = new EventSource('/api/logs/stream');

    evtSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.log) {
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                if (data.log.includes('[✔]')) entry.classList.add('success');
                else if (data.log.includes('[❌]') || data.log.includes('Помилка')) entry.classList.add('error');
                else if (data.log.includes('===') || data.log.includes('[•]')) entry.classList.add('highlight');

                entry.textContent = data.log;
                logsContainer.appendChild(entry);
                logsContainer.scrollTop = logsContainer.scrollHeight;
            }
        } catch (e) {
            console.error('Log parse error:', e);
        }
    };
}

// Actions
async function startQRLogin() {
    try {
        const res = await fetch('/api/auth/start-qr', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'need_qr') {
            openModal(data.qr_image, 'Скануйте QR-код у Telegram', 'Відкрийте Telegram > Налаштування > Пристрої > Підключити пристрій');
        } else if (data.status === 'already_authorized') {
            alert('Ви вже успішно авторизовані!');
        }
    } catch (e) {
        alert('Помилка запуску QR авторизації: ' + e);
    }
}

async function submit2FA() {
    const pwd = document.getElementById('input-2fa')?.value;
    if (!pwd) return;
    try {
        const res = await fetch('/api/auth/2fa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: pwd })
        });
        const data = await res.json();
        if (data.status === 'authorized') {
            alert('Успішний вхід із 2FA!');
            updateStatus();
        } else {
            alert('Помилка 2FA: ' + (data.message || 'Невірний пароль'));
        }
    } catch (e) {
        alert('Помилка відправки 2FA: ' + e);
    }
}

async function triggerFetch() {
    try {
        const res = await fetch('/api/actions/fetch', { method: 'POST' });
        if (res.ok) {
            switchTab('logs');
        }
    } catch (e) {
        alert('Помилка запуску синхронізації: ' + e);
    }
}

async function triggerAnalyze() {
    try {
        const res = await fetch('/api/actions/analyze', { method: 'POST' });
        if (res.ok) {
            switchTab('logs');
        }
    } catch (e) {
        alert('Помилка запуску аналізу: ' + e);
    }
}

function switchTab(tabId) {
    const btn = document.querySelector(`.nav-tab[data-tab="${tabId}"]`);
    if (btn) btn.click();
}

// Gallery & Report loader
async function loadGallery() {
    const container = document.getElementById('gallery-container');
    if (!container) return;

    try {
        const res = await fetch('/api/infographics');
        const categories = await res.json();

        container.innerHTML = '';
        let totalItems = 0;

        for (const [key, cat] of Object.entries(categories)) {
            if (!cat.items || cat.items.length === 0) continue;
            totalItems += cat.items.length;

            const iconName = categoryIcons[key] || 'bar-chart-2';
            const block = document.createElement('div');
            block.className = 'category-block';
            block.innerHTML = `
                <h2 class="section-title">
                    <i data-lucide="${iconName}"></i>
                    <span>${cat.title}</span>
                </h2>
                <div class="gallery-grid" id="cat-grid-${key}"></div>
            `;
            container.appendChild(block);

            const grid = block.querySelector(`#cat-grid-${key}`);
            cat.items.forEach(it => {
                const card = document.createElement('div');
                card.className = 'chart-card';
                card.onclick = () => openModal(`/static/infographics/${it.file}?t=${Date.now()}`, it.title, it.desc);
                card.innerHTML = `
                    <img class="chart-preview" src="/static/infographics/${it.file}?t=${Date.now()}" alt="${it.title}" loading="lazy">
                    <div class="chart-info">
                        <div class="chart-title">${it.title}</div>
                        <div class="chart-desc">${it.desc}</div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        if (totalItems === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 4rem; color: var(--text-dim);">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem; color: var(--accent);">
                        <i data-lucide="image-off"></i>
                    </div>
                    <h3>Інфографіку ще не згенеровано</h3>
                    <p style="margin-top: 0.5rem;">Натисніть «Запустити повний аналіз», щоб побудувати всі графіки.</p>
                </div>
            `;
        }

        refreshIcons();
    } catch (e) {
        console.error('Failed to load gallery:', e);
    }
}

async function loadReport() {
    const reportBox = document.getElementById('report-content');
    if (!reportBox) return;

    try {
        const res = await fetch('/api/report');
        const data = await res.json();
        reportBox.textContent = data.content;
    } catch (e) {
        reportBox.textContent = 'Помилка завантаження звіту: ' + e;
    }
}

// Modal handling
function openModal(imgSrc, title, desc) {
    const modal = document.getElementById('chart-modal');
    document.getElementById('modal-img').src = imgSrc;
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-desc').textContent = desc || '';
    modal.classList.add('active');
    refreshIcons();
}

function closeModal() {
    const modal = document.getElementById('chart-modal');
    modal.classList.remove('active');
}
