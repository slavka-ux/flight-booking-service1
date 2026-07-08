<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README — FlyBooking</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    
    <style>
        /* ============================================
           ГЛОБАЛЬНІ СТИЛІ
           ============================================ */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --color-primary: #2563eb;
            --color-primary-dark: #1d4ed8;
            --color-primary-light: #60a5fa;
            --color-primary-gradient: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            --color-secondary: #0f172a;
            --color-white: #ffffff;
            --color-gray-50: #f8fafc;
            --color-gray-100: #f1f5f9;
            --color-gray-200: #e2e8f0;
            --color-gray-300: #cbd5e1;
            --color-gray-400: #94a3b8;
            --color-gray-500: #64748b;
            --color-gray-600: #475569;
            --color-gray-700: #334155;
            --color-gray-800: #1e293b;
            --color-gray-900: #0f172a;
            --color-success: #10b981;
            --color-danger: #ef4444;
            --color-warning: #f59e0b;
            --shadow: 0 1px 3px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
            --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1);
            --radius: 12px;
            --radius-sm: 6px;
            --radius-full: 9999px;
            --transition: 250ms cubic-bezier(0.4, 0, 0.2, 1);
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
            --max-width: 900px;
            --header-height: 72px;
        }

        html { scroll-behavior: smooth; }

        body {
            font-family: var(--font-family);
            color: var(--color-gray-800);
            background: var(--color-gray-50);
            line-height: 1.7;
            min-height: 100vh;
        }

        .container {
            max-width: var(--max-width);
            margin: 0 auto;
            padding: 0 1.5rem;
            width: 100%;
        }

        /* ============================================
           HEADER
           ============================================ */
        .header {
            background: var(--color-secondary);
            position: sticky;
            top: 0;
            z-index: 1000;
            height: var(--header-height);
            display: flex;
            align-items: center;
            box-shadow: var(--shadow-lg);
        }

        .navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            height: 100%;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--color-white);
            text-decoration: none;
        }
        .logo-icon { font-size: 1.5rem; }
        .logo-text span { color: var(--color-primary-light); }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            list-style: none;
        }

        .nav-links a {
            color: rgba(255,255,255,0.6);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.875rem;
            transition: color var(--transition);
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }
        .nav-links a:hover {
            color: var(--color-white);
        }

        .nav-links a.active {
            color: var(--color-white);
        }

        .badge-version {
            padding: 0.25rem 0.75rem;
            background: rgba(37, 99, 235, 0.2);
            border-radius: var(--radius-full);
            font-size: 0.75rem;
            color: var(--color-primary-light);
            font-weight: 600;
            border: 1px solid rgba(37, 99, 235, 0.2);
        }

        /* ============================================
           HERO
           ============================================ */
        .hero-readme {
            background: var(--color-secondary);
            padding: 3rem 0 2.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        .hero-readme h1 {
            color: var(--color-white);
            font-size: 2.5rem;
            font-weight: 900;
        }

        .hero-readme .subtitle {
            color: rgba(255,255,255,0.6);
            font-size: 1.125rem;
            margin-top: 0.25rem;
        }

        .hero-readme .meta {
            display: flex;
            gap: 1.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }

        .hero-readme .meta span {
            color: rgba(255,255,255,0.4);
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }

        .hero-readme .meta i {
            color: var(--color-primary-light);
        }

        /* ============================================
           ОСНОВНИЙ КОНТЕНТ
           ============================================ */
        .content {
            padding: 3rem 0;
        }

        .toc {
            background: var(--color-white);
            border-radius: var(--radius);
            padding: 1.5rem 2rem;
            box-shadow: var(--shadow);
            margin-bottom: 2.5rem;
            border-left: 4px solid var(--color-primary);
        }

        .toc h2 {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            color: var(--color-gray-900);
        }

        .toc ul {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.25rem 1.5rem;
            list-style: none;
            padding: 0;
        }

        .toc ul li::before {
            content: '▸ ';
            color: var(--color-primary);
        }

        .toc ul li a {
            color: var(--color-gray-600);
            text-decoration: none;
            font-size: 0.875rem;
            transition: color var(--transition);
        }

        .toc ul li a:hover {
            color: var(--color-primary);
        }

        /* ============================================
           СЕКЦІЇ
           ============================================ */
        .section {
            margin-bottom: 3rem;
        }

        .section:last-child {
            margin-bottom: 0;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--color-gray-200);
        }

        .section-header .icon {
            width: 40px;
            height: 40px;
            border-radius: var(--radius-sm);
            background: var(--color-primary-gradient);
            color: var(--color-white);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.125rem;
            flex-shrink: 0;
        }

        .section-header h2 {
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--color-gray-900);
        }

        .section-header .badge {
            margin-left: auto;
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-full);
            font-size: 0.625rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .badge-new {
            background: #d1fae5;
            color: #065f46;
        }

        .badge-core {
            background: #dbeafe;
            color: #1e40af;
        }

        .badge-feature {
            background: #fef3c7;
            color: #92400e;
        }

        .section p {
            color: var(--color-gray-600);
            font-size: 1rem;
            margin-bottom: 1rem;
        }

        .section ul,
        .section ol {
            padding-left: 1.5rem;
            color: var(--color-gray-600);
            margin-bottom: 1rem;
        }

        .section ul li,
        .section ol li {
            margin-bottom: 0.25rem;
        }

        .section ul li strong,
        .section ol li strong {
            color: var(--color-gray-800);
        }

        /* ============================================
           КАРТКИ
           ============================================ */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }

        .card-mini {
            background: var(--color-white);
            border-radius: var(--radius);
            padding: 1.25rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--color-gray-200);
            transition: all var(--transition);
        }

        .card-mini:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: var(--color-primary-light);
        }

        .card-mini .card-icon {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }

        .card-mini h4 {
            font-size: 0.875rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .card-mini p {
            font-size: 0.75rem;
            color: var(--color-gray-500);
            margin-bottom: 0;
        }

        /* ============================================
           КОД
           ============================================ */
        .code-block {
            background: var(--color-gray-900);
            border-radius: var(--radius-sm);
            padding: 1.25rem;
            margin: 1rem 0;
            overflow-x: auto;
            position: relative;
        }

        .code-block .lang {
            position: absolute;
            top: 0.5rem;
            right: 0.75rem;
            font-size: 0.625rem;
            color: rgba(255,255,255,0.3);
            font-family: var(--font-mono);
            background: rgba(255,255,255,0.05);
            padding: 0.125rem 0.5rem;
            border-radius: var(--radius-sm);
        }

        .code-block code {
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: #e2e8f0;
            line-height: 1.8;
            white-space: pre;
        }

        .code-block .comment {
            color: #64748b;
        }

        .code-block .keyword {
            color: #818cf8;
        }

        .code-block .string {
            color: #34d399;
        }

        .code-block .function {
            color: #fbbf24;
        }

        .code-block .variable {
            color: #f472b6;
        }

        /* ============================================
           ТАБЛИЦІ
           ============================================ */
        .table-wrap {
            overflow-x: auto;
            margin: 1rem 0;
            border-radius: var(--radius-sm);
            border: 1px solid var(--color-gray-200);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }

        table thead {
            background: var(--color-gray-50);
        }

        table th {
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            color: var(--color-gray-700);
            border-bottom: 2px solid var(--color-gray-200);
        }

        table td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--color-gray-100);
            color: var(--color-gray-600);
        }

        table tr:last-child td {
            border-bottom: none;
        }

        table .tag {
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: var(--radius-sm);
            font-size: 0.625rem;
            font-weight: 600;
        }

        .tag-frontend {
            background: #dbeafe;
            color: #1e40af;
        }

        .tag-backend {
            background: #d1fae5;
            color: #065f46;
        }

        .tag-db {
            background: #fef3c7;
            color: #92400e;
        }

        .tag-tools {
            background: #f3e8ff;
            color: #6d28d9;
        }

        .tag-other {
            background: #fce4ec;
            color: #b71c1c;
        }

        /* ============================================
           СТРУКТУРА ПРОЄКТУ
           ============================================ */
        .tree {
            background: var(--color-gray-900);
            border-radius: var(--radius-sm);
            padding: 1.25rem;
            margin: 1rem 0;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: #e2e8f0;
            line-height: 1.8;
            overflow-x: auto;
        }

        .tree .folder {
            color: #60a5fa;
        }

        .tree .file {
            color: #fbbf24;
        }

        .tree .comment {
            color: #64748b;
        }

        /* ============================================
           КНОПКА ВГОРУ
           ============================================ */
        .btn-top {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--color-primary-gradient);
            color: var(--color-white);
            border: none;
            box-shadow: var(--shadow-lg);
            cursor: pointer;
            font-size: 1.25rem;
            transition: all var(--transition);
            opacity: 0;
            visibility: hidden;
            transform: translateY(10px);
            z-index: 999;
        }

        .btn-top.visible {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .btn-top:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-xl);
        }

        /* ============================================
           FOOTER
           ============================================ */
        .footer {
            background: var(--color-secondary);
            color: rgba(255,255,255,0.4);
            padding: 2rem 0;
            margin-top: 2rem;
            border-top: 1px solid rgba(255,255,255,0.05);
        }

        .footer .container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .footer a {
            color: rgba(255,255,255,0.5);
            text-decoration: none;
            transition: color var(--transition);
        }

        .footer a:hover {
            color: var(--color-white);
        }

        .footer .links {
            display: flex;
            gap: 1.5rem;
            font-size: 0.875rem;
        }

        .footer .copy {
            font-size: 0.75rem;
        }

        /* ============================================
           АДАПТИВ
           ============================================ */
        @media (max-width: 768px) {
            .hero-readme h1 {
                font-size: 1.75rem;
            }

            .hero-readme .meta {
                flex-direction: column;
                gap: 0.5rem;
            }

            .toc ul {
                grid-template-columns: 1fr;
            }

            .cards-grid {
                grid-template-columns: 1fr;
            }

            .nav-links {
                display: none;
            }

            .section-header {
                flex-wrap: wrap;
            }

            .section-header .badge {
                margin-left: 0;
            }

            .footer .container {
                flex-direction: column;
                text-align: center;
            }

            .btn-top {
                bottom: 1rem;
                right: 1rem;
                width: 40px;
                height: 40px;
                font-size: 1rem;
            }
        }

        @media (max-width: 480px) {
            .hero-readme {
                padding: 2rem 0;
            }

            .hero-readme h1 {
                font-size: 1.5rem;
            }

            .code-block {
                padding: 0.75rem;
                font-size: 0.7rem;
            }

            .code-block code {
                font-size: 0.7rem;
            }
        }
    </style>
