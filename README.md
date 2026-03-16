# ИИ-ассистент — Карьерный помощник

Веб-приложение с ИИ-ассистентом для помощи в карьере и обучении. Бот помогает составлять резюме, готовиться к собеседованиям, строить учебные планы и отвечает на любые вопросы.

**Стек:** Python 3.11 + FastAPI | React 19 + TypeScript + Vite | PostgreSQL | Redis | GigaChat API

---

## Установка с нуля (пошаговая инструкция)

### Шаг 0. Что нужно установить на компьютер

Перед тем как начать, убедись что на компьютере установлены три программы:

#### 1) Docker Desktop

Docker — это программа, которая запускает бэкенд, базу данных и всё остальное в контейнерах (как маленькие виртуальные машины).

- Скачай и установи: https://www.docker.com/products/docker-desktop/
- **Windows:** при установке поставь галочку "Use WSL 2" если спросит
- После установки **перезагрузи компьютер**
- Открой Docker Desktop и дождись пока он полностью запустится (иконка кита в трее перестанет анимироваться)

**Как проверить что Docker работает:** открой терминал и напиши:
```bash
docker --version
```
Должно показать что-то вроде `Docker version 27.x.x` — значит всё ок.

#### 2) Node.js (версия 20 или новее)

Node.js нужен для запуска фронтенда (интерфейса сайта).

- Скачай **LTS-версию** (зелёная кнопка): https://nodejs.org/
- Установи, ничего не меняя в настройках (просто жми "Next")

**Как проверить:**
```bash
node --version
```
Должно показать `v20.x.x` или выше.

#### 3) Git

Git нужен чтобы скачать код проекта.

- Скачай: https://git-scm.com/downloads
- Установи с настройками по умолчанию

**Как проверить:**
```bash
git --version
```

---

### Шаг 1. Скачай проект

Открой терминал (Terminal, PowerShell, Git Bash — любой) и выполни:

```bash
git clone https://github.com/dkutugin3/ai-career-helper.git
cd ai-career-helper
```

> Если у тебя нет доступа к репозиторию, попроси владельца добавить тебя как коллаборатора на GitHub.

---

### Шаг 2. Настрой конфиг бэкенда

Бэкенд читает настройки из файла `config.toml`. Этот файл не хранится в git (там секретные ключи), поэтому его нужно создать из примера.

```bash
cp backend/deploy/configs/exemple.config.toml backend/deploy/configs/config.toml
```

> **Что делает эта команда:** копирует файл-пример `exemple.config.toml` в `config.toml`. В примере уже прописаны рабочие ключи GigaChat, так что больше ничего менять не нужно.

Если команда `cp` не работает (бывает в PowerShell), используй:
```powershell
copy backend\deploy\configs\exemple.config.toml backend\deploy\configs\config.toml
```

---

### Шаг 3. Запусти бэкенд (Docker)

**Убедись что Docker Desktop запущен!** (иконка кита в трее должна быть активной)

```bash
cd backend
docker compose -f deploy/docker-compose.yml up --build -d
```

> **Что происходит:** Docker скачивает нужные образы (Python, PostgreSQL, Redis) и собирает контейнеры. Первый раз это может занять **5-10 минут** — это нормально, он качает ~2 ГБ данных. Потом будет быстрее.

**Как проверить что всё запустилось:**
```bash
docker ps
```

Должно показать **4 контейнера** со статусом `Up`:
- `deploy-backend-1` — бэкенд (API)
- `deploy-database-1` — база данных PostgreSQL
- `deploy-redis-1` — кэш Redis
- `deploy-pgadmin-1` — панель управления БД (необязательная)

Если какой-то контейнер не запустился или упал, посмотри логи:
```bash
docker logs deploy-backend-1
```

---

### Шаг 4. Примени миграции базы данных

Миграции создают таблицы в базе данных (пользователи, чаты, сообщения и т.д.). Без этого шага регистрация и всё остальное **не будет работать**.

```bash
docker exec deploy-backend-1 alembic upgrade head
```

> **Что делает:** заходит внутрь контейнера бэкенда и применяет все миграции. Должно вывести несколько строк вроде `Running upgrade ... -> ...` и закончиться без ошибок.

**Если видишь ошибку "No such container":**
Имя контейнера может отличаться. Проверь точное имя:
```bash
docker ps --format "{{.Names}}"
```
И используй нужное имя вместо `deploy-backend-1`.

**Если видишь ошибку подключения к БД:**
Подожди 10-15 секунд после `docker compose up` — база данных ещё стартует. Потом попробуй снова.

---

### Шаг 5. Проверь что бэкенд работает

Открой в браузере: http://localhost:8000/docs

Должна открыться страница **Swagger UI** — это документация API. Если она открылась, бэкенд работает.

---

### Шаг 6. Настрой и запусти фронтенд

Вернись в корень проекта и перейди в папку фронтенда:

```bash
cd ../frontend
```

Создай файл настроек `.env`:

```bash
cp .env.example .env
```

(Или в PowerShell: `copy .env.example .env`)

Установи зависимости:

```bash
npm install
```

> Это скачает все библиотеки (~200 МБ). Займёт 1-3 минуты.

Запусти фронтенд:

```bash
npm run dev
```

В терминале появится что-то вроде:

```
  VITE v7.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
```

---

### Шаг 7. Открой сайт и зарегистрируйся

