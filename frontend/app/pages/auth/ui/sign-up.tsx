import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useUser } from "~/modules/user/lib/use-user"

export default function SignUp() {
  const navigate = useNavigate()
  const { setUser } = useUser()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [birthDate, setBirthDate] = useState("")
  const [agree, setAgree] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const inputCls = "w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#0157FF] focus:ring-1 focus:ring-[#0157FF]"

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")

    if (!email || !password || !confirmPassword) { setError("Заполните все обязательные поля"); return }
    if (password.length < 8) { setError("Пароль должен быть не менее 8 символов"); return }
    if (password !== confirmPassword) { setError("Пароли не совпадают"); return }
    if (!agree) { setError("Необходимо согласиться с условиями использования"); return }

    setLoading(true)
    setUser({ isAuthorized: true, email })
    navigate("/")
  }

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <div className="px-10 py-8">
        <Link to="/" className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-[#0157FF]" />
          <span className="text-xl font-semibold text-gray-900">ИИ-ассистент</span>
        </Link>
      </div>
      <div className="mx-auto w-full max-w-2xl px-10 py-8">
        <h1 className="mb-2 text-3xl font-bold uppercase tracking-tight text-gray-900">Создать аккаунт</h1>
        <p className="mb-12 text-[#C5CBD3]">Для бизнеса, музыкальной группы или публичной личности</p>
        <form className="space-y-8" onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm text-gray-600">Электронная почта *</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder="example@mail.com" autoComplete="email" className={inputCls} />
            </div>
            <div>
              <label className="mb-2 block text-sm text-gray-600">Дата рождения</label>
              <input type="date" value={birthDate} onChange={(e) => setBirthDate(e.target.value)}
                className={inputCls + " text-gray-600"} />
            </div>
          </div>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm text-gray-600">Пароль *</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                placeholder="Минимум 8 символов" autoComplete="new-password" className={inputCls} />
            </div>
            <div>
              <label className="mb-2 block text-sm text-gray-600">Подтвердите пароль *</label>
              <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Повторите пароль" autoComplete="new-password" className={inputCls} />
            </div>
          </div>
          <div className="space-y-3">
            <label className="flex items-start gap-2 text-sm text-gray-600">
              <input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)}
                className="mt-0.5 h-4 w-4 rounded border-[#C5CBD3] accent-[#0157FF]" required />
              <span>Я согласен с <span className="text-[#0157FF]">условиями использования</span> и <span className="text-[#0157FF]">политикой конфиденциальности</span> *</span>
            </label>
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full rounded-lg bg-[#0157FF] py-4 text-sm font-semibold text-white hover:bg-[#0157FF]/90 disabled:opacity-50">
            Создать аккаунт
          </button>
          <p className="text-center text-sm text-gray-500">
            Уже есть аккаунт?{" "}
            <Link to="/sign-in" className="font-medium text-[#0157FF] hover:underline">Войти</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
