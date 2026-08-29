// WordsTelegramStats Web Client
// Multi-language support (UK / EN) & Realtime Dashboard

const translations = {
    uk: {
        page_title: 'WordsTelegramStats — Статистика Telegram',
        nav_gallery: 'Інфографіка',
        nav_report: 'Текстовий звіт',
        nav_logs: 'Термінал та Логи',
        stat_chats_title: 'Особисті чати',
        stat_chats_sub: 'Окремих баз SQLite',
        stat_messages_title: 'Надіслано повідомлень',
        stat_messages_sub: 'Лише ваші вихідні повідомлення (from_user)',
        stat_period_title: 'Період активності',
        stat_period_sub: 'Охоплення історії',
        stat_infographics_title: 'Графіків згенеровано',
        stat_infographics_sub: 'Інфографіка високої якості',
        pipeline_title: 'Управління пайплайном',
        pipeline_desc: 'Синхронізація виключно ваших вихідних повідомлень (без повідомлень співрозмовника) для персонального аналізу лише вашого стилю.',
        btn_fetch: 'Синхронізувати повідомлення',
        btn_analyze: 'Запустити повний аналіз',
        report_section_title: 'Повний лінгвістичний звіт (advanced_report.txt)',
        btn_refresh: 'Оновити',
        report_loading: 'Завантаження звіту...',
        report_empty: 'Звіт ще не згенеровано. Запустіть аналіз.',
        report_error: 'Помилка завантаження звіту: ',
        logs_section_title: 'Лайв-термінал процесів',
        logs_ready: '[System] Готовий до роботи. Натисніть дію вище для запуску.',
        modal_chart_title: 'Графік',
        modal_2fa_title: 'Двоетапна перевірка (2FA)',
        modal_2fa_desc: 'Ваш обліковий запис захищений паролем. Введіть його для завершення авторизації.',
        modal_2fa_placeholder: 'Введіть 2FA пароль',
        btn_confirm_2fa: 'Підтвердити пароль',
        checking_2fa: 'Перевірка...',
        enter_password_alert: 'Будь ласка, введіть пароль.',
        invalid_2fa: 'Невірний 2FA пароль. Спробуйте ще раз.',
        server_error: "Помилка з'єднання із сервером: ",
        qr_modal_title: 'Скануйте QR-код у Telegram',
        qr_modal_desc: 'Відкрийте Telegram на телефоні: Налаштування → Пристрої → Підключити пристрій',
        already_authorized: 'Ви вже успішно авторизовані!',
        qr_start_error: 'Помилка запуску QR авторизації: ',
        confirm_logout: 'Ви дійсно бажаєте вийти з облікового запису Telegram?',
        logout_error: 'Помилка виходу: ',
        fetch_error: 'Помилка запуску синхронізації: ',
        analyze_error: 'Помилка запуску аналізу: ',
        status_checking: 'Перевірка...',
        status_syncing: 'Синхронізація...',
        status_analyzing: 'Аналіз...',
        status_connected: 'Підключено',
        status_unauthorized: 'Не авторизовано',
        btn_login_qr: 'Увійти через QR',
        btn_enter_2fa: 'Ввести 2FA',
        btn_logout: 'Вийти',
        btn_logout_title: 'Вийти з облікового запису Telegram',
        gallery_empty_title: 'Інфографіку ще не згенеровано',
        gallery_empty_desc: 'Натисніть «Запустити повний аналіз», щоб побудувати всі графіки.',
        progress_prep_scan: 'Підготовка: аналіз обсягу чатів...',
        progress_prep_prefix: 'Підготовка',
        progress_scan_badge: 'Сканування',
        progress_found_msgs: 'Знайдено: ~{count} пов.',
        progress_queue_eval: 'Оцінка черги',
        progress_checked_chats: 'Перевірено {idx} із {total} чатів',
        progress_sync_title: 'Синхронізація повідомлень Telegram',
        progress_pipeline_title: 'Аналітичний пайплайн...',
        progress_chat_label: 'Чат',
        progress_speed: '{speed} пов/сек',
        progress_speed_na: '— пов/сек',
        progress_eta: 'Залишилось: ~{eta}',
        progress_eta_calc: 'розрахунок...',
        progress_msgs_stat: '{curr} / {total} повідомлень',
        progress_prep_fetch: 'Підготовка до синхронізації...',
        progress_prep_analyze: 'Обробка аналітики та побудова графіків...',
        progress_in_progress: 'Виконується...',
        progress_wait: 'Зачекайте...',
        progress_data_processing: 'Обробка даних...',
        categories: {
            dashboard: 'Головне та базова інфографіка',
            time: 'Часові патерни, ритм та режим сну',
            style: 'Стиль мовлення, словник та лінгвістика',
            social: 'Стосунки, чати та кластеризація'
        },
        charts: {
            'wordcloud.png': { title: 'Хмара слів', desc: 'Візуалізація найчастіших змістовних слів за весь час' },
            'top_words.png': { title: 'Топ-25 змістовних слів', desc: 'Рейтинг найбільш вживаних лексичних одиниць' },
            'years_volume.png': { title: 'Обсяг за роками', desc: 'Динаміка кількості повідомлень та слів' },
            'ttr_evolution.png': { title: 'Багатство мови (TTR)', desc: 'Словникове різноманіття та середня довжина реплік' },
            'zipf_distribution.png': { title: 'Закон Ціпфа', desc: 'Рангочастотний розподіл слів vs ідеальний закон' },
            'zipf_law.png': { title: 'Закон Ціпфа', desc: 'Рангочастотний розподіл слів vs ідеальний закон' },
            'word_length_distribution.png': { title: 'Довжина слів', desc: 'Розподіл слів за кількістю літер' },
            'timeline_monthly.png': { title: 'Щомісячний таймлайн', desc: 'Обсяг повідомлень місяць за місяцем за всі роки' },
            'activity_by_hour.png': { title: 'Активність за годинами', desc: 'Добовий розподіл відправки повідомлень' },
            'activity_by_weekday.png': { title: 'Активність за днями тижня', desc: 'Порівняння робочих днів та вихідних' },
            'activity_heatmap.png': { title: 'Теплова карта активності', desc: 'Години доби × дні тижня' },
            'seasonality.png': { title: 'Сезонність', desc: 'У які місяці року інтенсивність спілкування найвища' },
            'night_trend.png': { title: 'Нічні повідомлення', desc: 'Частка повідомлень після півночі (00:00–06:00)' },
            'active_days.png': { title: 'Активні дні та серії', desc: 'Кількість активних днів на рік та рекорди поспіль' },
            'sleep_evolution.png': { title: 'Еволюція режиму сну', desc: 'Реконструкція часу засинання, пробудження та тривалості сну' },
            'message_rhythm.png': { title: 'Ритм та паузи', desc: 'Розподіл пауз між репліками та частка повідомлень-черг' },
            'msg_length_dist.png': { title: 'Розподіл довжини реплік', desc: 'Гістограма довжини повідомлень у словах' },
            'core_vocabulary.png': { title: 'Кістяк мовлення', desc: 'Слова, що стабільно вживаються з року в рік (heatmap)' },
            'signature_words.png': { title: '«Фірмові» слова', desc: 'Характерні слова проти нормативного еталону мови' },
            'vocab_timeline.png': { title: 'Чесний ріст словника', desc: 'Крива накопичення перевірених та словникових лем' },
            'vocab_growth.png': { title: 'Закон Хіпса', desc: 'Зростання словникового запасу від обсягу тексту' },
            'vocab_validation.png': { title: 'Склад словника', desc: 'Словникові слова vs латиниця vs сленг/одруківки' },
            'ngrams.png': { title: 'Коронні фрази', desc: 'Топ стійких біграм та триграм' },
            'pos_evolution.png': { title: 'Частини мови', desc: 'Співвідношення дієслів, іменників, прикметників' },
            'informality.png': { title: 'Неформальність', desc: 'Частка несловникових слів та сленгу за роками' },
            'laughter_evolution.png': { title: 'Еволюція сміху', desc: 'Динаміка написання сміху (ха-ха, хпхвх, хехе)' },
            'questions_exclamations.png': { title: 'Питання та знаки оклику', desc: 'Емоційність та частка повідомлень із ? та !' },
            'profanity_trend.png': { title: 'Частота мату', desc: 'Ненормативна лексика на 1000 слів за роками' },
            'language_mix.png': { title: 'Мовний мікс', desc: 'Співвідношення мов (українська / російська / англійська)' },
            'top_chats.png': { title: 'Топ діалогів', desc: 'Найбільш активні чати за кількістю повідомлень' },
            'streamgraph_chats.png': { title: 'Потік спілкування (Streamgraph)', desc: 'Як з роками перерозподілялась увага між чатами' },
            'social_breadth.png': { title: 'Широта спілкування', desc: 'Кількість співрозмовників на місяць та частка топ-3' },
            'relationships_timeline.png': { title: 'Таймлайн життя чатів', desc: 'Коли починалось, спалахувало та згасало спілкування' },
            'chat_fingerprint.png': { title: 'Лінгвістичні відбитки чатів', desc: 'Характерні слова для кожного контакту (TF-IDF)' },
            'ty_vy.png': { title: 'Ти / Ви', desc: 'Рівень формальності та пропорція звертань' },
            'mat_per_chat.png': { title: 'Мат за чатами', desc: 'Розподіл ненормативної лексики по конкретних діалогах' },
            'speech_clustering.png': { title: 'Кластеризація мовлення', desc: 'Дендрограма схожості лексичного стилю з різними людьми' },
            'speech_similarity_matrix.png': { title: 'Матриця схожості стилю', desc: 'Теплова карта попарної косинусної схожості лексики між чатами' }
        }
    },
    en: {
        page_title: 'WordsTelegramStats — Telegram Analytics',
        nav_gallery: 'Infographics',
        nav_report: 'Text Report',
        nav_logs: 'Terminal & Logs',
        stat_chats_title: 'Private Chats',
        stat_chats_sub: 'Individual SQLite databases',
        stat_messages_title: 'Messages Sent',
        stat_messages_sub: 'Exclusively your outgoing messages (from_user)',
        stat_period_title: 'Activity Period',
        stat_period_sub: 'Historical coverage',
        stat_infographics_title: 'Charts Generated',
        stat_infographics_sub: 'High-quality infographics',
        pipeline_title: 'Pipeline Management',
        pipeline_desc: 'Synchronization of exclusively your outgoing messages (excluding interlocutor messages) for personal stylometric analysis of only your speech.',
        btn_fetch: 'Sync Messages',
        btn_analyze: 'Run Full Pipeline',
        report_section_title: 'Full Linguistic Report (advanced_report.txt)',
        btn_refresh: 'Refresh',
        report_loading: 'Loading report...',
        report_empty: 'Report has not been generated yet. Please run analysis.',
        report_error: 'Failed to load report: ',
        logs_section_title: 'Live Process Terminal',
        logs_ready: '[System] Ready. Click an action above to start.',
        modal_chart_title: 'Chart',
        modal_2fa_title: 'Two-Step Verification (2FA)',
        modal_2fa_desc: 'Your Telegram account is protected with a password. Enter it to complete authorization.',
        modal_2fa_placeholder: 'Enter 2FA password',
        btn_confirm_2fa: 'Confirm Password',
        checking_2fa: 'Verifying...',
        enter_password_alert: 'Please enter your password.',
        invalid_2fa: 'Invalid 2FA password. Please try again.',
        server_error: 'Server connection error: ',
        qr_modal_title: 'Scan QR Code in Telegram',
        qr_modal_desc: 'Open Telegram on your mobile: Settings → Devices → Link Desktop Device',
        already_authorized: 'You are already successfully authorized!',
        qr_start_error: 'Failed to start QR authorization: ',
        confirm_logout: 'Are you sure you want to log out from your Telegram account?',
        logout_error: 'Logout error: ',
        fetch_error: 'Failed to start message synchronization: ',
        analyze_error: 'Failed to start analytics pipeline: ',
        status_checking: 'Checking...',
        status_syncing: 'Syncing...',
        status_analyzing: 'Analyzing...',
        status_connected: 'Connected',
        status_unauthorized: 'Unauthorized',
        btn_login_qr: 'Login via QR',
        btn_enter_2fa: 'Enter 2FA',
        btn_logout: 'Logout',
        btn_logout_title: 'Log out from Telegram account',
        gallery_empty_title: 'No Infographics Generated Yet',
        gallery_empty_desc: 'Click "Run Full Pipeline" to build all charts.',
        progress_prep_scan: 'Preparing: analyzing chat volumes...',
        progress_prep_prefix: 'Preparing',
        progress_scan_badge: 'Scanning',
        progress_found_msgs: 'Found: ~{count} msgs',
        progress_queue_eval: 'Queue estimation',
        progress_checked_chats: 'Checked {idx} of {total} chats',
        progress_sync_title: 'Syncing Telegram Messages',
        progress_pipeline_title: 'Analytics Pipeline...',
        progress_chat_label: 'Chat',
        progress_speed: '{speed} msg/sec',
        progress_speed_na: '— msg/sec',
        progress_eta: 'Remaining: ~{eta}',
        progress_eta_calc: 'calculating...',
        progress_msgs_stat: '{curr} / {total} messages',
        progress_prep_fetch: 'Preparing for synchronization...',
        progress_prep_analyze: 'Processing analytics & building charts...',
        progress_in_progress: 'In progress...',
        progress_wait: 'Please wait...',
        progress_data_processing: 'Processing data...',
        categories: {
            dashboard: 'Summary & Core Infographics',
            time: 'Temporal Patterns, Rhythm & Sleep Schedule',
            style: 'Stylometry, Vocabulary & Linguistics',
            social: 'Relationships, Social Dynamics & Clustering'
        },
        charts: {
            'wordcloud.png': { title: 'Word Cloud', desc: 'Visualization of the most frequent meaningful words of all time' },
            'top_words.png': { title: 'Top 25 Words', desc: 'Ranking of the most frequently used lexical units' },
            'years_volume.png': { title: 'Volume by Year', desc: 'Yearly dynamics of messages and word count' },
            'ttr_evolution.png': { title: 'Lexical Richness (TTR)', desc: 'Type-Token Ratio and average message length over time' },
            'zipf_distribution.png': { title: "Zipf's Law", desc: 'Rank-frequency word distribution vs theoretical ideal' },
            'zipf_law.png': { title: "Zipf's Law", desc: 'Rank-frequency word distribution vs theoretical ideal' },
            'word_length_distribution.png': { title: 'Word Length', desc: 'Word distribution by letter count' },
            'timeline_monthly.png': { title: 'Monthly Timeline', desc: 'Message volume month by month across all years' },
            'activity_by_hour.png': { title: 'Hourly Activity', desc: '24-hour daily message dispatch distribution' },
            'activity_by_weekday.png': { title: 'Weekday Activity', desc: 'Comparison of weekdays vs weekends' },
            'activity_heatmap.png': { title: 'Activity Heatmap', desc: 'Day of week × Hour of day' },
            'seasonality.png': { title: 'Seasonality', desc: 'Months with peak communication intensity' },
            'night_trend.png': { title: 'Night Messages', desc: 'Share of messages sent after midnight (00:00–06:00)' },
            'active_days.png': { title: 'Active Days & Streaks', desc: 'Annual active days count and consecutive activity records' },
            'sleep_evolution.png': { title: 'Sleep Schedule Evolution', desc: 'Reconstruction of bedtime, wake-up time, and sleep duration' },
            'message_rhythm.png': { title: 'Message Rhythm & Pauses', desc: 'Inter-message time gaps and burstiness ratio' },
            'msg_length_dist.png': { title: 'Message Length Distribution', desc: 'Histogram of message lengths in words' },
            'core_vocabulary.png': { title: 'Core Vocabulary', desc: 'Words persistently used year over year (heatmap)' },
            'signature_words.png': { title: 'Signature Words', desc: 'Characteristic words vs standard language baseline' },
            'vocab_timeline.png': { title: 'Honest Vocabulary Growth', desc: 'Cumulative curve of verified and standard dictionary lemmas' },
            'vocab_growth.png': { title: "Heaps' Law", desc: 'Vocabulary growth relative to total corpus volume' },
            'vocab_validation.png': { title: 'Vocabulary Structure', desc: 'Dictionary words vs Latin vs slang & typos' },
            'ngrams.png': { title: 'Signature N-grams', desc: 'Top frequent bigrams and trigrams' },
            'pos_evolution.png': { title: 'Parts of Speech (POS)', desc: 'Balance of verbs, nouns, adjectives, and adverbs' },
            'informality.png': { title: 'Informality Trend', desc: 'Share of non-dictionary slang and informal speech' },
            'laughter_evolution.png': { title: 'Laughter Evolution', desc: 'Evolution of textual laughter (haha, hehe, lol, etc.)' },
            'questions_exclamations.png': { title: 'Questions & Exclamations', desc: 'Emotional tone and proportion of ? and ! messages' },
            'profanity_trend.png': { title: 'Profanity Trend', desc: 'Strong language frequency per 1,000 words over time' },
            'language_mix.png': { title: 'Language Mix', desc: 'Proportion of languages (Ukrainian / Russian / English)' },
            'top_chats.png': { title: 'Top Dialogues', desc: 'Most active chats by total message count' },
            'streamgraph_chats.png': { title: 'Social Attention Streamgraph', desc: 'Redistribution of attention and chat volume over years' },
            'social_breadth.png': { title: 'Social Breadth', desc: 'Active monthly contacts and Top-3 concentration' },
            'relationships_timeline.png': { title: 'Relationship Lifecycles', desc: 'When dialogues emerged, peaked, and faded' },
            'chat_fingerprint.png': { title: 'Chat Fingerprints (TF-IDF)', desc: 'Distinctive keywords unique to specific contacts' },
            'ty_vy.png': { title: 'Formality Index (Ty/Vy)', desc: 'Ratio of informal vs formal addressing' },
            'mat_per_chat.png': { title: 'Profanity by Chat', desc: 'Distribution of profanity across individual chats' },
            'speech_clustering.png': { title: 'Speech Style Clustering', desc: 'Dendrogram of vocabulary style similarity across contacts' },
            'speech_similarity_matrix.png': { title: 'Speech Style Similarity Matrix', desc: 'Heatmap of pairwise vocabulary cosine similarity across chats' }
        }
    }
};

