import { Link, Outlet, useLocation, useNavigate } from "react-router-dom"
import { useUser } from "~/modules/user/lib/use-user"

const navItems = [
  { title: "Дорожная карта", url: "/roadmap", icon: "/icons/icon map.svg" },
  { title: "ИИ-ассистент", url: "/", icon: "/icons/icon ai.svg" },
  { title: "Мой профиль", url: "/profile", icon: "/icons/icon profile.svg" },
  { title: "База знаний", url: "/knowledge-base", icon: "/icons/icon info.svg" },
]

export default function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useUser()

  const handleLogout = () => {
    logout()
    navigate("/sign-in")
  }

  return (
    <div className="flex h-screen bg-white">
      <aside className="flex w-56 shrink-0 flex-col border-r border-gray-100">
        <Link to="/" className="flex items-center gap-3 px-5 py-5">
          <div className="h-9 w-9 shrink-0 rounded-full bg-[#0157FF]" />
          <span className="text-lg font-semibold text-gray-900">ИИ-ассистент</span>
        </Link>
        <nav className="flex-1 space-y-1 px-3 pt-2">
          {navItems.map((item) => {
            const isActive = item.url === "/" ? location.pathname === "/" : location.pathname.startsWith(item.url)
            return (
              <Link key={item.url} to={item.url}
                className={["flex items-center gap-3 rounded-lg px-4 py-2.5 text-sm transition-colors",
                  isActive ? "bg-[#0157FF] font-medium text-white" : "text-[#C5CBD3] hover:bg-gray-50 hover:text-gray-600",
                ].join(" ")}>
                <img src={item.icon} alt="" className={["h-5 w-5", isActive ? "brightness-0 invert" : "opacity-60"].join(" ")} />
                {item.title}
              </Link>
            )
          })}
        </nav>
        <div className="px-5 py-4">
          {user.isAuthorized ? (
            <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-red-400 hover:text-red-500">
              <img src="/icons/icon exit.svg" alt="" className="h-5 w-5" />
              Выйти
            </button>
          ) : (
            <Link to="/sign-in" className="flex items-center gap-2 text-sm text-[#0157FF]">
              <img src="/icons/icon exit.svg" alt="" className="h-5 w-5" />
              Войти
            </Link>
          )}
        </div>
      </aside>
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center gap-4 border-b border-gray-100 px-6 py-3">
          <div className="flex flex-1 items-center gap-2">
            <img src="/icons/search.svg" alt="" className="h-5 w-5 opacity-40" />
            <input type="text" placeholder="Введите запрос..." autoComplete="off" name="app-search"
              spellCheck={false} className="w-full bg-transparent text-sm text-gray-600 placeholder-[#C5CBD3] outline-none" />
          </div>
          <button className="shrink-0">
            <img src="/icons/notification.svg" alt="" className="h-5 w-5 opacity-40" />
          </button>
          <Link to="/profile" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gray-100 hover:bg-gray-200">
            <img src="/icons/icon profile.svg" alt="" className="h-5 w-5 opacity-50" />
          </Link>
        </header>
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
