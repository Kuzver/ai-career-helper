import { useCallback, useContext } from "react"
import { UserContext } from "../ui/user-context"

export type UserProfile = {
  name: string
  specialization: string
  experience: string
  skills: string
  careerGoal: string
}

const PROFILE_KEY = "user_profile"

export const useUser = () => {
  const { user, setUser } = useContext(UserContext)

  const logout = useCallback(() => {
    setUser({ isAuthorized: false })
    localStorage.removeItem(PROFILE_KEY)
  }, [setUser])

  const getProfile = useCallback((): UserProfile => {
    try {
      const raw = localStorage.getItem(PROFILE_KEY)
      if (raw) return JSON.parse(raw)
    } catch {}
    return { name: "", specialization: "", experience: "", skills: "", careerGoal: "" }
  }, [])

  const saveProfile = useCallback((profile: UserProfile) => {
    localStorage.setItem(PROFILE_KEY, JSON.stringify(profile))
  }, [])

  const getProfileContext = useCallback((): string => {
    const p = getProfile()
    const parts: string[] = []
    if (p.name) parts.push(`Имя: ${p.name}`)
    if (p.specialization) parts.push(`Специализация: ${p.specialization}`)
    if (p.experience) parts.push(`Опыт: ${p.experience}`)
    if (p.skills) parts.push(`Навыки: ${p.skills}`)
    if (p.careerGoal) parts.push(`Карьерная цель: ${p.careerGoal}`)
    return parts.length > 0 ? parts.join(". ") + "." : ""
  }, [getProfile])

  const getToken = useCallback((): string | null => {
    return user.token ?? null
  }, [user.token])

  return { user, setUser, logout, getProfile, saveProfile, getProfileContext, getToken }
}