let currentLang = localStorage.getItem('wts_lang') || 'uk';

function t(key, params = {}) {
    const dict = translations[currentLang] || translations.uk;
    let val = dict[key] || (translations.uk && translations.uk[key]) || key;
    if (typeof val === 'string') {
        for (const [k, v] of Object.entries(params)) {
            val = val.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
        }
    }
    return val;
}

// Global state
let appState = {
    currentTab: 'gallery',
    isAuthorized: false,
    taskRunning: false,
    taskType: null,
    authModalOpen: false,
    in2FAMode: false,
    lastStatusData: null,
    lastInfographicsData: null,
    hasReport: false,
    reportContent: null,
    currentModalChartFile: null
};

// Set language & immediately re-render all UI elements
function setLanguage(lang) {
    if (lang !== 'uk' && lang !== 'en') lang = 'uk';
    currentLang = lang;
    localStorage.setItem('wts_lang', lang);
    document.documentElement.lang = lang;

    // Document title
    document.title = t('page_title');

    // Update switcher active buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Update static i18n text nodes
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        el.textContent = t(key);
    });

    // Update placeholder attributes
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.dataset.i18nPlaceholder;
        el.placeholder = t(key);
    });

    // Update title attributes
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.dataset.i18nTitle;
        el.title = t(key);
    });

    // Update report view placeholder if no report loaded yet
    const reportBox = document.getElementById('report-content');
    if (reportBox) {
        if (!appState.hasReport) {
            reportBox.textContent = t('report_empty');
        }
    }

    // Update modal if currently open
    if (appState.currentModalChartFile) {
        const meta = getChartMeta(appState.currentModalChartFile);
        const modalTitle = document.getElementById('modal-title');
        const modalDesc = document.getElementById('modal-desc');
        if (modalTitle) modalTitle.textContent = meta.title;
        if (modalDesc) modalDesc.textContent = meta.desc;
    }

    // Instant UI re-render from cached state
    if (appState.lastStatusData) {
        renderStatus(appState.lastStatusData);
    }
    if (appState.lastInfographicsData) {
        renderGallery(appState.lastInfographicsData);
    }

    refreshIcons();
}