</head>
<body>

<!-- ===== HEADER ===== -->
<header class="header">
    <div class="container">
        <nav class="navbar">
            <a href="index.html" class="logo">
                <span class="logo-icon">✈️</span>
                <span class="logo-text">Fly<span>Booking</span></span>
            </a>

            <ul class="nav-links">
                <li><a href="index.html"><i class="fas fa-home"></i> Головна</a></li>
                <li><a href="#" class="active"><i class="fas fa-book"></i> README</a></li>
                <li><span class="badge-version">v1.0.0</span></li>
            </ul>
        </nav>
    </div>
</header>

<!-- ===== HERO ===== -->
<section class="hero-readme">
    <div class="container">
        <h1>📖 README</h1>
        <p class="subtitle">FlyBooking — сервіс пошуку та бронювання авіаквитків</p>
        <div class="meta">
            <span><i class="fas fa-calendar-alt"></i> 07.07.2026</span>
            <span><i class="fas fa-code-branch"></i> Версія 1.0.0</span>
            <span><i class="fas fa-user"></i> Автор: FlyBooking Team</span>
            <span><i class="fas fa-shield-alt"></i> Ліцензія: MIT</span>
        </div>
    </div>
</section>

<!-- ===== MAIN CONTENT ===== -->
<main class="content">
    <div class="container">

        <!-- ===== ЗМІСТ ===== -->
        <div class="toc">
            <h2>📑 Зміст</h2>
            <ul>
                <li><a href="#about">Про проєкт</a></li>
                <li><a href="#features">Функціонал</a></li>
                <li><a href="#tech">Технології</a></li>
                <li><a href="#structure">Структура проєкту</a></li>
                <li><a href="#installation">Встановлення та запуск</a></li>
                <li><a href="#auth">Тестові дані</a></li>
                <li><a href="#pages">Сторінки</a></li>
                <li><a href="#api">API Ендпоінти</a></li>
                <li><a href="#team">Команда</a></li>
                <li><a href="#license">Ліцензія</a></li>
            </ul>
        </div>

        <!-- ===== 1. ПРО ПРОЄКТ ===== -->
        <section class="section" id="about">
            <div class="section-header">
                <div class="icon"><i class="fas fa-info-circle"></i></div>
                <h2>Про проєкт</h2>
                <span class="badge badge-core">Core</span>
            </div>

            <p>
                <strong>FlyBooking</strong> — це повнофункціональний веб-сервіс для пошуку, бронювання та оплати авіаквитків.
                Проєкт демонструє сучасний підхід до розробки веб-додатків з використанням чистого HTML, CSS та JavaScript
                з імітацією роботи бекенду через LocalStorage.
            </p>

            <p>
                <strong>Мета проєкту:</strong> створити зручний та інтуїтивно зрозумілий інтерфейс для користувачів,
                які шукають авіаквитки, з можливістю реєстрації, входу, перегляду профілю та управління бронюваннями.
            </p>

            <div class="cards-grid">
                <div class="card-mini">
                    <div class="card-icon">🎯</div>
                    <h4>Головна мета</h4>
                    <p>Створення зручного сервісу для пошуку та бронювання авіаквитків</p>
                </div>
                <div class="card-mini">
                    <div class="card-icon">👥</div>
                    <h4>Цільова аудиторія</h4>
                    <p>Мандрівники, туристи, бізнес-клієнти, які шукають авіаквитки онлайн</p>
                </div>
                <div class="card-mini">
                    <div class="card-icon">💡</div>
                    <h4>Ключова цінність</h4>
                    <p>Швидкий пошук, зручне бронювання, безпечна оплата та бонусна система</p>
                </div>
            </div>
        </section>

        <!-- ===== 2. ФУНКЦІОНАЛ ===== -->
        <section class="section" id="features">
            <div class="section-header">
                <div class="icon"><i class="fas fa-list-check"></i></div>
                <h2>Функціонал</h2>
                <span class="badge badge-feature">Features</span>
            </div>

            <div class="cards-grid">
                <div class="card-mini">
                    <div class="card-icon">🔍</div>
                    <h4>Пошук рейсів</h4>
                    <p>Пошук за напрямками, датами, кількістю пасажирів та класом обслуговування</p>
                </div>
                <div class="card-mini">
                    <div class="card-icon">✈️</div>
                    <h4>Спецпропозиції</h4>
                    <p>Відображення акційних пропозицій зі знижками на популярні напрямки</p>
                </div>
                <div class="card-mini">
                    <div class="card-icon">👤</div>
                    <h4>Профіль користувача</h4>
                    <p>Реєстрація, вхід, редагування даних, перегляд історії бронювань</p>
                </div>
                <div class="card-mini">
                    <div class="card-icon">🎁</div>
                    <h4>Бонусна система</h4>
                    <p>Нарахування бонусних балів за кожну подорож, рівні користувачів</p>
                </div>
                <div class="card-mini">
                    <div class="card-icon">📋</div>
                    <h4>Історія бронювань</h4>
                    <p>Всі бронювання в одному місці з фільтрацією за статусом та пошуком</p>
                </div>
                <div class="card-mini">
                    <div class="card-icon">⚙️</div>
                    <h4>Налаштування</h4>
                    <p>Керування сповіщеннями, безпекою, конфіденційністю та акаунтом</p>
                </div>
            </div>
        </section>

        <!-- ===== 3. ТЕХНОЛОГІЇ ===== -->
        <section class="section" id="tech">
            <div class="section-header">
                <div class="icon"><i class="fas fa-microchip"></i></div>
                <h2>Технології</h2>
                <span class="badge badge-core">Stack</span>
            </div>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Компонент</th>
                            <th>Технологія</th>
                            <th>Призначення</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="tag tag-frontend">Frontend</span></td>
                            <td><strong>HTML5</strong></td>
                            <td>Структура сторінок</td>
                        </tr>
                        <tr>
                            <td><span class="tag tag-frontend">Frontend</span></td>
                            <td><strong>CSS3</strong></td>
                            <td>Стилізація, анімації, адаптивність</td>
                        </tr>
                        <tr>
                            <td><span class="tag tag-frontend">Frontend</span></td>
                            <td><strong>JavaScript (Vanilla)</strong></td>
                            <td>Інтерактивність, логіка, модальні вікна</td>
                        </tr>
                        <tr>
                            <td><span class="tag tag-frontend">Frontend</span></td>
                            <td><strong>Font Awesome 6</strong></td>
                            <td>Іконки та векторна графіка</td>
                        </tr>
                        <tr>
                            <td><span class="tag tag-frontend">Frontend</span></td>
                            <td><strong>Google Fonts</strong></td>
                            <td>Шрифти (Inter, Poppins, JetBrains Mono)</td>
                        </tr>
                        <tr>
                            <td><span class="tag tag-backend">Backend</span></td>
                            <td><strong>LocalStorage</strong></td>
                            <td>Зберігання даних користувача (імітація БД)</td>
                        </tr>
                        <tr>
                            <td><span class="tag tag-tools">Tools</span></td>
                            <td><strong>Git</strong></td>
                            <td>Контроль версій</td>
                        </tr>
                        <tr>
                            <td><span class="tag tag-tools">Tools</span></td>
                            <td><strong>VS Code</strong></td>
                            <td>Редактор коду</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- ===== 4. СТРУКТУРА ПРОЄКТУ ===== -->
        <section class="section" id="structure">
            <div class="section-header">
                <div class="icon"><i class="fas fa-folder-tree"></i></div>
                <h2>Структура проєкту</h2>
                <span class="badge badge-core">Structure</span>
            </div>

            <div class="tree">
                <pre>📁 flybooking/
