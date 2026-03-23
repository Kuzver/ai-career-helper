import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useUser } from "~/modules/user/lib/use-user"
import { baseClient } from "~/shared/api/axios-client"
import { getPendingMandatory } from "~/modules/survey/api/surveys"

export default function SignUp() {
  const navigate = useNavigate()
  const { setUser } = useUser()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [agree, setAgree] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const inputCls = "w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#3649F9] focus:ring-1 focus:ring-[#3649F9]"

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")

    if (!email || !password || !confirmPassword) { setError("Заполните все поля"); return }
    if (password.length < 8) { setError("Пароль должен быть не менее 8 символов"); return }
    if (password !== confirmPassword) { setError("Пароли не совпадают"); return }
    if (!agree) { setError("Необходимо согласиться с условиями использования"); return }

    setLoading(true)
    try {
      const { data } = await baseClient.post("/api/auth/register", { email, password })
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
      setError(typeof message === "string" ? message : "Ошибка при регистрации")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="px-10 py-8">
        <Link to="/" className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-[#3649F9]" />
          <span className="text-xl font-semibold text-gray-900">ИИ-ассистент</span>
        </Link>
      </div>
      <div className="mx-auto w-full max-w-md px-10 py-8">
        <h1 className="mb-2 text-3xl font-bold uppercase tracking-tight text-gray-900">Создать аккаунт</h1>
        <p className="mb-12 text-[#C5CBD3]">Зарегистрируйтесь, чтобы начать работу</p>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm text-gray-600">Электронная почта</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="example@mail.com" autoComplete="email" className={inputCls} />
          </div>
          <div>
            <label className="mb-2 block text-sm text-gray-600">Пароль</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="Минимум 8 символов" autoComplete="new-password" className={inputCls} />
          </div>
          <div>
            <label className="mb-2 block text-sm text-gray-600">Подтвердите пароль</label>
            <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Повторите пароль" autoComplete="new-password" className={inputCls} />
          </div>
          <label className="flex items-start gap-2 text-sm text-gray-600">
            <input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-[#C5CBD3] accent-[#3649F9]" />
            <span>Я согласен с <span className="text-[#3649F9]">условиями использования</span> и <span className="text-[#3649F9]">политикой конфиденциальности</span></span>
          </label>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full rounded-lg bg-[#3649F9] py-4 text-sm font-semibold text-white hover:bg-[#3649F9]/90 disabled:opacity-50">
            {loading ? "Создаём аккаунт..." : "Создать аккаунт"}
          </button>
          <p className="text-center text-sm text-gray-500">
            Уже есть аккаунт?{" "}
            <Link to="/sign-in" className="font-medium text-[#3649F9] hover:underline">Войти</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
