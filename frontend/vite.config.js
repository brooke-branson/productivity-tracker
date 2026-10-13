import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Proxy API calls through Vite so the browser stays same-origin.
// The FastAPI app has no CORS middleware, and this keeps that backend untouched.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/tasks': 'http://127.0.0.1:8000',
      '/healthz': 'http://127.0.0.1:8000',
      '/weekly-summary': 'http://127.0.0.1:8000',
      '/historical-search': 'http://127.0.0.1:8000',
    },
  },
})
