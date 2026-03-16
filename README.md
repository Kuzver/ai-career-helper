# ИИ-ассистент — Карьерный помощник

Веб-приложение с ИИ-ассистентом для помощи в карьере и обучении. Бот помогает составлять резюме, готовиться к собеседованиям, строить учебные планы и отвечает на любые вопросы.

## Стек технологий

**Бэкенд:** Python 3.11, FastAPI, SQLAlchemy 2 (async), PostgreSQL, Redis, Dishka (DI), GigaChat API
**Фронтенд:** React 19, React Router 7, Vite 7, Tailwind CSS 4, TypeScript, Axios

---

## Быстрый старт (локальная разработка)

### Предварительные требования

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (включает Docker Compose)
- [Node.js](https://nodejs.org/) версии 20+
- Git

### 1. Клонируйте репозиторий

```bash
git clone <url-репозитория>
cd ai-career-helper
```

### 2. Запустите бэкенд (Docker)

Бэкенд, база данных (PostgreSQL), Redis и pgAdmin запускаются через Docker Compose.

```bash
cd backend

# Создайте конфиг из примера (если ещё не создан)
cp deploy/configs/exemple.config.toml deploy/configs/config.toml

# Запустите все сервисы
docker compose -f deploy/docker-compose.yml up --build -d

# Примените миграции базы данных
docker exec deploy-backend-1 alembic upgrade head
```

После запуска:
- **Backend API:** http://localhost:8000
- **Swagger документация:** http://localhost:8000/docs
- **pgAdmin (управление БД):** http://localhost:5050 (логин: `admin@example.co`, пароль: `admin`)
- **PostgreSQL:** localhost:5433 (user: `postgres`, password: `postgres`)

### 3. Запустите фронтенд

```bash
cd frontend

# Создайте файл переменных окружения
cp .env.example .env

# Установите зависимости
npm install

# Запустите dev-сервер
npm run dev
```

Фронтенд будет доступен по адресу: **http://localhost:5173**

### 4. Откройте в браузере

Перейдите на http://localhost:5173, зарегистрируйтесь и начните общение с ИИ-ассистентом.

---

## Конфигурация

### Бэкенд (`backend/deploy/configs/config.toml`)

```toml
[api]
host = 'localhost'
port = 8000
project_name = 'base'
cors = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]

[database]
host = 'database'      # имя Docker-сервиса, НЕ localhost
port = 5432
username = 'postgres'
password = 'postgres'
database = 'postgres'

[gigachat]
client_id = "ваш_client_id"
scope = "GIGACHAT_API_PERS"
authorization_key = "ваш_ключ_авторизации"
```

> **Важно:** `host = 'database'` — это имя сервиса из docker-compose.yml. Внутри Docker-сети контейнеры обращаются друг к другу по именам сервисов, а не по `localhost`.

### Фронтенд (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_API_BASE_URL=http://localhost:4000/api/
VITE_AUTH_APP_ID=3326168f-5238-405b-aad3-eb8b1f9872bd
```

### GigaChat API

Для работы ИИ-ассистента нужен ключ GigaChat API:
1. Зарегистрируйтесь на https://developers.sber.ru/
2. Создайте проект и получите `client_id` и `authorization_key`
3. Укажите их в `backend/deploy/configs/config.toml`

---

## Структура проекта

```
ai-career-helper/
├── backend/
│   ├── src/
│   │   ├── main/              # Точка входа, конфиг, DI-контейнер
│   │   ├── presentation/      # FastAPI роуты (API endpoints)
│   │   ├── usecase/           # Бизнес-логика
│   │   ├── infra/             # БД, GigaChat, Redis, Auth
│   │   └── application/       # Схемы (Pydantic), ошибки
│   ├── deploy/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── configs/
│   └── pyproject.toml
│
├── frontend/
│   ├── app/
│   │   ├── pages/             # Страницы (чат, профиль, база знаний, авторизация)
│   │   ├── modules/           # Модули (chat, user, auth, knowledge-base)
│   │   └── shared/            # Общие компоненты, API-клиент, утилиты
│   ├── src/
│   │   ├── main.tsx           # Точка входа React
│   │   └── router.tsx         # Маршрутизация
│   ├── public/icons/          # SVG иконки
│   └── package.json
│
└── README.md
```

---

## Полезные команды

### Бэкенд

```bash
# Перезапустить бэкенд после изменений кода
docker compose -f deploy/docker-compose.yml restart backend

# Пересобрать контейнер (если менялся Dockerfile или зависимости)
docker compose -f deploy/docker-compose.yml up --build -d backend

# Посмотреть логи бэкенда
docker logs deploy-backend-1 -f

# Создать новую миграцию БД
docker exec deploy-backend-1 alembic revision --autogenerate -m "описание"

# Применить миграции
docker exec deploy-backend-1 alembic upgrade head

# Откатить последнюю миграцию
docker exec deploy-backend-1 alembic downgrade -1

# Остановить все сервисы
docker compose -f deploy/docker-compose.yml down

# Остановить и удалить данные (volumes)
docker compose -f deploy/docker-compose.yml down -v
```

### Фронтенд

```bash
# Запуск dev-сервера
npm run dev

# Сборка для продакшена
npm run build

# Проверка TypeScript
npx tsc --noEmit
```

---

## Деплой на сервер (продакшен)

### Вариант 1: Docker Compose на сервере

1. Установите Docker и Docker Compose на сервере
2. Клонируйте репозиторий
3. Настройте `backend/deploy/configs/config.toml`:
   - Поменяйте `cors` на домен вашего фронтенда
   - Укажите реальные credentials GigaChat
4. Для фронтенда:
   ```bash
   cd frontend
   cp .env.example .env
   # Отредактируйте .env — укажите URL бэкенда на сервере
   # VITE_API_BASE_URL=https://api.ваш-домен.ru
   npm install && npm run build
   ```
5. Раздавайте `frontend/dist/` через Nginx:

   ```nginx
   server {
       listen 80;
       server_name ваш-домен.ru;

       root /path/to/frontend/dist;
       index index.html;

       # SPA: все маршруты → index.html
       location / {
           try_files $uri $uri/ /index.html;
       }

       # Проксирование API на бэкенд
       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

6. Запустите бэкенд:
   ```bash
   cd backend
   docker compose -f deploy/docker-compose.yml up --build -d
   docker exec deploy-backend-1 alembic upgrade head
   ```

### Вариант 2: Отдельные серверы

- **Бэкенд:** разверните Docker Compose на отдельном сервере
- **Фронтенд:** соберите через `npm run build` и выложите на CDN/хостинг статики (Vercel, Netlify, S3)
- **БД:** используйте managed PostgreSQL (Supabase, Railway, AWS RDS)

---

## Решение проблем

| Проблема | Решение |
|----------|---------|
| CORS ошибки | Добавьте URL фронтенда в `config.toml` → `cors` |
| Бэкенд не стартует | Проверьте логи: `docker logs deploy-backend-1` |
| Миграции не проходят | Убедитесь что PostgreSQL запущен: `docker ps` |
| GigaChat не отвечает | Проверьте `authorization_key` в config.toml, а также доступ к API из Docker |
| Фронтенд не видит бэкенд | Проверьте `VITE_API_BASE_URL` в `.env` и CORS настройки |
