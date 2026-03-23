"""
Seed data: категории статей, статьи, обязательный опрос, sender_types.
Запуск: docker exec deploy-backend-1 python -m src.infra.postgres.seed
"""
import asyncio
from uuid import uuid4, UUID
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.main.config import config
from src.infra.auth.jwt import hash_password

ADMIN_ID = UUID("00000000-0000-0000-0000-000000000001")
ADMIN_EMAIL = "admin@career-helper.ru"
ADMIN_PASSWORD = "Admin123!"

CATEGORIES = [
    ("resume", "Резюме и поиск работы", 1),
    ("interview", "Собеседования", 2),
    ("career", "Карьерный рост", 3),
    ("learning", "Обучение и развитие", 4),
    ("soft-skills", "Soft Skills", 5),
]

ARTICLES = [
    {
        "title": "Как составить резюме, которое заметят",
        "slug": "how-to-write-resume",
        "category_slug": "resume",
        "specialization": None,
        "content_md": """## Структура эффективного резюме

### 1. Контактная информация
Имя, email, телефон, город. Ссылки на GitHub/LinkedIn если есть. Не нужно: фото, дата рождения, семейное положение.

### 2. О себе (2-3 предложения)
Кратко: кто вы, что умеете, что ищете. Пример:
> Frontend-разработчик с 2-летним опытом. Специализируюсь на React и TypeScript. Ищу позицию в продуктовой компании.

### 3. Опыт работы (от нового к старому)
Для каждой позиции:
- **Название компании** — должность (даты)
- 3-5 пунктов с конкретными достижениями
- Используйте цифры: «Ускорил загрузку на 40%», «Внедрил CI/CD, сократив время деплоя с 2 часов до 15 минут»

### 4. Навыки
Группируйте: языки, фреймворки, инструменты, базы данных. Не перечисляйте всё подряд — только то, с чем реально работали.

### 5. Образование
Вуз, специальность, год. Курсы и сертификаты — только значимые.

## Частые ошибки
- Резюме на 3+ страницы (идеал — 1 страница)
- Обязанности вместо достижений («Разрабатывал» → «Разработал систему X, которая Y»)
- Нерелевантный опыт (работа кассиром для позиции разработчика)
- Орфографические ошибки — проверяйте!

## Адаптация под вакансию
Каждое резюме должно быть адаптировано. Читайте описание вакансии и подчёркивайте релевантный опыт. ATS-системы ищут ключевые слова из вакансии в вашем резюме.""",
    },
    {
        "title": "Подготовка к техническому собеседованию",
        "slug": "technical-interview-prep",
        "category_slug": "interview",
        "specialization": None,
        "content_md": """## План подготовки

### За 2-4 недели до собеседования

**Алгоритмы и структуры данных:**
- Массивы, строки, хеш-таблицы — решайте по 1-2 задачи в день
- Деревья, графы, динамическое программирование — по мере уровня
- Ресурсы: LeetCode (Easy → Medium), NeetCode 150

**Системный дизайн (для Middle+):**
- Как проектировать URL-shortener, чат, ленту новостей
- Понимание CAP-теоремы, шардирования, кеширования
- Книга: «System Design Interview» by Alex Xu

### За 1 неделю до
- Изучите компанию: продукт, стек, культура
- Подготовьте вопросы к интервьюеру
- Повторите свои проекты — будьте готовы объяснить любое решение

### На собеседовании
1. **Уточните задачу** — не бросайтесь кодить сразу
2. **Обсудите подход** — интервьюер хочет видеть ход мыслей
3. **Пишите чистый код** — именование, структура
4. **Тестируйте** — пройдитесь по edge cases
5. **Оцените сложность** — O(n), O(n log n) и т.д.

## Поведенческие вопросы (STAR-метод)
- **S**ituation — опишите ситуацию
- **T**ask — какая была задача
- **A**ction — что вы сделали
- **R**esult — какой результат

Примеры: конфликт в команде, сложный баг, дедлайн, инициатива.""",
    },
    {
        "title": "Git для начинающих: команды на каждый день",
        "slug": "git-basics",
        "category_slug": "learning",
        "specialization": None,
        "content_md": """## Базовые команды

```bash
git init                    # создать репозиторий
git clone <url>             # склонировать
git status                  # текущее состояние
git add <file>              # добавить в индекс
git add .                   # добавить всё
git commit -m "сообщение"   # зафиксировать изменения
git push                    # отправить на сервер
git pull                    # получить изменения
```

## Ветки

```bash
git branch                  # список веток
git branch feature-x        # создать ветку
git checkout feature-x      # переключиться
git checkout -b feature-x   # создать и переключиться
git merge feature-x         # слить ветку в текущую
git branch -d feature-x     # удалить ветку
```

## Правила хороших коммитов
1. Один коммит = одно логическое изменение
2. Сообщение в повелительном наклонении: «Добавить», «Исправить», «Удалить»
3. Первая строка — до 72 символов
4. Не коммитьте секреты, логи, node_modules

## .gitignore
Создайте в корне проекта:
```
node_modules/
.env
*.log
dist/
.idea/
```

## Полезные команды
```bash
git log --oneline          # компактная история
git diff                   # что изменилось
git stash                  # временно спрятать изменения
git stash pop              # вернуть спрятанное
git reset HEAD~1           # отменить последний коммит (сохранив файлы)
```""",
    },
    {
        "title": "Как расти от Junior до Middle",
        "slug": "junior-to-middle",
        "category_slug": "career",
        "specialization": None,
        "content_md": """## Что отличает Middle от Junior

| Junior | Middle |
|--------|--------|
| Выполняет задачи по инструкции | Самостоятельно декомпозирует задачу |
| Спрашивает «как делать» | Спрашивает «зачем делать» |
| Знает фреймворк | Понимает, как фреймворк работает внутри |
| Пишет код | Пишет поддерживаемый код |
| Фиксит баги | Предотвращает баги |

## Практические шаги

### 1. Углубите знания (3-6 месяцев)
- Прочитайте документацию своего основного фреймворка целиком
- Изучите паттерны проектирования (хотя бы Strategy, Observer, Factory)
- Поймите, как работает HTTP, DNS, TCP/IP на базовом уровне

### 2. Пишите production-код (постоянно)
- Code review — читайте чужой код, учитесь у старших
- Пишите тесты — не для галочки, а для уверенности
- Рефакторите — улучшайте код, который уже работает

### 3. Развивайте soft skills
- Оценка задач — учитесь давать адекватные сроки
- Коммуникация — объясняйте техническое простым языком
- Инициатива — предлагайте улучшения, не ждите указаний

### 4. Создайте значимый проект
Не todo-app, а что-то реальное: инструмент для команды, open-source библиотека, автоматизация процесса.

## Сколько времени занимает переход
Обычно 1-2 года при активной работе. Но дело не во времени, а в качестве опыта.""",
    },
    {
        "title": "React: лучшие практики 2025",
        "slug": "react-best-practices",
        "category_slug": "learning",
        "specialization": "frontend",
        "content_md": """## Структура проекта

```
src/
├── modules/           # фичи (auth, chat, profile)
│   ├── auth/
│   │   ├── api/       # API вызовы
│   │   ├── ui/        # компоненты
│   │   └── model/     # типы, хуки
│   └── ...
├── shared/            # переиспользуемое
│   ├── api/           # axios client
│   ├── ui/            # Button, Input, Modal
│   └── lib/           # утилиты
└── pages/             # роуты
```

## Ключевые принципы

### 1. Компоненты — маленькие и однозадачные
Если компонент > 150 строк — разбейте. Если у него > 3 пропсов — подумайте о композиции.

### 2. Состояние — как можно ниже
Не тяните состояние в глобальный стор без необходимости. `useState` > `useContext` > Zustand/Redux.

### 3. Кастомные хуки для логики
```tsx
// Плохо: логика в компоненте
const [data, setData] = useState(null)
useEffect(() => { fetch('/api/data').then(...) }, [])

// Хорошо: логика в хуке
const { data, loading } = useData()
```

### 4. TypeScript — обязательно
- Типизируйте пропсы, ответы API, состояние
- Используйте `type` для объектов, `interface` для расширяемых контрактов
- `as` — только в крайнем случае

### 5. Обработка ошибок
- Error Boundary для критических ошибок
- try/catch для API-вызовов
- Показывайте пользователю понятные сообщения, не стектрейсы

## Производительность
- `React.memo` — только когда рендер реально дорогой
- `useMemo`/`useCallback` — не везде, а где есть проблема
- Ленивая загрузка роутов: `React.lazy(() => import(...))`""",
    },
    {
        "title": "SQL для разработчика: минимум, который нужно знать",
        "slug": "sql-essentials",
        "category_slug": "learning",
        "specialization": "backend",
        "content_md": """## Базовые запросы

```sql
-- Выборка
SELECT name, email FROM users WHERE is_active = true;

-- Сортировка и лимит
SELECT * FROM articles ORDER BY created_at DESC LIMIT 10;

-- Агрегация
SELECT department, COUNT(*) as cnt, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;
```

## JOIN — объединение таблиц

```sql
-- INNER JOIN — только совпадения
SELECT u.name, o.total
FROM users u
JOIN orders o ON o.user_id = u.id;

-- LEFT JOIN — все из левой + совпадения из правой
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.name;
```

## Индексы
```sql
-- Создать индекс (ускоряет WHERE и JOIN по этому полю)
CREATE INDEX idx_users_email ON users(email);

-- Составной индекс
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);
```

**Когда нужен индекс:**
- Поле часто в WHERE или JOIN
- Поле в ORDER BY
- Уникальные значения (email, username)

**Когда НЕ нужен:**
- Таблица маленькая (< 1000 строк)
- Поле часто обновляется
- Низкая кардинальность (boolean)

## Транзакции
```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- или ROLLBACK если ошибка
```

## Полезные функции PostgreSQL
```sql
COALESCE(value, default)    -- первое не-NULL значение
NOW()                       -- текущее время
uuid_generate_v4()          -- генерация UUID
jsonb_agg(...)              -- агрегация в JSON
```""",
    },
    {
        "title": "Как вести себя на новой работе: первые 90 дней",
        "slug": "first-90-days",
        "category_slug": "soft-skills",
        "specialization": None,
        "content_md": """## Первая неделя: слушайте

- Познакомьтесь с командой — запомните имена и роли
- Изучите внутренние инструменты: Jira/Linear, Slack, Git workflow
- Попросите доступы ко всему заранее — не ждите
- Запустите проект локально — это первый тест на self-sufficiency
- Задавайте вопросы — это показывает заинтересованность, а не слабость

## Первый месяц: маленькие победы

- Возьмите 2-3 простые задачи и сделайте их хорошо
- Пишите код в стиле команды, а не в своём
- Делайте code review — даже если junior, ваш свежий взгляд ценен
- Документируйте то, что нигде не записано (setup, неочевидные процессы)

## Месяцы 2-3: вливайтесь

- Беритесь за задачи сложнее — покажите рост
- Предлагайте улучшения, но аргументируйте
- Участвуйте в обсуждениях — ваше мнение важно
- Попросите фидбек у лида — не ждите ревью

## Чего НЕ делать
- Не критикуйте легаси-код — у него есть причины
- Не переписывайте всё «правильно» без согласования
- Не работайте по 12 часов — это не sustainability
- Не молчите, если что-то непонятно — спрашивайте сразу""",
    },
]

