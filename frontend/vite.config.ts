import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite"; 
import path from "path";

export default defineConfig({
  plugins: [react(), tsconfigPaths(), tailwindcss(),],
  resolve: {
    alias: {
      "~": path.resolve(__dirname, "app"), // ~ резолвит в frontend/app
    },
  },
  server: {
    port: 5173,
    // fallback для всех маршрутов React Router
    fs: {
      strict: false, // позволяет обращаться к файлам вне root, безопасно для dev
    },
  },
  build: {
    rollupOptions: {
      input: path.resolve(__dirname, "index.html"), // чтобы build понимал точку входа
    },
  },
});