1. Открой в браузере: **http://localhost:5173**
2. Нажми "Регистрация" (или перейди на http://localhost:5173/sign-up)
3. Введи email, пароль (минимум 8 символов), подтверди пароль
4. Нажми "Зарегистрироваться"
5. Готово! Тебя перекинет в чат с ИИ-ассистентом

---

## Как остановить и снова запустить

### Остановить всё

Фронтенд: просто нажми `Ctrl + C` в терминале где запущен `npm run dev`.

Бэкенд:
```bash
cd backend
docker compose -f deploy/docker-compose.yml down
```

### Запустить снова (после первой установки)

1. Открой Docker Desktop
2. Запусти бэкенд:
   ```bash
   cd backend
   docker compose -f deploy/docker-compose.yml up -d
   ```
   (без `--build` — он уже собран, запустится за секунды)
3. Запусти фронтенд:
   ```bash
   cd frontend
   npm run dev
   ```
4. Открой http://localhost:5173

---

## Частые проблемы и решения

### "Не могу зарегистрироваться" / "Ошибка при регистрации"

1. **Бэкенд вообще запущен?** Открой http://localhost:8000/docs — если не открывается, бэкенд не работает. Запусти контейнеры.
2. **Миграции применены?** Без миграций таблицы в БД не существуют. Выполни:
   ```bash
   docker exec deploy-backend-1 alembic upgrade head
   ```
3. **Посмотри логи бэкенда:**
   ```bash
   docker logs deploy-backend-1 --tail 50
   ```
   Там будет написано в чём ошибка.

### "CORS error" в консоли браузера

Фронтенд не может достучаться до бэкенда. Убедись что:
- Бэкенд запущен на порту 8000
- Фронтенд запущен на порту 5173
- В `backend/deploy/configs/config.toml` в разделе `[api]` есть `cors = ["http://localhost:5173"]`

### Docker пишет "Cannot connect to the Docker daemon"

Docker Desktop не запущен. Открой Docker Desktop и подожди пока он полностью загрузится.

### "port is already allocated" при запуске Docker

Какой-то из портов (8000, 5432, 5433, 6379) уже занят другой программой.
- Закрой другие проекты, которые используют эти порты
- Или перезагрузи компьютер

### npm install выдаёт ошибки

- Убедись что Node.js версии 20+: `node --version`
- Попробуй удалить `node_modules` и поставить заново:
  ```bash
  rm -rf node_modules
  npm install
  ```
  (В PowerShell: `Remove-Item -Recurse -Force node_modules` вместо `rm -rf`)

### Бэкенд падает сразу после запуска

Посмотри логи:
```bash
docker logs deploy-backend-1
```
Скорее всего проблема в `config.toml` — файл не создан или в нём ошибка. Убедись что файл `backend/deploy/configs/config.toml` существует и скопирован из примера.

### GigaChat не отвечает / ошибка в чате

Ключи GigaChat могут быть просрочены. Для получения своих ключей:
1. Зарегистрируйся на https://developers.sber.ru/
2. Создай проект, подключи GigaChat API
3. Скопируй `client_id` и `authorization_key`
4. Обнови их в `backend/deploy/configs/config.toml` в разделе `[gigachat]`

---

## Структура проекта

```
ai-career-helper/
├── backend/                    # Серверная часть (Python)
│   ├── src/
│   │   ├── main/               # Точка входа, конфиг, DI-контейнер
│   │   ├── presentation/       # API эндпоинты (роуты)
│   │   ├── usecase/            # Бизнес-логика
│   │   ├── infra/              # БД, GigaChat, Redis, авторизация
│   │   └── application/        # Схемы (Pydantic), ошибки
│   ├── deploy/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── configs/
│   │       ├── exemple.config.toml   # Пример конфига (в git)
│   │       └── config.toml           # Рабочий конфиг (НЕ в git)
│   └── pyproject.toml
│
├── frontend/                   # Клиентская часть (React)
│   ├── app/
│   │   ├── pages/              # Страницы (чат, профиль, авторизация)
│   │   ├── modules/            # Модули (chat, user, auth)
│   │   └── shared/             # Общие компоненты, API-клиент
│   ├── .env.example            # Пример переменных окружения (в git)
│   ├── .env                    # Рабочие переменные (НЕ в git)
│   └── package.json
│
└── README.md
```

---

## Полезные команды

```bash
# Логи бэкенда (в реальном времени)
docker logs deploy-backend-1 -f

# Перезапустить бэкенд после изменений в коде
docker compose -f deploy/docker-compose.yml restart backend

# Пересобрать бэкенд (если менялись зависимости или Dockerfile)
docker compose -f deploy/docker-compose.yml up --build -d backend

# Применить новые миграции БД
docker exec deploy-backend-1 alembic upgrade head

# Остановить все контейнеры
docker compose -f deploy/docker-compose.yml down

# Остановить и удалить все данные (БД, кэш — начать с чистого листа)
docker compose -f deploy/docker-compose.yml down -v
```

---

## Ссылки после запуска

| Что                       | URL                        | Логин / Пароль              |
|---------------------------|----------------------------|-----------------------------|
| Фронтенд (сайт)          | http://localhost:5173      | регистрируешься сам         |
| Бэкенд API               | http://localhost:8000      | —                           |
| Swagger (документация API)| http://localhost:8000/docs | —                           |
| pgAdmin (управление БД)  | http://localhost:5050      | `admin@example.co` / `admin`|
