import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Lee WEB_PORT del .env de la raíz del proyecto
  const env = loadEnv(mode, '..', '')
  const target = `http://localhost:${env.WEB_PORT || 8000}`
  return {
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target,
        changeOrigin: true,
      },
      '/emu-view': {
        target,
        changeOrigin: true,
      }
    }
  }
  }
})
