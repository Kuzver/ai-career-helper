import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { useUser } from "~/modules/user/lib/use-user"
import { getProfile, updateProfile } from "~/modules/user/api/profile"

type ProfileForm = {
  name: string
  specialization: string
  experience: string
  skills: string
  careerGoal: string
}

const SPECIALIZATIONS = [
  { value: "frontend", label: "Frontend-разработка" },
  { value: "backend", label: "Backend-разработка" },
  { value: "fullstack", label: "Fullstack-разработка" },
  { value: "mobile", label: "Мобильная разработка" },
  { value: "data", label: "Data Science / Аналитика" },
  { value: "devops", label: "DevOps" },
  { value: "design", label: "Дизайн" },
  { value: "pm", label: "Управление проектами" },
  { value: "qa", label: "Тестирование (QA)" },
  { value: "other", label: "Другое" },
]

const EXPERIENCE_LEVELS = [
  { value: "student", label: "Студент / Стажёр" },
  { value: "junior", label: "Junior (0-1 год)" },
  { value: "middle", label: "Middle (1-3 года)" },
  { value: "senior", label: "Senior (3-6 лет)" },
  { value: "lead", label: "Lead / Architect (6+ лет)" },
]

export default function Profile() {
  const { user, logout } = useUser()
  const [form, setForm] = useState<ProfileForm>({
    name: "", specialization: "", experience: "", skills: "", careerGoal: "",
  })
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user.isAuthorized) return

    const load = async () => {
      try {
        const data = await getProfile()

        // Одноразовая миграция из localStorage
        if (!data.name && !data.specialization) {
          const raw = localStorage.getItem("user_profile")
          if (raw) {
            try {
              const local = JSON.parse(raw)
              await updateProfile({
                name: local.name || null,
                specialization: local.specialization || null,
                experience_level: local.experience || null,
                skills: local.skills || null,
                career_goal: local.careerGoal || null,
              })
              localStorage.removeItem("user_profile")
              const migrated = await getProfile()
              setForm({
                name: migrated.name || "",
                specialization: migrated.specialization || "",
                experience: migrated.experience_level || "",
                skills: migrated.skills || "",
                careerGoal: migrated.career_goal || "",
              })
              setLoading(false)
              return
            } catch {}
          }
        }

        setForm({
          name: data.name || "",
          specialization: data.specialization || "",
          experience: data.experience_level || "",
          skills: data.skills || "",
          careerGoal: data.career_goal || "",
        })
      } catch {
        setError("Не удалось загрузить профиль")
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [user.isAuthorized])

  if (!user.isAuthorized) {
    return (
      <div className="flex h-full flex-col items-center justify-center">
        <div className="mb-4 h-16 w-16 rounded-full bg-[#3649F9]/10" />
        <p className="mb-2 text-lg font-medium text-gray-600">Вы не авторизованы</p>
        <p className="mb-6 text-sm text-[#C5CBD3]">Войдите, чтобы просматривать профиль</p>
        <Link to="/sign-in" className="rounded-lg bg-[#3649F9] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#3649F9]/90">
          Войти
        </Link>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-[#C5CBD3]">Загрузка профиля...</p>
      </div>
    )
  }

  const update = (key: keyof ProfileForm, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    setSaved(false)
    setError(null)
  }

  const handleSave = async () => {
    try {
      await updateProfile({
        name: form.name || null,
        specialization: form.specialization || null,
        experience_level: form.experience || null,
        skills: form.skills || null,
        career_goal: form.careerGoal || null,
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      setError("Не удалось сохранить профиль")
    }
  }

  const inputCls = "w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#3649F9] focus:ring-1 focus:ring-[#3649F9]"

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-8 text-2xl font-bold text-gray-900">Мой профиль</h1>

      <div className="mb-8 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#3649F9] text-xl font-bold text-white">
          {(form.name?.[0] || user.email?.[0] || "U").toUpperCase()}
        </div>
        <div>
          <p className="text-lg font-medium text-gray-900">{form.name || user.email}</p>
          <p className="text-sm text-[#C5CBD3]">
            {SPECIALIZATIONS.find((s) => s.value === form.specialization)?.label || "Специализация не указана"}
          </p>
        </div>
      </div>

      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}

      <div className="space-y-6">
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-600">Имя</label>
          <input type="text" value={form.name} onChange={(e) => update("name", e.target.value)}
            placeholder="Ваше имя" className={inputCls} />
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-600">Специализация</label>
            <select value={form.specialization} onChange={(e) => update("specialization", e.target.value)}
              className={inputCls + " text-gray-600"}>
              <option value="">Выберите специализацию</option>
              {SPECIALIZATIONS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-600">Уровень опыта</label>
            <select value={form.experience} onChange={(e) => update("experience", e.target.value)}
              className={inputCls + " text-gray-600"}>
              <option value="">Выберите уровень</option>
              {EXPERIENCE_LEVELS.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-600">Ключевые навыки</label>
          <input type="text" value={form.skills} onChange={(e) => update("skills", e.target.value)}
            placeholder="Python, React, SQL, Docker..." className={inputCls} />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-600">Карьерная цель</label>
          <textarea value={form.careerGoal} onChange={(e) => update("careerGoal", e.target.value)}
            placeholder="Например: стать senior backend разработчиком через 2 года"
            className={inputCls + " min-h-[80px] resize-none"} />
        </div>

        <div className="flex items-center gap-4 pt-2">
          <button onClick={handleSave}
            className="rounded-lg bg-[#3649F9] px-8 py-3 text-sm font-medium text-white hover:bg-[#3649F9]/90">
            Сохранить
          </button>
          {saved && <span className="text-sm text-green-600">Данные сохранены</span>}
        </div>

        <hr className="border-gray-100" />
        <button onClick={logout} className="text-sm text-red-400 hover:text-red-500">Выйти из аккаунта</button>
      </div>
    </div>
  )
}
