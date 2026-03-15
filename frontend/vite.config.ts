// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),          // React plugin, версия 5 для Vite 7
    tsconfigPaths()   // Поддержка путей из tsconfig.json
  ],
  server: {
    port: 5174,       // порт фронта, поменяй если нужно
    proxy: {
      '/api': {       // всё, что идёт на /api, будет проксировано на бэк
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});