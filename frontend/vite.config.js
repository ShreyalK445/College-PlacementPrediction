import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/predict': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000',
      '/ready': 'http://127.0.0.1:5000',
      '/metrics': 'http://127.0.0.1:5000',
      '/model': 'http://127.0.0.1:5000',
    },
  },
})
