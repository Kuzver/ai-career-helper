import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useUser } from "~/modules/user/lib/use-user"
import { baseClient } from "~/shared/api/axios-client"
import { Logo } from "~/shared/components/ui/logo"
import { getPendingMandatory } from "~/modules/survey/api/surveys"

export default function SignIn() {
  const navigate = useNavigate()
  const { setUser } = useUser()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    if (!email || !password) { setError("Заполните все поля"); return }

    setLoading(true)
    try {
      const { data } = await baseClient.post("/api/auth/login", { email, password })
      setUser({
        isAuthorized: true,
        email: data.email,
        token: data.token,
        userId: data.user_id,
      })
      try {
        const pending = await getPendingMandatory()
        if (pending.length > 0) {
          navigate(`/survey/${pending[0].id}`)
          return
        }
      } catch {}
      navigate("/")
    } catch (err: any) {
      const message = err?.response?.data?.detail
      setError(typeof message === "string" ? message : "Неверный email или пароль")
    } finally {
      setLoading(false)
    }
  }

  const inputCls = "w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#3649F9] focus:ring-1 focus:ring-[#3649F9] dark:border-gray-600 dark:bg-[#1e293b] dark:text-gray-200 dark:placeholder-gray-500"

  return (
    <div className="flex min-h-dvh flex-col bg-white dark:bg-[#0f172a]">
      <div className="px-5 py-6 md:px-10 md:py-8">
        <div className="flex items-center gap-3">
          <Logo size={40} />
          <span className="text-xl font-semibold text-gray-900 dark:text-gray-100">ИИ-ассистент</span>
        </div>
      </div>
      <div className="mx-auto w-full max-w-md px-5 py-6 md:px-10 md:py-8">
        <h1 className="mb-2 text-2xl font-bold uppercase tracking-tight text-gray-900 md:text-3xl dark:text-gray-100">Вход в аккаунт</h1>
        <p className="mb-12 text-[#C5CBD3]">Войдите, чтобы продолжить работу</p>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm text-gray-600 dark:text-gray-400">Электронная почта</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="example@mail.com" autoComplete="email" className={inputCls} />
          </div>
          <div>
            <label className="mb-2 block text-sm text-gray-600 dark:text-gray-400">Пароль</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="Пароль" autoComplete="current-password" className={inputCls} />
          </div>
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <input type="checkbox" className="h-4 w-4 rounded border-[#C5CBD3] accent-[#3649F9]" />
              Запомнить меня
            </label>
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full rounded-lg bg-[#3649F9] py-4 text-sm font-semibold text-white hover:bg-[#3649F9]/90 disabled:opacity-50">
            {loading ? "Входим..." : "Войти"}
          </button>
          <p className="text-center text-sm text-gray-500">
            Нет аккаунта?{" "}
            <Link to="/sign-up" className="font-medium text-[#3649F9] hover:underline">Зарегистрироваться</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
