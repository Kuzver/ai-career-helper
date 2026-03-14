import { Outlet } from "react-router"

import { AppSidebar } from "~/shared/components/app-sidebar"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "~/shared/components/ui/sidebar"

export default function AppLayout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="flex min-h-svh flex-1 flex-col bg-background">
        <header className="flex h-16 items-center gap-3 border-b px-6">
          <SidebarTrigger className="shrink-0" />
          <div className="text-lg font-semibold">AI Career Helper</div>
        </header>
        <main className="flex-1 px-6 py-8">
          <Outlet />
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
