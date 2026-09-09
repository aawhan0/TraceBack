import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/health': 'http://127.0.0.1:8000',
      '/scenarios': 'http://127.0.0.1:8000',
      '/investigations': 'http://127.0.0.1:8000',
      '/experiments': 'http://127.0.0.1:8000',
      '/runs': 'http://127.0.0.1:8000',
    },
  },
})
