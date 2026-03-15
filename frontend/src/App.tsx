// frontend/main.tsx (или index.tsx)
import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import router from "../../frontend/src/router";

export default function App() {
  return <RouterProvider router={router} />;
}