window.setLanguage = setLanguage;

// Category icon map
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
    // Attach click listener to language switcher buttons
    const langSwitch = document.getElementById('lang-switch');
    if (langSwitch) {
        langSwitch.addEventListener('click', (e) => {
            const btn = e.target.closest('.lang-btn');
            if (btn && btn.dataset.lang) {
                setLanguage(btn.dataset.lang);
            }
        });
    }

    setLanguage(currentLang);
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
let pollingInterval = null;

async function initStatusPolling() {
    await updateStatus();
    pollingInterval = setInterval(updateStatus, 1500);
}

async function updateStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        appState.lastStatusData = data;
        renderStatus(data);
    } catch (e) {
        console.error('Status fetch failed:', e);
    }
}

function renderStatus(data) {
    appState.isAuthorized = data.is_authorized;
    appState.taskRunning = data.task_running;
    appState.taskType = data.task_type;

    const numLocale = currentLang === 'uk' ? 'uk-UA' : 'en-US';

    // Header status badge
    const badge = document.getElementById('auth-badge');
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');

    if (data.task_running) {
        dot.className = 'status-dot working';
        text.textContent = data.task_type === 'fetch' ? t('status_syncing') : t('status_analyzing');
    } else if (data.is_authorized) {
        dot.className = 'status-dot online';
        const u = data.user_info;
        text.textContent = u ? `${u.first_name} (@${u.username || 'user'})` : t('status_connected');
    } else {
        dot.className = 'status-dot offline';
        text.textContent = t('status_unauthorized');
    }

    // Auto-close modal on successful authorization
    if (data.is_authorized && appState.authModalOpen) {
        closeModal();
        appState.authModalOpen = false;
        appState.in2FAMode = false;
    }

    // Transition modal to 2FA input if required
    if (!data.is_authorized && data.auth_status === 'need_2fa' && appState.authModalOpen && !appState.in2FAMode) {
        showModal2FA();
    }

    // Dashboard metric cards
    const statChats = document.getElementById('stat-chats');
    const statMessages = document.getElementById('stat-messages');
    const statInfographics = document.getElementById('stat-infographics');
    const statPeriod = document.getElementById('stat-period');

    if (statChats) statChats.textContent = data.total_chats || 0;
    if (statMessages) statMessages.textContent = (data.total_messages || 0).toLocaleString(numLocale);
    if (statInfographics) statInfographics.textContent = data.infographics_count || 0;

    if (statPeriod) {
        if (data.min_date && data.max_date) {
            const y1 = data.min_date.substring(0, 4);
            const y2 = data.max_date.substring(0, 4);
            statPeriod.textContent = `${y1} — ${y2}`;
        } else {
            statPeriod.textContent = '—';
        }
    }

    // Live Progress Card
    const progressCard = document.getElementById('task-progress-card');
    if (progressCard) {
        if (data.task_running && data.progress) {
            progressCard.style.display = 'flex';
            const p = data.progress;

            if (p.phase === 'precheck') {
                const rawChat = (p.current_chat || '').replace(/^Підготовка:?\s*/i, '').replace(/^Preparing:?\s*/i, '').trim();
                const chatDisplay = rawChat ? `${t('progress_prep_prefix')}: ${rawChat}` : t('progress_scan_badge');
                document.getElementById('progress-task-name').textContent = t('progress_prep_scan');
                document.getElementById('progress-chat-badge').textContent = `[${p.chat_idx}/${p.total_chats}] ${chatDisplay}`;
                document.getElementById('progress-speed-badge').textContent = t('progress_found_msgs', { count: (p.current || 0).toLocaleString(numLocale) });
                document.getElementById('progress-eta-badge').textContent = t('progress_queue_eval');
                document.getElementById('progress-bar-fill').style.width = `${Math.min(100, Math.max(0, p.pct))}%`;
                document.getElementById('progress-count-text').textContent = t('progress_checked_chats', { idx: p.chat_idx, total: p.total_chats });
                document.getElementById('progress-pct-text').textContent = `${(p.pct || 0).toFixed(1)}%`;
            } else {
                const rawChat = (p.current_chat || '').replace(/^Підготовка:?\s*/i, '').replace(/^Preparing:?\s*/i, '').trim();
                const chatDisplay = rawChat || t('progress_chat_label');
                document.getElementById('progress-task-name').textContent =
                    data.task_type === 'fetch' ? t('progress_sync_title') : t('progress_pipeline_title');

                document.getElementById('progress-chat-badge').textContent =
                    `[${p.chat_idx}/${p.total_chats}] ${chatDisplay}`;

                document.getElementById('progress-speed-badge').textContent =
                    p.speed > 0 ? t('progress_speed', { speed: p.speed.toLocaleString(numLocale) }) : t('progress_speed_na');

                document.getElementById('progress-eta-badge').textContent =
                    t('progress_eta', { eta: p.eta || t('progress_eta_calc') });

                document.getElementById('progress-bar-fill').style.width = `${Math.min(100, Math.max(0, p.pct))}%`;

                document.getElementById('progress-count-text').textContent =
                    t('progress_msgs_stat', {
                        curr: (p.current || 0).toLocaleString(numLocale),
                        total: (p.total || 0).toLocaleString(numLocale)
                    });

                document.getElementById('progress-pct-text').textContent = `${(p.pct || 0).toFixed(1)}%`;
            }
        } else if (data.task_running) {
            progressCard.style.display = 'flex';
            document.getElementById('progress-task-name').textContent =
                data.task_type === 'fetch' ? t('progress_prep_fetch') : t('progress_prep_analyze');
            document.getElementById('progress-chat-badge').textContent = t('progress_in_progress');
            document.getElementById('progress-speed-badge').textContent = '—';
            document.getElementById('progress-eta-badge').textContent = t('progress_wait');
            document.getElementById('progress-bar-fill').style.width = '100%';
            document.getElementById('progress-count-text').textContent = t('progress_data_processing');
            document.getElementById('progress-pct-text').textContent = '...';
        } else {
            progressCard.style.display = 'none';
        }
    }

    // Button states
    const btnFetch = document.getElementById('btn-fetch');
    const btnAnalyze = document.getElementById('btn-analyze');
    if (btnFetch) btnFetch.disabled = data.task_running || !data.is_authorized;
    if (btnAnalyze) btnAnalyze.disabled = data.task_running || data.total_messages === 0;

    // Auth container logic in header
    const authContainer = document.getElementById('auth-actions-container');
    if (authContainer) {
        if (!data.is_authorized) {
            const btnLabel = data.auth_status === 'need_2fa' ? t('btn_enter_2fa') : t('btn_login_qr');
            authContainer.innerHTML = `
                <button class="btn btn-secondary" onclick="startQRLogin()">
                    <i data-lucide="key"></i>
                    <span>${btnLabel}</span>
                </button>
            `;
            refreshIcons();
        } else {
            authContainer.innerHTML = `
                <button class="btn btn-secondary btn-logout" onclick="triggerLogout()" title="${t('btn_logout_title')}">
                    <i data-lucide="log-out"></i>
                    <span>${t('btn_logout')}</span>
                </button>
            `;
            refreshIcons();
        }
    }
}

