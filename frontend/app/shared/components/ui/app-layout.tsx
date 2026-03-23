import { useEffect, useRef, useState } from "react"
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom"
import { useUser } from "~/modules/user/lib/use-user"
import { ChatSidebar } from "~/modules/chat/ui/chat-sidebar"
import { baseClient } from "~/shared/api/axios-client"

type SearchResult = { type: string; id: string; title: string; url: string }

const navItems = [
  { title: "Дорожная карта", url: "/roadmap", icon: "/icons/icon map.svg" },
  { title: "ИИ-ассистент", url: "/chat", icon: "/icons/icon ai.svg" },
  { title: "Опросы", url: "/surveys", icon: "/icons/icon homework.svg" },
  { title: "Мой профиль", url: "/profile", icon: "/icons/icon profile.svg" },
  { title: "База знаний", url: "/knowledge-base", icon: "/icons/icon info.svg" },
]

export default function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useUser()
  const isChatPage = location.pathname === "/chat"

  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [showResults, setShowResults] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const searchTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleLogout = () => {
    logout()
    navigate("/sign-in")
  }

  useEffect(() => {
    if (searchTimeout.current) clearTimeout(searchTimeout.current)
    if (!searchQuery || searchQuery.length < 2) { setSearchResults([]); return }

    searchTimeout.current = setTimeout(async () => {
      try {
        const { data } = await baseClient.get<SearchResult[]>("/api/search", { params: { q: searchQuery } })
        setSearchResults(data)
        setShowResults(true)
      } catch { setSearchResults([]) }
    }, 300)

    return () => { if (searchTimeout.current) clearTimeout(searchTimeout.current) }
  }, [searchQuery])

  useEffect(() => { setShowResults(false); setSearchQuery("") }, [location.pathname])

  return (
    <div className="flex h-screen bg-white">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/30 md:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      <aside className={[
        "flex w-56 shrink-0 flex-col border-r border-gray-100 bg-white",
        "fixed inset-y-0 left-0 z-50 transition-transform md:relative md:translate-x-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full",
      ].join(" ")}>
        <Link to="/" className="flex items-center gap-3 px-5 py-5">
          <div className="h-9 w-9 shrink-0 rounded-full bg-[#3649F9]" />
          <span className="text-lg font-semibold text-gray-900">ИИ-ассистент</span>
        </Link>
        <nav className="space-y-1 px-3 pt-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.url || location.pathname.startsWith(item.url + "/")
            return (
              <Link key={item.url} to={item.url} onClick={() => setSidebarOpen(false)}
                className={["flex items-center gap-3 rounded-lg px-4 py-2.5 text-sm transition-colors",
                  isActive ? "bg-[#3649F9] font-medium text-white" : "text-[#C5CBD3] hover:bg-gray-50 hover:text-gray-600",
                ].join(" ")}>
                <img src={item.icon} alt="" className={["h-5 w-5", isActive ? "brightness-0 invert" : "opacity-60"].join(" ")} />
                {item.title}
              </Link>
            )
          })}
        </nav>

        {isChatPage && user.isAuthorized && <ChatSidebar />}

        <div className="mt-auto px-5 py-4">
          {user.isAuthorized ? (
            <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-red-400 hover:text-red-500">
              <img src="/icons/icon exit.svg" alt="" className="h-5 w-5" />
              Выйти
            </button>
          ) : (
            <Link to="/sign-in" className="flex items-center gap-2 text-sm text-[#3649F9]">
              <img src="/icons/icon exit.svg" alt="" className="h-5 w-5" />
              Войти
            </Link>
          )}
        </div>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center gap-4 border-b border-gray-100 px-4 py-3 md:px-6">
          {/* Mobile hamburger */}
          <button onClick={() => setSidebarOpen(true)} className="shrink-0 md:hidden" aria-label="Открыть меню">
            <svg className="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Search */}
          {user.isAuthorized && (
            <div className="relative flex-1">
              <div className="flex items-center gap-2">
                <img src="/icons/search.svg" alt="" className="h-5 w-5 opacity-40" />
                <input
                  type="text"
                  placeholder="Поиск по чатам и статьям..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => searchResults.length > 0 && setShowResults(true)}
                  onBlur={() => setTimeout(() => setShowResults(false), 200)}
                  className="w-full bg-transparent text-sm text-gray-600 placeholder-[#C5CBD3] outline-none"
                />
              </div>
              {showResults && searchResults.length > 0 && (
                <div className="absolute left-0 right-0 top-full z-20 mt-2 rounded-lg border bg-white py-1 shadow-lg">
                  {searchResults.map((r) => (
                    <button
                      key={`${r.type}-${r.id}`}
                      onMouseDown={() => { navigate(r.url); setShowResults(false); setSearchQuery("") }}
                      className="flex w-full items-center gap-3 px-4 py-2 text-left text-sm text-gray-600 hover:bg-gray-50"
                    >
                      <span className={["rounded px-1.5 py-0.5 text-xs",
                        r.type === "chat" ? "bg-[#E8EAFF] text-[#3649F9]" : "bg-green-50 text-green-600",
                      ].join(" ")}>
                        {r.type === "chat" ? "Чат" : "Статья"}
                      </span>
                      <span className="truncate">{r.title}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          <Link to="/profile" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gray-100 hover:bg-gray-200" aria-label="Мой профиль">
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
