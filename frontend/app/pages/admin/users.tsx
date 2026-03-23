import { useEffect, useState } from "react"
import { useUser } from "~/modules/user/lib/use-user"
import { baseClient } from "~/shared/api/axios-client"

type User = {
  id: string
  email: string
  first_name: string | null
  role: string
  is_active: boolean
}

const ROLES = ["user", "editor", "admin"]

export default function AdminUsers() {
  const { user } = useUser()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadUsers = async () => {
    try {
      const { data } = await baseClient.get<User[]>("/api/admin/users")
      setUsers(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Нет доступа")
    } finally { setLoading(false) }
  }

  useEffect(() => { if (user.isAuthorized) loadUsers() }, [user.isAuthorized])

  const handleRoleChange = async (userId: string, role: string) => {
    try {
      await baseClient.patch(`/api/admin/users/${userId}/role`, { role })
      setUsers((prev) => prev.map((u) => u.id === userId ? { ...u, role } : u))
    } catch (err: any) {
      setError(err.response?.data?.detail || "Ошибка")
      setTimeout(() => setError(null), 3000)
    }
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>
  if (error && users.length === 0) return <div className="flex h-full items-center justify-center"><p className="text-sm text-red-500">{error}</p></div>

  const roleColor = (role: string) => {
    if (role === "admin") return "bg-red-50 text-red-600"
    if (role === "editor") return "bg-blue-50 text-blue-600"
    return "bg-gray-50 text-gray-500"
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-8 text-2xl font-bold text-gray-900">Управление пользователями</h1>

      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}

      <div className="space-y-3">
        {users.map((u) => (
          <div key={u.id} className="flex items-center justify-between rounded-xl border border-gray-100 p-4">
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-gray-800">{u.email}</p>
                <span className={`rounded px-2 py-0.5 text-xs font-medium ${roleColor(u.role)}`}>
                  {u.role}
                </span>
              </div>
              {u.first_name && <p className="mt-0.5 text-xs text-[#C5CBD3]">{u.first_name}</p>}
            </div>
            <select
              value={u.role}
              onChange={(e) => handleRoleChange(u.id, e.target.value)}
              disabled={u.id === user.userId}
              className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs outline-none disabled:opacity-40"
            >
              {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
        ))}
      </div>
    </div>
  )
}
