import { Navigate, Outlet } from "react-router";
import { useUser } from "~/modules/user/lib/use-user"

export default function AuthLayout({ children }: { children: React.ReactNode }) {
    const { user: { isAuthorized } } = useUser();

    if (isAuthorized) {
        return <Navigate to='/' replace />
    }

    return (
        <Outlet />
    )
}
