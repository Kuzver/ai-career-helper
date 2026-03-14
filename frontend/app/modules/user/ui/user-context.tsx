import { createContext, useEffect, useState, type ReactNode } from "react";

export type UserData = {
    isAuthorized: boolean;
    email?: string;
};

export type UserContextData = {
    user: UserData;
    setUser: (user: UserData) => void;
};

const getInitialUser = (): UserData => {
  if (typeof window === "undefined") {
    return { isAuthorized: false }
  }

  const storedEmail = window.localStorage.getItem("user")

  return storedEmail
    ? { isAuthorized: true, email: storedEmail }
    : { isAuthorized: false }
}


export const UserContext = createContext<UserContextData>({
    user: getInitialUser(),
    setUser: () => {},
});

export const UserContextProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<UserData>(getInitialUser);

    useEffect(() => {
        if (typeof window === "undefined") return

        if (user.email) {
            window.localStorage.setItem("user", user.email)
        } else {
            window.localStorage.removeItem("user")
        }
    }, [user])

    return (
        <UserContext.Provider value={{ user, setUser }}>
            {children}
        </UserContext.Provider>
    )
};