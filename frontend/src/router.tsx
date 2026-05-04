import React from "react"
import { createBrowserRouter, Navigate } from "react-router-dom"
import AppLayout from "~/shared/components/ui/app-layout"
import ChatPage, { loader as chatLoader } from "../app/pages/chat"
import SignIn from "../app/pages/auth/ui/sign-in"
import SignUp from "../app/pages/auth/ui/sign-up"
import KnowledgeBase from "../app/pages/knowledge-base/ui/knowledge-base"
import ArticlePage from "../app/pages/knowledge-base/ui/article-page"
import Roadmap from "../app/pages/roadmap"
import Profile from "../app/pages/profile"
import AuthLayout from "../app/pages/auth/ui/auth-layout"
import SurveyList from "../app/pages/survey/survey-list"
import SurveyPage from "../app/pages/survey/survey-page"
import AdminSurveys from "../app/pages/admin/surveys"
import AdminArticles from "../app/pages/admin/articles"
import AdminUsers from "../app/pages/admin/users"
import NotFoundPage from "../app/pages/not-found"
import PrivacyPolicy from "../app/pages/privacy-policy"

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    errorElement: <NotFoundPage />,
    children: [
      { index: true, element: <Navigate to="/chat" replace /> },
      { path: "chat", element: <ChatPage />, loader: chatLoader },
      { path: "knowledge-base", element: <KnowledgeBase /> },
      { path: "knowledge-base/:slug", element: <ArticlePage /> },
      { path: "roadmap", element: <Roadmap /> },
      { path: "profile", element: <Profile /> },
      { path: "surveys", element: <SurveyList /> },
      { path: "survey/:id", element: <SurveyPage /> },
      { path: "admin/surveys", element: <AdminSurveys /> },
      { path: "admin/articles", element: <AdminArticles /> },
      { path: "admin/users", element: <AdminUsers /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
  {
    element: <AuthLayout />,
    children: [
      { path: "/sign-in", element: <SignIn /> },
      { path: "/sign-up", element: <SignUp /> },
    ],
  },

  {
    path: "/privacy-policy",
    element: <PrivacyPolicy />,
  },
])

export default router