├── <span class="folder">📄 index.html</span>          <span class="comment"># Головна сторінка з пошуком</span>
├── <span class="folder">📄 profile.html</span>         <span class="comment"># Сторінка профілю користувача</span>
├── <span class="folder">📄 README.html</span>          <span class="comment"># Документація проєкту (цей файл)</span>
├── <span class="folder">📁 docs/</span>                 <span class="comment"># Додаткова документація</span>
│   ├── <span class="file">📄 requirements.md</span>     <span class="comment"># Технічні вимоги</span>
│   ├── <span class="file">📄 api.md</span>             <span class="comment"># API документація</span>
│   ├── <span class="file">📄 database-schema.md</span> <span class="comment"># Схема бази даних</span>
│   └── <span class="file">📄 use-case-diagram.md</span> <span class="comment"># Діаграма варіантів використання</span>
└── <span class="folder">📁 assets/</span>              <span class="comment"># Зображення, іконки, шрифти</span>
    └── <span class="file">🖼️ favicon.ico</span>         <span class="comment"># Іконка сайту</span></pre>
            </div>

            <p>
                <strong>Примітка:</strong> Всі сторінки є самостійними HTML-файлами, які працюють без сервера.
                Для зберігання даних використовується <code>localStorage</code> браузера.
            </p>
        </section>

        <!-- ===== 5. ВСТАНОВЛЕННЯ ТА ЗАПУСК ===== -->
        <section class="section" id="installation">
            <div class="section-header">
                <div class="icon"><i class="fas fa-rocket"></i></div>
                <h2>Встановлення та запуск</h2>
                <span class="badge badge-new">Quick Start</span>
            </div>

            <p><strong>Мінімальні вимоги:</strong></p>
            <ul>
                <li>Будь-який сучасний браузер (Chrome, Firefox, Edge, Safari)</li>
                <li>Текстовий редактор (VS Code, Sublime Text, Notepad++)</li>
                <li>Базове розуміння HTML, CSS, JavaScript</li>
            </ul>

            <p><strong>Кроки для запуску:</strong></p>
            <ol>
                <li><strong>Завантажте проєкт</strong> — скачайте всі файли в одну папку</li>
                <li><strong>Відкрийте <code>index.html</code></strong> — двічі клікніть на файл або відкрийте його в браузері</li>
                <li><strong>Використовуйте</strong> — навігація по сторінках, реєстрація, вхід, пошук</li>
            </ol>

            <div class="code-block">
                <span class="lang">BASH</span>
                <code><span class="comment"># Клонування репозиторію (якщо використовуєте Git)</span>
