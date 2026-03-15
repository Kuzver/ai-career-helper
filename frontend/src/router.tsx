import React from "react";
import { createBrowserRouter } from "react-router-dom";
import ChatPage from "~/pages/chat"; // алиас ~ = frontend/app
import SignIn from "~/pages/auth/ui/sign-in";
import SignUp from "~/pages/auth/ui/sign-up";

const routes = [
  {
    path: "/",
    element: <ChatPage />,
    errorElement: <div>Ошибка при загрузке чатов 😢</div>,
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
];

const router = createBrowserRouter(routes);
export default router;