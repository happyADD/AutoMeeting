import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy config shared by both the dev server (vite dev) and the preview server
// (vite preview).  Without this, `vite preview` – which is used for CI E2E
// tests – would not forward /api requests to the backend, breaking the
// frontend-backend connection during tests.
// See Vite docs: https://vitejs.dev/config/server-options#server-proxy
//                https://vitejs.dev/config/preview-options#preview-proxy
const apiProxy = {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
  },
}

export default defineConfig({
  base: '/',
  plugins: [react()],
  server: {
    port: 5173,
    proxy: apiProxy,
  },
  // preview.proxy mirrors server.proxy so that `vite preview` (used in CI)
  // also routes /api requests to the backend, solving the
  // "frontend cannot connect to backend" issue.
  preview: {
    proxy: apiProxy,
  },
})