git clone https://github.com/your-username/flybooking.git
cd flybooking

<span class="comment"># Або просто скачайте ZIP-архів та розпакуйте</span>

<span class="comment"># Відкрийте index.html у браузері</span>
open index.html          <span class="comment"># macOS</span>
start index.html         <span class="comment"># Windows</span>
xdg-open index.html      <span class="comment"># Linux</span></code>
            </div>

            <p><strong>Альтернативний спосіб (з Live Server):</strong></p>
            <div class="code-block">
                <span class="lang">VS CODE</span>
                <code><span class="comment"># Встановіть розширення "Live Server" у VS Code</span>
<span class="comment"># Натисніть кнопку "Go Live" в правому нижньому кутку</span>
<span class="comment"># Або натисніть Alt+L, Alt+O</span></code>
            </div>
        </section>

        <!-- ===== 6. ТЕСТОВІ ДАНІ ===== -->
        <section class="section" id="auth">
            <div class="section-header">
                <div class="icon"><i class="fas fa-key"></i></div>
                <h2>Тестові дані</h2>
                <span class="badge badge-feature">Demo</span>
            </div>

            <p>Для швидкого доступу до всіх функцій використовуйте тестові дані:</p>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Поле</th>
                            <th>Значення</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Email</strong></td>
                            <td><code>demo@flybooking.com</code></td>
                        </tr>
                        <tr>
                            <td><strong>Пароль</strong></td>
                            <td><code>password123</code></td>
                        </tr>
                        <tr>
                            <td><strong>Ім'я</strong></td>
                            <td>Олена</td>
                        </tr>
                        <tr>
                            <td><strong>Прізвище</strong></td>
                            <td>Коваленко</td>
                        </
