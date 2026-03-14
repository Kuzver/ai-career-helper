# AI Career Helper Frontend

Фронтенд-приложение на React Router + Vite с модульной структурой. Ниже — как запустить проект, краткая архитектура и ссылки на примеры запросов данных.

## Запуск проекта

### 1) Установить Node.js и pnpm

- Node.js: используйте актуальную LTS-версию.
- pnpm: удобнее всего через Corepack (входит в Node.js).

```bash
corepack enable
corepack prepare pnpm@latest --activate
```

Проверить версии:

```bash
node -v
pnpm -v
```

### 2) Установить зависимости

```bash
pnpm install
```

### 3) Переменные окружения

Файл `.env` нужно создать в репозитории. Пример содержания:

```
VITE_AUTH_API_BASE_URL=http://localhost:4000/api/
VITE_AUTH_APP_ID=3326168f-5238-405b-aad3-eb8b1f9872bd
VITE_API_BASE_URL=http://localhost:8000
```

### 4) Запуск в dev-режиме

```bash
pnpm dev
```

Приложение будет доступно на `http://localhost:5173`.

### 5) Сборка и запуск production

```bash
pnpm build
pnpm start
```

## Архитектура (кратко)

- `app/pages` — страницы и маршруты. Каждая страница обычно экспортирует `clientLoader`/`clientAction` и UI.
- `app/modules` — бизнес-модули по доменам (chat, auth, knowledge-base). Внутри чаще всего есть `api`, `model`, `ui`.
- `app/shared` — переиспользуемые компоненты и инфраструктура: UI-kit, клиенты запросов, конфиг окружения.

## Примеры получения данных (GET/POST)

GET и POST запросы реализованы через axios-клиент:

- Клиент: `app/shared/api/axios-client.ts`
- API-методы чатов: `app/modules/chat/api/chats.ts`

Примеры на странице чатов:

- GET: `app/pages/chat.tsx` — `clientLoader` вызывает `getChats` и `getChatById`.
- POST: `app/pages/chat.tsx` — `clientAction` вызывает `createChat`.

Соответствующие запросы внутри API-слоя:

- GET `/api/chats/all` и `/api/chats/:id` в `app/modules/chat/api/chats.ts`
- POST `/api/chats` в `app/modules/chat/api/chats.ts`

## UI и shadcn

В проекте используется набор компонентов shadcn/ui. Базовые компоненты находятся в `app/shared/components/ui`, а их стили и утилиты подключены через Tailwind CSS.

Пример команды для добавления компонента через pnpm:

```bash
pnpm dlx shadcn@latest add button
```