SURVEYS = [
  {
    "title": "Определение вашего профессионального профиля",
    "description": "Этот опрос поможет ИИ-ассистенту лучше понять ваши цели и давать более точные рекомендации. Займёт 2-3 минуты.",
    "is_mandatory": True,
    "questions": [
        {
            "text": "Какая сфера IT вас интересует больше всего?",
            "type": "single",
            "options": [
                "Frontend-разработка (React, Vue, Angular)",
                "Backend-разработка (Python, Java, Go, Node.js)",
                "Fullstack-разработка",
                "Мобильная разработка (iOS/Android)",
                "Data Science / Machine Learning",
                "DevOps / SRE",
                "Тестирование (QA)",
                "Управление проектами (PM)",
                "Ещё не определился",
            ],
        },
        {
            "text": "Какой у вас текущий уровень опыта в IT?",
            "type": "single",
            "options": [
                "Полный новичок — только начинаю изучать",
                "Учусь 3-6 месяцев, знаю основы",
                "Есть пет-проекты, ищу первую работу",
                "Junior — работаю менее года",
                "Middle — работаю 1-3 года",
                "Senior — работаю 3+ лет",
            ],
        },
        {
            "text": "Какая ваша главная цель на ближайшие 6 месяцев?",
            "type": "single",
            "options": [
                "Получить первую работу в IT",
                "Перейти на следующий уровень (Junior → Middle, Middle → Senior)",
                "Сменить специализацию внутри IT",
                "Повысить зарплату на текущей позиции",
                "Освоить новую технологию/фреймворк",
                "Запустить свой проект / стартап",
            ],
        },
        {
            "text": "Сколько времени в неделю вы готовы уделять обучению?",
            "type": "single",
            "options": [
                "Менее 5 часов",
                "5-10 часов",
                "10-20 часов",
                "Более 20 часов (учусь full-time)",
            ],
        },
        {
            "text": "Какие технологии вы уже знаете? (опишите кратко)",
            "type": "text",
            "options": [],
        },
        {
            "text": "Что для вас сейчас самое сложное в карьере/обучении?",
            "type": "single",
            "options": [
                "Не знаю с чего начать",
                "Не хватает практики — много теории, мало реальных проектов",
                "Не могу пройти собеседования",
                "Не могу определиться с направлением",
                "Выгорание / потеря мотивации",
                "Не хватает английского языка",
            ],
        },
    ],
  },
  {
    "title": "Оценка soft skills",
    "description": "Поможет определить ваши сильные и слабые стороны в коммуникации и работе в команде.",
    "is_mandatory": False,
    "questions": [
        {
            "text": "Как вы обычно реагируете на критику вашего кода на code review?",
            "type": "single",
            "options": [
                "Принимаю спокойно, анализирую замечания",
                "Иногда воспринимаю лично, но стараюсь быть объективным",
                "Часто чувствую раздражение, но не показываю",
                "Сразу соглашаюсь со всем, даже если не согласен",
            ],
        },
        {
            "text": "Как часто вы просите помощь у коллег, когда застреваете на задаче?",
            "type": "single",
            "options": [
                "Сразу — не трачу время на то, что можно узнать быстрее",
                "После 30-60 минут самостоятельных попыток",
                "Стараюсь решить сам, спрашиваю только в крайнем случае",
                "Почти никогда — боюсь показаться некомпетентным",
            ],
        },
        {
            "text": "Как вы оцениваете задачи по времени?",
            "type": "single",
            "options": [
                "Обычно попадаю в оценку (±20%)",
                "Часто недооцениваю — задачи занимают больше времени",
                "Часто переоцениваю — заканчиваю раньше",
                "Не умею оценивать, называю случайные числа",
            ],
        },
        {
            "text": "Что бы вы хотели улучшить в коммуникации?",
            "type": "text",
            "options": [],
        },
    ],
  },
  {
    "title": "Стиль обучения",
    "description": "Определим, как вам эффективнее всего учиться, чтобы рекомендации были максимально полезными.",
    "is_mandatory": False,
    "questions": [
        {
            "text": "Какой формат обучения вам подходит лучше всего?",
            "type": "single",
            "options": [
                "Видеокурсы — смотрю и повторяю",
                "Книги и документация — читаю и разбираюсь",
                "Практика — сразу пишу код, разбираюсь по ходу",
                "Менторство — нужен человек, который направит",
                "Микс всего — зависит от темы",
            ],
        },
        {
            "text": "Как вы относитесь к изучению на английском языке?",
            "type": "single",
            "options": [
                "Свободно читаю и смотрю на английском",
                "Читаю нормально, видео сложнее",
                "С трудом, предпочитаю русскоязычные материалы",
                "Вообще не знаю английский",
            ],
        },
        {
            "text": "Как быстро вы теряете мотивацию при изучении нового?",
            "type": "single",
            "options": [
                "Могу учить месяцами без потери мотивации",
                "2-3 недели, потом нужен перерыв или смена темы",
                "Несколько дней — быстро перегораю",
                "Зависит от того, вижу ли я практический результат",
            ],
        },
        {
            "text": "Какую тему вы хотели бы изучить следующей?",
            "type": "text",
            "options": [],
        },
    ],
  },
]


