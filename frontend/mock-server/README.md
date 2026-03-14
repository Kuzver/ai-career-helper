# Mock auth server

Небольшой Express-сервер, который имитирует конечные точки из Postman-коллекции.

## Запуск

```bash
cd mock-server
pnpm install
pnpm dev
```

По умолчанию сервер поднимается на `http://localhost:4000`. При необходимости порт можно
переопределить переменной окружения `MOCK_AUTH_PORT`.

## Маршруты

- `POST /api/login` — ожидает `{ applicationId, loginId, password }` и возвращает моковый
  токен + данные пользователя при успешной проверке.
- `POST /api/user/registration` — ожидает структуру из Postman (`user.email`, `user.password`,
  `registration.applicationId`), добавляет пользователя в `users.json` и выдаёт токен.

## Данные

Все пользователи лежат в `users.json`. Файл перезаписывается при каждой регистрации,
поэтому его можно редактировать вручную, чтобы быстро подготовить входные данные.
