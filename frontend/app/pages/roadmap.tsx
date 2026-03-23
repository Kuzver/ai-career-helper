import { useEffect, useRef, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import confetti from "canvas-confetti"
import { useUser } from "~/modules/user/lib/use-user"
import { getProfile } from "~/modules/user/api/profile"
import { getProgress, toggleProgress } from "~/modules/roadmap/api/roadmap"
import { getPendingMandatory } from "~/modules/survey/api/surveys"

type RoadmapStep = {
  id: string
  title: string
  description: string
  details: string
  resources: string[]
  skills: string[]
  duration: string
}

type Roadmap = {
  key: string
  title: string
  description: string
  steps: RoadmapStep[]
}

const ROADMAPS: Record<string, Roadmap> = {
  frontend: {
    key: "frontend",
    title: "Frontend-разработчик",
    description: "Путь от новичка до уверенного фронтенд-разработчика",
    steps: [
      { id: "1", title: "Основы HTML и CSS", description: "Изучите семантическую вёрстку, Flexbox, Grid, адаптивный дизайн и доступность.", details: "Начните с HTML5: семантические теги (header, main, article, section), формы, таблицы. Затем CSS3: селекторы, каскад, специфичность, box model. Освойте Flexbox для одномерных раскладок и Grid для двумерных. Обязательно изучите media queries для адаптивного дизайна. Практика: сверстайте 3-5 макетов с Figma.", resources: ["FreeCodeCamp — HTML/CSS курс", "MDN Web Docs — справочник", "CSS Tricks — Flexbox Guide", "Kevin Powell (YouTube) — CSS"], skills: ["HTML5", "CSS3", "Flexbox", "Grid", "Responsive Design"], duration: "1-2 месяца" },
      { id: "2", title: "JavaScript", description: "Освойте основы языка: переменные, функции, DOM, асинхронность, ES6+ синтаксис.", details: "Изучите типы данных, операторы, циклы, условия. Затем функции (стрелочные, замыкания, колбэки). DOM API: выборка элементов, события, изменение стилей. Асинхронность: промисы, async/await, fetch. ES6+: деструктуризация, spread, template literals, модули. Практика: сделайте Todo-app, калькулятор, мини-игру.", resources: ["JavaScript.info — учебник", "Eloquent JavaScript — книга", "LeetCode Easy — задачи", "Web Dev Simplified (YouTube)"], skills: ["JavaScript", "ES6+", "DOM API", "Fetch API", "Async/Await"], duration: "2-3 месяца" },
      { id: "3", title: "React и экосистема", description: "Изучите компоненты, хуки, роутинг, управление состоянием и работу с API.", details: "Начните с JSX, компонентов, пропсов и состояния (useState). Изучите useEffect для побочных эффектов, useRef, useContext. React Router для навигации. Управление состоянием: начните с Context API, потом Zustand или Redux Toolkit. TypeScript: типизация пропсов, состояния, API-ответов. Практика: создайте полноценное SPA с авторизацией.", resources: ["React docs (react.dev)", "TypeScript Handbook", "React Router docs", "Zustand GitHub — примеры"], skills: ["React", "React Router", "Zustand/Redux", "React Query", "TypeScript"], duration: "2-3 месяца" },
      { id: "4", title: "Инструменты разработки", description: "Git, сборщики, линтеры, тестирование, CI/CD основы.", details: "Git: ветки, merge, rebase, pull requests. Сборщики: Vite (рекомендуется), Webpack (для понимания). Линтеры: ESLint + Prettier. Тестирование: Jest или Vitest для unit-тестов, React Testing Library для компонентов. CI/CD: GitHub Actions для автоматического запуска тестов и деплоя.", resources: ["Pro Git — книга", "Vite docs", "Testing Library docs", "GitHub Actions docs"], skills: ["Git", "Vite/Webpack", "ESLint", "Jest/Vitest", "GitHub Actions"], duration: "1-2 месяца" },
      { id: "5", title: "Продвинутый уровень", description: "Оптимизация, SSR/SSG, архитектура, паттерны проектирования.", details: "Next.js или Remix для SSR/SSG. Оптимизация: React.memo, useMemo, code splitting, lazy loading. Web Vitals: LCP, FID, CLS — инструменты Lighthouse. Архитектура: Feature-Sliced Design, Clean Architecture для фронтенда. Accessibility: ARIA, семантика, keyboard navigation. Практика: open-source вклад или собственная библиотека.", resources: ["Next.js docs", "web.dev — Performance", "Feature-Sliced Design", "A11y Project"], skills: ["Next.js", "Performance", "Web Vitals", "Design Patterns", "Accessibility"], duration: "2-4 месяца" },
    ],
  },
  backend: {
    key: "backend",
    title: "Backend-разработчик",
    description: "Путь от новичка до уверенного бэкенд-разработчика",
    steps: [
      { id: "1", title: "Язык программирования", description: "Выберите Python, Go, Java или Node.js. Изучите основы и стандартную библиотеку.", details: "Рекомендация для начинающих: Python (простой синтаксис, огромное комьюнити). Изучите: типы данных, ООП (классы, наследование, полиморфизм), модули, работу с файлами. Алгоритмы: сортировки, поиск, хеш-таблицы. Структуры данных: списки, стеки, очереди, деревья.", resources: ["Python docs", "LeetCode — алгоритмы", "CS50 (Harvard) — бесплатный курс", "Automate the Boring Stuff — книга"], skills: ["Python/Go/Java", "ООП", "Алгоритмы", "Структуры данных"], duration: "2-3 месяца" },
      { id: "2", title: "Базы данных", description: "SQL и NoSQL базы данных, проектирование схем, оптимизация запросов.", details: "Начните с PostgreSQL: CREATE TABLE, SELECT, JOIN, GROUP BY, индексы. Проектирование: нормализация (1NF-3NF), связи (1:1, 1:N, N:N). ORM: SQLAlchemy (Python) или TypeORM (Node). Redis для кеширования. MongoDB — для понимания NoSQL подхода.", resources: ["PostgreSQL Tutorial", "SQLBolt — интерактивные задачи", "Redis University", "Database Design — Vertabelo Academy"], skills: ["PostgreSQL", "Redis", "MongoDB", "SQL", "ORM"], duration: "1-2 месяца" },
      { id: "3", title: "Web-фреймворки", description: "Изучите REST API, аутентификацию, валидацию, работу с файлами.", details: "Выберите фреймворк: FastAPI (Python, async), Django (Python, batteries-included), Express (Node), Spring Boot (Java). Освойте: REST endpoints, HTTP методы, статус коды, middleware, CORS, JWT авторизация, валидация данных (Pydantic/Zod), загрузка файлов, Swagger/OpenAPI документация.", resources: ["FastAPI docs", "Django REST framework", "Express.js Guide", "REST API Design Best Practices"], skills: ["FastAPI/Django/Spring", "REST API", "JWT", "OpenAPI", "Middleware"], duration: "2-3 месяца" },
      { id: "4", title: "DevOps основы", description: "Контейнеризация, CI/CD, мониторинг, деплой.", details: "Docker: Dockerfile, docker-compose, multi-stage builds. CI/CD: GitHub Actions — тесты при push, деплой при merge. Linux: базовые команды, права, systemd, nginx reverse proxy. Мониторинг: логирование (структурированное), health checks.", resources: ["Docker docs", "GitHub Actions docs", "Linux Journey", "Nginx Beginner Guide"], skills: ["Docker", "Docker Compose", "GitHub Actions", "Nginx", "Linux"], duration: "1-2 месяца" },
      { id: "5", title: "Продвинутый уровень", description: "Микросервисы, очереди сообщений, масштабирование, безопасность.", details: "Микросервисы: когда и зачем, inter-service communication. Очереди: RabbitMQ или Kafka для async processing. Кеширование: стратегии (cache-aside, write-through). Безопасность: OWASP Top 10, SQL injection, XSS, rate limiting. Масштабирование: horizontal scaling, load balancing, database sharding.", resources: ["System Design Primer (GitHub)", "OWASP Top 10", "Kafka docs", "Designing Data-Intensive Applications — книга"], skills: ["Kafka/RabbitMQ", "gRPC", "Kubernetes", "Кеширование", "Security"], duration: "3-6 месяцев" },
    ],
  },
  fullstack: {
    key: "fullstack",
    title: "Fullstack-разработчик",
    description: "Путь к владению и фронтендом, и бэкендом",
    steps: [
      { id: "1", title: "Основы веба", description: "HTML, CSS, JavaScript — фундамент любого веб-разработчика.", details: "", resources: [], skills: ["HTML5", "CSS3", "JavaScript", "HTTP", "Git"], duration: "2-3 месяца" },
      { id: "2", title: "Frontend-фреймворк", description: "React или Vue.js для создания интерактивных интерфейсов.", details: "", resources: [], skills: ["React/Vue", "TypeScript", "Роутинг", "Стейт-менеджмент"], duration: "2-3 месяца" },
      { id: "3", title: "Backend и базы данных", description: "Серверный язык, REST API, работа с БД.", details: "", resources: [], skills: ["Python/Node.js", "FastAPI/Express", "PostgreSQL", "REST API"], duration: "2-3 месяца" },
      { id: "4", title: "Интеграция и деплой", description: "Соединение фронта и бэка, Docker, CI/CD, деплой.", details: "", resources: [], skills: ["Docker", "CI/CD", "Nginx", "Cloud", "Тестирование"], duration: "1-2 месяца" },
      { id: "5", title: "Продвинутые навыки", description: "Архитектура, оптимизация, безопасность, работа с командой.", details: "", resources: [], skills: ["Архитектура", "Паттерны", "Agile/Scrum", "Code Review"], duration: "2-4 месяца" },
    ],
  },
  data: {
    key: "data",
    title: "Data Science / Аналитика",
    description: "Путь в мир данных и машинного обучения",
    steps: [
      { id: "1", title: "Python и математика", description: "Основы Python, линейная алгебра, статистика, теория вероятностей.", details: "", resources: [], skills: ["Python", "NumPy", "Статистика", "Линейная алгебра"], duration: "2-3 месяца" },
      { id: "2", title: "Анализ данных", description: "Pandas, визуализация, SQL, работа с реальными датасетами.", details: "", resources: [], skills: ["Pandas", "Matplotlib", "SQL", "EDA", "Jupyter"], duration: "2-3 месяца" },
      { id: "3", title: "Машинное обучение", description: "Классические алгоритмы ML, валидация, feature engineering.", details: "", resources: [], skills: ["Scikit-learn", "Регрессия", "Классификация", "Кластеризация"], duration: "2-3 месяца" },
      { id: "4", title: "Глубокое обучение", description: "Нейронные сети, NLP, компьютерное зрение.", details: "", resources: [], skills: ["PyTorch/TensorFlow", "CNN", "RNN", "Transformers", "NLP"], duration: "3-4 месяца" },
      { id: "5", title: "MLOps и продакшн", description: "Деплой моделей, мониторинг, A/B тесты, пайплайны.", details: "", resources: [], skills: ["MLflow", "Docker", "Airflow", "A/B тесты", "Feature Store"], duration: "2-3 месяца" },
    ],
  },
}

const DEFAULT_ROADMAP: Roadmap = {
  key: "default",
  title: "Общий карьерный путь в IT",
  description: "Универсальный план развития для специалиста в IT-сфере",
  steps: [
    { id: "1", title: "Выберите направление", description: "Определите свою специализацию: фронтенд, бэкенд, data science, DevOps, QA или другое.", details: "", resources: [], skills: ["Самоанализ", "Исследование рынка", "Нетворкинг"], duration: "1-2 недели" },
    { id: "2", title: "Изучите основы", description: "Освойте фундаментальные технологии выбранного направления.", details: "", resources: [], skills: ["Основы программирования", "Git", "Английский язык"], duration: "2-3 месяца" },
    { id: "3", title: "Создайте портфолио", description: "Реализуйте 2-3 проекта, которые покажут ваши навыки.", details: "", resources: [], skills: ["Pet-проекты", "GitHub", "README", "Демо"], duration: "2-3 месяца" },
    { id: "4", title: "Подготовьтесь к поиску работы", description: "Составьте резюме, подготовьтесь к собеседованиям, настройте профиль.", details: "", resources: [], skills: ["Резюме", "LinkedIn", "Собеседования", "Нетворкинг"], duration: "1-2 месяца" },
    { id: "5", title: "Развивайтесь на работе", description: "Менторство, участие в open source, изучение смежных областей.", details: "", resources: [], skills: ["Менторство", "Open Source", "Soft Skills", "Лидерство"], duration: "Постоянно" },
  ],
}

export default function RoadmapPage() {
  const { user } = useUser()
  const navigate = useNavigate()
  const [expandedStep, setExpandedStep] = useState<string | null>(null)
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set())
  const [roadmap, setRoadmap] = useState<Roadmap>(DEFAULT_ROADMAP)
  const [loading, setLoading] = useState(true)
  const [showExport, setShowExport] = useState(false)
  const progressBarRef = useRef<HTMLDivElement>(null)
  const [needsSurvey, setNeedsSurvey] = useState(false)

  useEffect(() => {
    if (!user.isAuthorized) { setLoading(false); return }

    const load = async () => {
      try {
        const [profile, pending] = await Promise.all([getProfile(), getPendingMandatory()])
        setNeedsSurvey(pending.length > 0)

        const spec = profile.specialization || ""
        const rm = ROADMAPS[spec] || DEFAULT_ROADMAP
        setRoadmap(rm)

        const progress = await getProgress(rm.key)
        setCompletedSteps(new Set(progress.map((p) => p.step_id)))

        const raw = localStorage.getItem("roadmap_progress")
        if (raw) {
          try {
            const local: string[] = JSON.parse(raw)
            for (const stepId of local) {
              if (!progress.some((p) => p.step_id === stepId)) {
                await toggleProgress(rm.key, stepId)
              }
            }
            localStorage.removeItem("roadmap_progress")
            const updated = await getProgress(rm.key)
            setCompletedSteps(new Set(updated.map((p) => p.step_id)))
          } catch {}
        }
      } catch {}
      setLoading(false)
    }
    load()
  }, [user.isAuthorized])

  if (!user.isAuthorized) {
    return (
      <div className="flex h-full flex-col items-center justify-center">
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[#3649F9]/10">
          <img src="/icons/icon map.svg" alt="" className="h-8 w-8 opacity-60" />
        </div>
        <p className="mb-2 text-lg font-medium text-gray-600">Дорожная карта</p>
        <p className="mb-6 text-sm text-[#C5CBD3]">Войдите, чтобы увидеть свой карьерный план</p>
        <Link to="/sign-in" className="rounded-lg bg-[#3649F9] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#3649F9]/90">
          Войти
        </Link>
      </div>
    )
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>

  const handleToggle = async (stepId: string) => {
    const prev = new Set(completedSteps)
    if (prev.has(stepId)) prev.delete(stepId)
    else prev.add(stepId)
    setCompletedSteps(prev)

    if (prev.size === roadmap.steps.length && roadmap.steps.length > 0) {
      const rect = progressBarRef.current?.getBoundingClientRect()
      if (rect) {
        const x = (rect.right) / window.innerWidth
        const y = rect.top / window.innerHeight
        confetti({ particleCount: 100, spread: 70, origin: { x, y }, colors: ["#3649F9", "#22c55e", "#f59e0b", "#ec4899"] })
        setTimeout(() => confetti({ particleCount: 50, spread: 100, origin: { x, y: y - 0.05 } }), 300)
      } else {
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.3 } })
      }
    }

    try {
      await toggleProgress(roadmap.key, stepId)
    } catch {
      setCompletedSteps(completedSteps)
    }
  }

  const progress = roadmap.steps.length > 0
    ? Math.round((completedSteps.size / roadmap.steps.length) * 100)
    : 0

  const handleExportRoadmap = async (format: "md" | "html") => {
    const lines = [`# ${roadmap.title}\n`, `${roadmap.description}\n`]
    for (const [i, step] of roadmap.steps.entries()) {
      const done = completedSteps.has(step.id) ? " [x]" : " [ ]"
      lines.push(`## ${i + 1}.${done} ${step.title} (${step.duration})`)
      lines.push(step.description)
      lines.push(`**Навыки:** ${step.skills.join(", ")}\n`)
    }
    lines.push(`\n---\nПрогресс: ${progress}%`)
    const text = lines.join("\n")

    if (format === "md") {
      const blob = new Blob([text], { type: "text/markdown" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a"); a.href = url; a.download = `roadmap-${roadmap.key}.md`; a.click()
      URL.revokeObjectURL(url)
    } else {
      try {
        const { data } = await baseClient.post("/api/export", { message_id: "00000000-0000-0000-0000-000000000000", format: "html" }, { responseType: "blob" }).catch(() => ({ data: null }))
        const html = `<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><title>${roadmap.title}</title><style>body{font-family:system-ui;max-width:800px;margin:40px auto;padding:0 20px;color:#333}h1{color:#3649F9}h2{margin-top:1.5em}.done{color:#22c55e}.skills{color:#3649F9;font-size:0.9em}</style></head><body>${text.replace(/^# (.+)$/gm, '<h1>$1</h1>').replace(/^## (.+)$/gm, '<h2>$1</h2>').replace(/\*\*(.+?)\*\*/g, '<strong class="skills">$1</strong>').replace(/\n/g, '<br>')}</body></html>`
        const blob = new Blob([html], { type: "text/html" })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a"); a.href = url; a.download = `roadmap-${roadmap.key}.html`; a.click()
        URL.revokeObjectURL(url)
      } catch {}
    }
    setShowExport(false)
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="mb-2 text-2xl font-bold text-gray-900">{roadmap.title}</h1>
            <p className="text-sm text-[#6D7C90]">{roadmap.description}</p>
          </div>
          <div className="relative shrink-0">
            <button onClick={() => setShowExport((v) => !v)}
              className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-[#6D7C90] hover:border-[#3649F9] hover:text-[#3649F9]">
              Скачать
            </button>
            {showExport && (
              <div className="absolute right-0 top-full z-10 mt-1 rounded-lg border bg-white py-1 shadow-lg">
                <button onClick={() => handleExportRoadmap("md")} className="block w-full px-4 py-1.5 text-left text-xs text-gray-600 hover:bg-gray-50">Markdown</button>
                <button onClick={() => handleExportRoadmap("html")} className="block w-full px-4 py-1.5 text-left text-xs text-gray-600 hover:bg-gray-50">HTML</button>
              </div>
            )}
          </div>
        </div>

        {roadmap.key === "default" && (
          <div className="mt-4 rounded-lg bg-[#E8EAFF] px-4 py-3">
            {needsSurvey ? (
              <div>
                <p className="mb-2 text-sm text-[#3649F9]">Для персонализированного roadmap пройдите обязательный опрос</p>
                <button onClick={() => navigate("/surveys")}
                  className="rounded-lg bg-[#3649F9] px-4 py-2 text-xs font-medium text-white">
                  Пройти опрос
                </button>
              </div>
            ) : (
              <p className="text-sm text-[#3649F9]">
                Укажите специализацию в{" "}
                <Link to="/profile" className="font-medium underline">профиле</Link>
                {", "}а затем{" "}
                <Link to="/chat" className="font-medium underline">пообщайтесь с ботом</Link>
                {" "}для персонализированной дорожной карты
              </p>
            )}
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-[#6D7C90]">Прогресс</span>
          <span className={["font-medium", progress === 100 ? "text-green-600" : "text-gray-900"].join(" ")}>{progress}%{progress === 100 && " — Завершено!"}</span>
        </div>
        <div ref={progressBarRef} className="h-2 overflow-hidden rounded-full bg-gray-100">
          <div className={["h-full rounded-full transition-all duration-500", progress === 100 ? "bg-green-500" : "bg-[#3649F9]"].join(" ")} style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-4">
        {roadmap.steps.map((step, index) => {
          const isCompleted = completedSteps.has(step.id)
          const isExpanded = expandedStep === step.id

          return (
            <div key={step.id} className="overflow-hidden rounded-2xl border border-gray-200 bg-white transition-shadow hover:shadow-sm">
              <div className="flex w-full items-center gap-4 p-5">
                <button
                  onClick={() => handleToggle(step.id)}
                  aria-label={isCompleted ? `Снять отметку: ${step.title}` : `Отметить: ${step.title}`}
                  className={[
                    "flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold transition-colors",
                    isCompleted ? "bg-[#3649F9] text-white" : "bg-gray-100 text-[#6D7C90] hover:bg-[#E8EAFF]",
                  ].join(" ")}
                >
                  {isCompleted ? (
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    index + 1
                  )}
                </button>
                <button onClick={() => setExpandedStep(isExpanded ? null : step.id)} className="flex flex-1 items-center gap-4 text-left">
                  <div className="flex-1">
                    <h3 className={["text-base font-semibold", isCompleted ? "text-[#3649F9]" : "text-gray-900"].join(" ")}>{step.title}</h3>
                    <p className="mt-0.5 text-xs text-[#6D7C90]">{step.duration}</p>
                  </div>
                  <svg className={["h-5 w-5 text-[#C5CBD3] transition-transform", isExpanded ? "rotate-180" : ""].join(" ")} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>

              {isExpanded && (
                <div className="border-t border-gray-100 px-5 pb-5 pt-4">
                  <p className="mb-3 text-sm leading-relaxed text-[#6D7C90]">{step.description}</p>

                  {step.details && (
                    <div className="mb-4 rounded-lg bg-[#f8f9ff] p-4">
                      <p className="mb-1 text-xs font-semibold text-gray-800">Подробно:</p>
                      <p className="text-xs leading-relaxed text-[#6D7C90]">{step.details}</p>
                    </div>
                  )}

                  {step.resources.length > 0 && (
                    <div className="mb-4">
                      <p className="mb-2 text-xs font-semibold text-gray-800">Ресурсы:</p>
                      <ul className="space-y-1">
                        {step.resources.map((r) => (
                          <li key={r} className="flex items-center gap-2 text-xs text-[#3649F9]">
                            <span className="h-1 w-1 shrink-0 rounded-full bg-[#3649F9]" />
                            {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2">
                    {step.skills.map((skill) => (
                      <span key={skill} className="rounded-full bg-[#E8EAFF] px-3 py-1 text-xs font-medium text-[#3649F9]">{skill}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