// Log streaming & direct rendering via SSE
function initLogStream() {
    const logsContainer = document.getElementById('logs-terminal');
    const evtSource = new EventSource('/api/logs/stream');

    evtSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.log) {
                const isNearBottom = (logsContainer.scrollHeight - logsContainer.scrollTop - logsContainer.clientHeight) <= 80;

                const entry = document.createElement('div');
                entry.className = 'log-entry';
                if (data.log.includes('[✔]')) entry.classList.add('success');
                else if (data.log.includes('[❌]') || data.log.includes('Помилка') || data.log.includes('Error')) entry.classList.add('error');
                else if (data.log.includes('===') || data.log.includes('[•]') || data.log.includes('ℹ️')) entry.classList.add('highlight');

                entry.textContent = data.log;
                logsContainer.appendChild(entry);

                if (isNearBottom) {
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                }
            }
        } catch (e) {
            console.error('Log parse error:', e);
        }
    };
}

// QR Login Actions
async function startQRLogin() {
    try {
        const res = await fetch('/api/auth/start-qr', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'need_qr') {
            appState.authModalOpen = true;
            appState.in2FAMode = false;

            document.getElementById('modal-img').style.display = 'block';
            document.getElementById('modal-2fa-container').style.display = 'none';

            openModal(
                data.qr_image,
                t('qr_modal_title'),
                t('qr_modal_desc')
            );
        } else if (data.status === 'already_authorized') {
            alert(t('already_authorized'));
        }
    } catch (e) {
        alert(t('qr_start_error') + e);
    }
}

