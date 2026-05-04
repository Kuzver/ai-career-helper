import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useUser } from "~/modules/user/lib/use-user"
import { baseClient } from "~/shared/api/axios-client"
import { Logo } from "~/shared/components/ui/logo"
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

  const inputCls = "w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#3649F9] focus:ring-1 focus:ring-[#3649F9] dark:border-gray-600 dark:bg-[#1e293b] dark:text-gray-200 dark:placeholder-gray-500"

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")

    if (!email || !password || !confirmPassword) { setError("Заполните все поля"); return }
    if (password.length < 8) { setError("Пароль должен быть не менее 8 символов"); return }
    if (password !== confirmPassword) { setError("Пароли не совпадают"); return }
    if (!agree) { setError("Необходимо согласиться с политикой конфиденциальности"); return }

    setLoading(true)
    try {
      const { data } = await baseClient.post("/api/auth/register", { 
          email, 
          password,
          policy_accepted: agree 
      })
      
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
    <div className="flex min-h-dvh flex-col bg-white dark:bg-[#0f172a]">
      <div className="px-5 py-6 md:px-10 md:py-8">
        <Link to="/" className="flex items-center gap-3">
          <Logo size={40} />
          <span className="text-xl font-semibold text-gray-900 dark:text-gray-100">ИИ-ассистент</span>
        </Link>
      </div>
      <div className="mx-auto w-full max-w-md px-5 py-6 md:px-10 md:py-8">
        <h1 className="mb-2 text-2xl font-bold uppercase tracking-tight text-gray-900 md:text-3xl dark:text-gray-100">Создать аккаунт</h1>
        <p className="mb-12 text-[#C5CBD3]">Зарегистрируйтесь, чтобы начать работу</p>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm text-gray-600 dark:text-gray-400">Электронная почта</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="example@mail.com" autoComplete="email" className={inputCls} />
          </div>
          <div>
            <label className="mb-2 block text-sm text-gray-600 dark:text-gray-400">Пароль</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="Минимум 8 символов" autoComplete="new-password" className={inputCls} />
          </div>
          <div>
            <label className="mb-2 block text-sm text-gray-600 dark:text-gray-400">Подтвердите пароль</label>
            <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Повторите пароль" autoComplete="new-password" className={inputCls} />
          </div>
          <label className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
            <input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-[#C5CBD3] accent-[#3649F9]" />
            <span>
              Я принимаю условия{" "}
              <Link 
                to="/privacy-policy" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 underline hover:text-blue-800"
              >
                Политики конфиденциальности
              </Link>
              {" "}и даю согласие на обработку персональных данных.
            </span>
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