async def seed():
    engine = create_async_engine(config.database.dsn)

    async with AsyncSession(engine) as session:
        # Sender types
        for name in ("user", "chat"):
            exists = await session.execute(
                text(f"SELECT 1 FROM db_schema.sender_types WHERE name = :n"), {"n": name}
            )
            if not exists.scalar():
                await session.execute(
                    text("INSERT INTO db_schema.sender_types (name) VALUES (:n)"), {"n": name}
                )

        # Admin account
        admin_exists = await session.execute(
            text("SELECT 1 FROM db_schema.users WHERE email = :e"), {"e": ADMIN_EMAIL}
        )
        if not admin_exists.scalar():
            await session.execute(text(
                "INSERT INTO db_schema.users (id, email, password_hash, first_name, is_active, role, created_at, updated_at) "
                "VALUES (:id, :email, :pw, 'Admin', true, 'admin', now(), now())"
            ), {"id": str(ADMIN_ID), "email": ADMIN_EMAIL, "pw": hash_password(ADMIN_PASSWORD)})
        else:
            await session.execute(text(
                "UPDATE db_schema.users SET role='admin' WHERE email = :e"
            ), {"e": ADMIN_EMAIL})

        # Categories
        cat_ids = {}
        for slug, name, order in CATEGORIES:
            exists = await session.execute(
                text("SELECT id FROM db_schema.article_categories WHERE slug = :s"), {"s": slug}
            )
            row = exists.fetchone()
            if row:
                cat_ids[slug] = row[0]
            else:
                cid = uuid4()
                await session.execute(text(
                    "INSERT INTO db_schema.article_categories (id, name, slug, \"order\", created_at, updated_at) "
                    "VALUES (:id, :name, :slug, :ord, now(), now())"
                ), {"id": str(cid), "name": name, "slug": slug, "ord": order})
                cat_ids[slug] = cid

        # Articles
        for a in ARTICLES:
            exists = await session.execute(
                text("SELECT 1 FROM db_schema.articles WHERE slug = :s"), {"s": a["slug"]}
            )
            if not exists.scalar():
                cat_id = cat_ids.get(a["category_slug"])
                await session.execute(text(
                    "INSERT INTO db_schema.articles (id, title, slug, content_md, category_id, specialization, created_at, updated_at) "
                    "VALUES (:id, :title, :slug, :content, :cat_id, :spec, now(), now())"
                ), {
                    "id": str(uuid4()), "title": a["title"], "slug": a["slug"],
                    "content": a["content_md"],
                    "cat_id": str(cat_id) if cat_id else None,
                    "spec": a["specialization"],
                })

        # Surveys
        for survey_data in SURVEYS:
            exists = await session.execute(
                text("SELECT 1 FROM db_schema.surveys WHERE title = :t"), {"t": survey_data["title"]}
            )
            if not exists.scalar():
                survey_id = uuid4()
                await session.execute(text(
                    "INSERT INTO db_schema.surveys (id, title, description, is_mandatory, is_active, created_by, created_at, updated_at) "
                    "VALUES (:id, :title, :desc, :mand, true, :admin, now(), now())"
                ), {
                    "id": str(survey_id), "title": survey_data["title"],
                    "desc": survey_data["description"], "mand": survey_data["is_mandatory"],
                    "admin": str(ADMIN_ID),
                })

                for qi, q in enumerate(survey_data["questions"]):
                    q_id = uuid4()
                    await session.execute(text(
                        "INSERT INTO db_schema.survey_questions (id, survey_id, text, question_type, \"order\", created_at, updated_at) "
                        "VALUES (:id, :sid, :text, :type, :ord, now(), now())"
                    ), {
                        "id": str(q_id), "sid": str(survey_id),
                        "text": q["text"], "type": q["type"], "ord": qi,
                    })

                    for oi, opt in enumerate(q["options"]):
                        await session.execute(text(
                            "INSERT INTO db_schema.survey_options (id, question_id, text, \"order\", created_at, updated_at) "
                            "VALUES (:id, :qid, :text, :ord, now(), now())"
                        ), {
                            "id": str(uuid4()), "qid": str(q_id),
                            "text": opt, "ord": oi,
                        })

        await session.commit()
        print("Seed data applied successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
