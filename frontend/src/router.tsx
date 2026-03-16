import React from "react";
import { createBrowserRouter } from "react-router-dom";
import AppLayout from "~/shared/components/ui/app-layout";
import ChatPage, { loader, action } from "../app/pages/chat";
import SignIn from "../app/pages/auth/ui/sign-in";
import SignUp from "../app/pages/auth/ui/sign-up";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />, // ← теперь рендерится Layout с сайдбаром
    errorElement: <div>Ошибка в корне</div>,
    children: [
      {
        index: true,
        element: <ChatPage />,
        loader,
        action,
        errorElement: <div>Ошибка при загрузке чатов 😢</div>,
      },
      // сюда можно добавить другие маршруты, например:
      // { path: "knowledge-base", element: <KnowledgeBase /> },
    ],
  },
  {
    path: "/sign-in",
    element: <SignIn />,
    errorElement: <div>Ошибка при входе</div>,
  },
  {
    path: "/sign-up",
    element: <SignUp />,
    errorElement: <div>Ошибка при регистрации</div>,
  },
]);

export default router;