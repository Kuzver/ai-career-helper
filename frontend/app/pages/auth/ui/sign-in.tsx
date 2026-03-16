import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useUser } from "~/modules/user/lib/use-user"

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
      setUser({ isAuthorized: true, email })
      navigate("/")
    } catch {
      setError("Произошла ошибка при входе")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="px-10 py-8">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-[#0157FF]" />
          <span className="text-xl font-semibold text-gray-900">ИИ-ассистент</span>
        </div>
      </div>
      <div className="mx-auto w-full max-w-md px-10 py-8">
        <h1 className="mb-2 text-3xl font-bold uppercase tracking-tight text-gray-900">Вход в аккаунт</h1>
        <p className="mb-12 text-[#C5CBD3]">Войдите, чтобы продолжить работу</p>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm text-gray-600">Электронная почта</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="example@mail.com" autoComplete="email"
              className="w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#0157FF] focus:ring-1 focus:ring-[#0157FF]" />
          </div>
          <div>
            <label className="mb-2 block text-sm text-gray-600">Пароль</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="Пароль" autoComplete="current-password"
              className="w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#0157FF] focus:ring-1 focus:ring-[#0157FF]" />
          </div>
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input type="checkbox" className="h-4 w-4 rounded border-[#C5CBD3] accent-[#0157FF]" />
              Запомнить меня
            </label>
            <Link to="/sign-up" className="text-sm text-[#0157FF] hover:underline">Забыли пароль?</Link>
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full rounded-lg bg-[#0157FF] py-4 text-sm font-semibold text-white hover:bg-[#0157FF]/90 disabled:opacity-50">
            Войти
          </button>
          <p className="text-center text-sm text-gray-500">
            Нет аккаунта?{" "}
            <Link to="/sign-up" className="font-medium text-[#0157FF] hover:underline">Зарегистрироваться</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