function showModal2FA() {
    appState.in2FAMode = true;
    appState.authModalOpen = true;

    const modal = document.getElementById('chart-modal');
    document.getElementById('modal-title').textContent = t('modal_2fa_title');
    document.getElementById('modal-img').style.display = 'none';
    document.getElementById('modal-desc').textContent = '';

    const twoFaBox = document.getElementById('modal-2fa-container');
    twoFaBox.style.display = 'block';

    const input = document.getElementById('modal-2fa-input');
    input.value = '';
    input.placeholder = t('modal_2fa_placeholder');
    const errBox = document.getElementById('modal-2fa-error');
    errBox.style.display = 'none';
    errBox.textContent = '';

    modal.classList.add('active');
    refreshIcons();

    setTimeout(() => input.focus(), 100);
}

async function submitModal2FA() {
    const input = document.getElementById('modal-2fa-input');
    const errBox = document.getElementById('modal-2fa-error');
    const btn = document.getElementById('btn-modal-2fa');
    const pwd = input.value.trim();

    if (!pwd) {
        errBox.textContent = t('enter_password_alert');
        errBox.style.display = 'block';
        input.focus();
        return;
    }

    errBox.style.display = 'none';
    btn.disabled = true;
    btn.innerHTML = `<i data-lucide="loader-2"></i> <span>${t('checking_2fa')}</span>`;
    refreshIcons();

    try {
        const res = await fetch('/api/auth/2fa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: pwd })
        });
        const data = await res.json();

        if (data.status === 'authorized') {
            closeModal();
            appState.authModalOpen = false;
            appState.in2FAMode = false;
            await updateStatus();
        } else {
            errBox.textContent = data.message || t('invalid_2fa');
            errBox.style.display = 'block';
            input.focus();
            input.select();
        }
    } catch (e) {
        errBox.textContent = t('server_error') + e;
        errBox.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="key"></i> <span>${t('btn_confirm_2fa')}</span>`;
        refreshIcons();
    }
}

async function triggerLogout() {
    if (!confirm(t('confirm_logout'))) return;
    try {
        const res = await fetch('/api/auth/logout', { method: 'POST' });
        if (res.ok) {
            await updateStatus();
        }
    } catch (e) {
        alert(t('logout_error') + e);
    }
}

async function triggerFetch() {
    try {
        const res = await fetch(`/api/actions/fetch?lang=${currentLang}`, { method: 'POST' });
        if (res.ok) {
            switchTab('logs');
        }
    } catch (e) {
        alert(t('fetch_error') + e);
    }
}

async function triggerAnalyze() {
    try {
        const res = await fetch(`/api/actions/analyze?lang=${currentLang}`, { method: 'POST' });
        if (res.ok) {
            switchTab('logs');
        }
    } catch (e) {
        alert(t('analyze_error') + e);
    }
}

function switchTab(tabId) {
    const btn = document.querySelector(`.nav-tab[data-tab="${tabId}"]`);
    if (btn) btn.click();
}

// Localized chart metadata
function getChartMeta(fileName, fallbackTitle, fallbackDesc) {
    const dict = translations[currentLang] || translations.uk;
    const chartInfo = dict.charts && dict.charts[fileName];
    if (chartInfo) {
        return {
            title: chartInfo.title,
            desc: chartInfo.desc
        };
    }
    return {
        title: fallbackTitle || fileName,
        desc: fallbackDesc || ''
    };
}

// Gallery loader & renderer
async function loadGallery() {
    try {
        const res = await fetch('/api/infographics');
        const categories = await res.json();
        appState.lastInfographicsData = categories;
        renderGallery(categories);
    } catch (e) {
        console.error('Failed to load gallery:', e);
    }
}

function renderGallery(categories) {
    const container = document.getElementById('gallery-container');
    if (!container) return;

    container.innerHTML = '';
    let totalItems = 0;

    const dict = translations[currentLang] || translations.uk;

    for (const [key, cat] of Object.entries(categories)) {
        if (!cat.items || cat.items.length === 0) continue;
        totalItems += cat.items.length;

        const iconName = categoryIcons[key] || 'bar-chart-2';
        const catTitle = (dict.categories && dict.categories[key]) || cat.title;

        const block = document.createElement('div');
        block.className = 'category-block';
        block.innerHTML = `
            <h2 class="section-title">
                <i data-lucide="${iconName}"></i>
                <span>${catTitle}</span>
            </h2>
            <div class="gallery-grid" id="cat-grid-${key}"></div>
        `;
        container.appendChild(block);

        const grid = block.querySelector(`#cat-grid-${key}`);
        cat.items.forEach(it => {
            const meta = getChartMeta(it.file, it.title, it.desc);
            const card = document.createElement('div');
            card.className = 'chart-card';
            card.onclick = () => openModal(`/static/infographics/${it.file}?t=${Date.now()}`, meta.title, meta.desc, it.file);
            card.innerHTML = `
                <img class="chart-preview" src="/static/infographics/${it.file}?t=${Date.now()}" alt="${meta.title}" loading="lazy">
                <div class="chart-info">
                    <div class="chart-title">${meta.title}</div>
                    <div class="chart-desc">${meta.desc}</div>
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
                <h3>${t('gallery_empty_title')}</h3>
                <p style="margin-top: 0.5rem;">${t('gallery_empty_desc')}</p>
            </div>
        `;
    }

    refreshIcons();
}

async function loadReport() {
    const reportBox = document.getElementById('report-content');
    if (!reportBox) return;

    try {
        const res = await fetch('/api/report');
        const data = await res.json();
        if (data.exists && data.content) {
            appState.hasReport = true;
            appState.reportContent = data.content;
            reportBox.textContent = data.content;
        } else {
            appState.hasReport = false;
            appState.reportContent = null;
            reportBox.textContent = t('report_empty');
        }
    } catch (e) {
        reportBox.textContent = t('report_error') + e;
    }
}

// Modal handling
function openModal(imgSrc, title, desc, file = null) {
    appState.currentModalChartFile = file;
    const modal = document.getElementById('chart-modal');
    document.getElementById('modal-img').src = imgSrc;
    document.getElementById('modal-img').style.display = 'block';
    document.getElementById('modal-2fa-container').style.display = 'none';
    document.getElementById('modal-title').textContent = title || t('modal_chart_title');
    document.getElementById('modal-desc').textContent = desc || '';
    modal.classList.add('active');
    refreshIcons();
}

function closeModal() {
    const modal = document.getElementById('chart-modal');
    modal.classList.remove('active');
    appState.authModalOpen = false;
    appState.in2FAMode = false;
    appState.currentModalChartFile = null;
}
