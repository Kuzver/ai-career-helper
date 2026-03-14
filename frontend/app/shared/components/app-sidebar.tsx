import { BookOpen, MessageCircle } from "lucide-react"
import { Link, useLocation } from "react-router"

import { useUser } from "~/modules/user/lib/use-user"
import { Button } from "~/shared/components/ui/button"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "~/shared/components/ui/sidebar"

const navigation = [
  { title: "Чат", url: "/", icon: MessageCircle },
  { title: "База знаний", url: "/knowledge-base", icon: BookOpen },
]

export function AppSidebar() {
  const { user, logout } = useUser()
  const isAuthorized = user.isAuthorized
  const location = useLocation()

  return (
    <Sidebar>
      <SidebarHeader className="px-4 py-3 text-base font-semibold">
        AI Career Helper
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Навигация</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.map((item) => {
                const isActive = location.pathname === item.url

                return (
                  <SidebarMenuItem key={item.url}>
                    <SidebarMenuButton asChild isActive={isActive}>
                      <Link to={item.url} className="gap-3">
                        <item.icon className="size-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="border-t px-4 py-3 text-sm">
        <div>
          <p className="font-medium">{user.email ?? "Гость"}</p>
          <p className="text-muted-foreground text-xs">
            {isAuthorized ? "Авторизован" : "Не авторизован"}
          </p>
        </div>
        <Button
          size="sm"
          className="mt-3"
          variant={isAuthorized ? "outline" : "default"}
          onClick={isAuthorized ? logout : undefined}
          asChild={!isAuthorized}
        >
          {isAuthorized ? "Выйти" : <Link to="/sign-in">Войти</Link>}
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}
