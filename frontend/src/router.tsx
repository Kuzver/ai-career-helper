import React from "react"
import { createBrowserRouter, Navigate } from "react-router-dom"
import AppLayout from "~/shared/components/ui/app-layout"
import ChatPage, { loader as chatLoader } from "../app/pages/chat"
import SignIn from "../app/pages/auth/ui/sign-in"
import SignUp from "../app/pages/auth/ui/sign-up"
import KnowledgeBase from "../app/pages/knowledge-base/ui/knowledge-base"
import Roadmap from "../app/pages/roadmap"
import Profile from "../app/pages/profile"
import AuthLayout from "../app/pages/auth/ui/auth-layout"

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/chat" replace /> },
      { path: "chat", element: <ChatPage />, loader: chatLoader },
      { path: "knowledge-base", element: <KnowledgeBase /> },
      { path: "roadmap", element: <Roadmap /> },
      { path: "profile", element: <Profile /> },
    ],
  },
  {
    element: <AuthLayout />,
    children: [
      { path: "/sign-in", element: <SignIn /> },
      { path: "/sign-up", element: <SignUp /> },
    ],
  },
])

export default router
