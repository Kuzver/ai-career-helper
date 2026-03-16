import { createContext, useEffect, useState, type ReactNode } from "react";

export type UserData = {
    isAuthorized: boolean;
    email?: string;
    token?: string;
    userId?: string;
};

export type UserContextData = {
    user: UserData;
    setUser: (user: UserData) => void;
};

const STORAGE_KEY = "auth";

const getInitialUser = (): UserData => {
  if (typeof window === "undefined") {
    return { isAuthorized: false }
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (parsed.token && parsed.email) {
        return { isAuthorized: true, email: parsed.email, token: parsed.token, userId: parsed.userId }
      }
    }
  } catch {}

  return { isAuthorized: false }
}


export const UserContext = createContext<UserContextData>({
    user: getInitialUser(),
    setUser: () => {},
});

export const UserContextProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUserState] = useState<UserData>(getInitialUser);

    const setUser = (newUser: UserData) => {
        setUserState(newUser)

        if (typeof window === "undefined") return

        if (newUser.isAuthorized && newUser.token) {
            window.localStorage.setItem(STORAGE_KEY, JSON.stringify({
                email: newUser.email,
                token: newUser.token,
                userId: newUser.userId,
            }))
        } else {
            window.localStorage.removeItem(STORAGE_KEY)
            window.localStorage.removeItem("user")
        }
    }

    return (
        <UserContext.Provider value={{ user, setUser }}>
            {children}
        </UserContext.Provider>
    )
};
