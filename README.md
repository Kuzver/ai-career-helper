# ИИ-ассистент — Карьерный помощник

Веб-приложение с ИИ-ассистентом для помощи в карьере и обучении в IT. Бот помогает составлять резюме, готовиться к собеседованиям, строить учебные планы и roadmap. Отклоняет вопросы не по теме.

**Стек:** Python 3.11 + FastAPI | React 19 + TypeScript + Vite | PostgreSQL | Redis | GigaChat API

---

## Возможности

- **Чат с ИИ** — карьерный и обучающий ассистент на базе GigaChat, контекст пользователя подгружается автоматически
- **Загрузка файлов** — PDF, DOCX, MD через кнопку или drag & drop, бот анализирует содержимое
- **Экспорт ответов** — скачивание ответов бота в MD, DOCX или HTML
- **Управление чатами** — список в сайдбаре, переименование (ПКМ), удаление, авто-именование через GigaChat
- **Профиль** — специализация, навыки, опыт, карьерная цель — хранятся в БД, подгружаются боту в контекст
- **Опросы** — обязательные и дополнительные, валидация ответов через GigaChat, результаты в контексте бота
- **База знаний** — статьи с категориями, фильтрация по специализации, markdown-рендеринг
- **Дорожная карта** — персонализированный roadmap по специализации, прогресс в БД, видим боту
- **Админка** — управление опросами (`/admin/surveys`) и статьями (`/admin/articles`) для пользователей с ролью `admin`
- **Поиск** — глобальный поиск по чатам и статьям в хедере
- **Адаптивность** — мобильный сайдбар, skeleton loaders
- **Безопасность** — rate limiting (60 req/min), санитизация markdown (XSS), JWT авторизация

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
git clone https://github.com/Kuzver/ai-career-helper.git
cd ai-career-helper
```

> Если у тебя нет доступа к репозиторию, попроси владельца добавить тебя как коллаборатора на GitHub.

---

### Шаг 2. Настрой конфиг бэкенда

Бэкенд читает настройки из файла `config.toml`. Этот файл не хранится в git (там секретные ключи), поэтому его нужно создать из примера.

```bash
cp backend/deploy/configs/exemple.config.toml backend/deploy/configs/config.toml
```

> **Что делает эта команда:** копирует файл-пример `exemple.config.toml` в `config.toml`. В примере уже прописаны рабочие ключи GigaChat.

Если команда `cp` не работает (бывает в PowerShell), используй:
```powershell
copy backend\deploy\configs\exemple.config.toml backend\deploy\configs\config.toml
```

**Важно:** после копирования откройте `config.toml` и замените JWT-секрет:

```toml
[jwt]
secret = "ваш-случайный-секрет-минимум-32-символа"
expire_days = 7
```

Сгенерировать секрет можно командой:
```bash
openssl rand -hex 32
```

> Если не поменять секрет — приложение будет работать, но в логах бэкенда появится предупреждение.

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

Миграции создают таблицы в базе данных. Без этого шага регистрация и всё остальное **не будет работать**.

```bash
docker exec deploy-backend-1 alembic upgrade head
```

> **Что делает:** заходит внутрь контейнера бэкенда и применяет все миграции. Должно вывести несколько строк вроде `Running upgrade ... -> ...` и закончиться без ошибок.

**Текущие миграции создают таблицы:**
- `users`, `chats`, `messages` — пользователи и чаты
- `user_careers` — профиль пользователя
- `surveys`, `survey_questions`, `survey_options`, `survey_responses`, `survey_answers` — опросы
- `article_categories`, `articles` — база знаний
- `user_roadmap_progress`, `user_roadmaps` — дорожная карта и прогресс

После миграций заполни начальные данные (аккаунт администратора, опросы, статьи):

```bash
docker exec deploy-backend-1 python -m src.infra.postgres.seed
```

> Должно вывести `Seed data applied successfully!`

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
5. Если есть обязательные опросы — заполни их (тебя перенаправит автоматически)
6. Готово! Тебя перекинет в чат с ИИ-ассистентом

---

### Шаг 8. Аккаунт администратора

При первом запуске seed автоматически создаёт аккаунт администратора:

| Поле | Значение |
|------|----------|
| Email | `admin@career-helper.ru` |
| Пароль | `Admin123!` |
| Роль | `admin` |

> **Рекомендуется сменить пароль** после первого входа через страницу профиля.

Админ-панель доступна после входа:
- http://localhost:5173/admin/surveys — управление опросами
- http://localhost:5173/admin/articles — управление статьями
- http://localhost:5173/admin/users — управление пользователями и ролями

Для назначения роли другому пользователю используйте `/admin/users`.

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

### "429 Too Many Requests"

Сработал rate limiter (60 запросов в минуту на IP). Подожди минуту и повтори.

---

## Структура проекта

```
ai-career-helper/
├── backend/                        # Серверная часть (Python 3.11)
│   ├── src/
│   │   ├── main/                   # Точка входа, конфиг, DI-контейнер
│   │   ├── presentation/           # API эндпоинты
│   │   │   └── fastapi/routes/
│   │   │       ├── auth/           #   /api/auth — регистрация, вход
│   │   │       ├── admin/          #   /api/admin — опросы, статьи (admin only)
│   │   │       └── core/           #   /api — чаты, сообщения, профиль, опросы, статьи, поиск, экспорт, roadmap
│   │   ├── usecase/                # Бизнес-логика
│   │   │   ├── chats/              #   создание, удаление, переименование, авто-именование
│   │   │   ├── message/            #   отправка сообщений, контекст бота
│   │   │   └── profile/            #   получение/обновление профиля
│   │   ├── infra/                  # Инфраструктура
│   │   │   ├── postgres/           #   ORM-модели, миграции, гейтвеи
│   │   │   ├── gigachat/           #   клиент GigaChat, агенты (career, learning, orchestrator)
│   │   │   ├── auth/               #   JWT, хеширование, проверка роли admin
│   │   │   ├── files/              #   парсинг (PDF, DOCX, MD), экспорт (MD, DOCX, HTML)
│   │   │   └── redis/              #   клиент Redis
│   │   └── application/            # Pydantic-схемы, ошибки
│   ├── deploy/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── configs/
│   │       ├── exemple.config.toml # Пример конфига (в git)
│   │       └── config.toml         # Рабочий конфиг (НЕ в git)
│   └── pyproject.toml
│
├── frontend/                       # Клиентская часть (React 19 + TypeScript)
│   ├── app/
│   │   ├── pages/                  # Страницы
│   │   │   ├── chat.tsx            #   чат с ботом, загрузка файлов, экспорт
│   │   │   ├── profile.tsx         #   профиль пользователя
│   │   │   ├── roadmap.tsx         #   дорожная карта
│   │   │   ├── survey/             #   список опросов, прохождение
│   │   │   ├── knowledge-base/     #   статьи, страница статьи
│   │   │   ├── admin/              #   админка опросов и статей
│   │   │   └── auth/               #   вход, регистрация
│   │   ├── modules/                # Модули
│   │   │   ├── chat/               #   API чатов, сайдбар чатов
│   │   │   ├── user/               #   контекст, API профиля
│   │   │   ├── survey/             #   API опросов
│   │   │   ├── articles/           #   API статей
│   │   │   └── roadmap/            #   API прогресса
│   │   └── shared/                 # Общие ресурсы
│   │       ├── api/                #   axios-клиент с JWT и 401-interceptor
│   │       └── components/ui/      #   layout, skeleton loaders
│   ├── .env.example
│   └── package.json
│
└── README.md
```

---

## API эндпоинты

### Авторизация
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |

### Чаты и сообщения
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/chats/all` | Список чатов пользователя |
| POST | `/api/chats` | Создать чат |
| GET | `/api/chats/{id}` | Чат с сообщениями |
| PATCH | `/api/chats/{id}` | Переименовать чат |
| DELETE | `/api/chats/{id}` | Удалить чат |
| POST | `/api/messages` | Отправить сообщение (+ файл) |

