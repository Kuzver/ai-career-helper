import { useCallback, useContext } from "react"
import { UserContext } from "../ui/user-context"

export const useUser = () => {
  const { user, setUser } = useContext(UserContext)

  const logout = useCallback(() => {
    setUser({ isAuthorized: false })
  }, [setUser])

  return {
    user,
    setUser,
    logout,
  }
}
