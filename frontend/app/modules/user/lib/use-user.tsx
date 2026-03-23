import { useCallback, useContext } from "react"
import { UserContext } from "../ui/user-context"

export const useUser = () => {
  const { user, setUser } = useContext(UserContext)

  const logout = useCallback(() => {
    setUser({ isAuthorized: false })
  }, [setUser])

  const getToken = useCallback((): string | null => {
    return user.token ?? null
  }, [user.token])

  return { user, setUser, logout, getToken }
}
