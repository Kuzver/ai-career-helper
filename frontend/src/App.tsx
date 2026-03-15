import { createBrowserRouter, RouterProvider } from "react-router-dom";

import SignIn from "~/pages/auth/ui/sign-in";
import SignUp from "~/pages/auth/ui/sign-up";
import ChatPage, { clientLoader as chatClientLoader } from "~/pages/chat";

// Адаптер для LoaderFunction
const chatLoader = async (args: { request: Request }) => {
  // Приведение к типу any, чтобы TS не ругался на недостающие свойства
  return chatClientLoader({ request: args.request } as any);
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <ChatPage />,
    loader: chatLoader, // ← теперь TS принимает
  },
  {
    path: "/sign-in",
    element: <SignIn />,
  },
  {
    path: "/sign-up",
    element: <SignUp />,
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}