### Профиль
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/profile` | Получить профиль |
| PUT | `/api/profile` | Обновить профиль |

### Опросы
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/surveys` | Список опросов |
| GET | `/api/surveys/mandatory/pending` | Незавершённые обязательные |
| GET | `/api/surveys/{id}` | Детали опроса |
| POST | `/api/surveys/{id}/submit` | Отправить ответы |

### База знаний
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/articles` | Список статей (?specialization=, ?category=) |
| GET | `/api/articles/categories` | Список категорий |
| GET | `/api/articles/{slug}` | Статья по slug |

### Прочее
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/export` | Экспорт сообщения (md/docx/html) |
| GET | `/api/search?q=` | Поиск по чатам и статьям |
| GET | `/api/roadmap/progress` | Прогресс roadmap |
| POST | `/api/roadmap/progress` | Отметить/снять шаг roadmap |

### Админка (role=admin)
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/admin/surveys` | Создать опрос |
| PUT | `/api/admin/surveys/{id}` | Редактировать опрос |
| DELETE | `/api/admin/surveys/{id}` | Удалить опрос |
| POST | `/api/admin/articles` | Создать статью |
| PUT | `/api/admin/articles/{id}` | Редактировать статью |
| DELETE | `/api/admin/articles/{id}` | Удалить статью |
| POST | `/api/admin/articles/categories` | Создать категорию |
| DELETE | `/api/admin/articles/categories/{id}` | Удалить категорию |

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

# Назначить пользователя администратором
docker exec deploy-database-1 psql -U postgres -d postgres -c "UPDATE db_schema.users SET role='admin' WHERE email='email@example.com';"
```

---

## Ссылки после запуска

| Что                       | URL                        | Логин / Пароль              |
|---------------------------|----------------------------|-----------------------------|
| Фронтенд (сайт)          | http://localhost:5173      | регистрируешься сам         |
| Бэкенд API               | http://localhost:8000      | —                           |
| Swagger (документация API)| http://localhost:8000/docs | —                           |
| pgAdmin (управление БД)  | http://localhost:5050      | `admin@example.co` / `admin`|
| Админка опросов           | http://localhost:5173/admin/surveys | role=admin          |
| Админка статей            | http://localhost:5173/admin/articles | role=admin         |
