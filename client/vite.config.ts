import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
  ],
  resolve: {
    extensions: ['.js', '.ts', '.jsx', '.tsx', '.json']
  },
  server: {
    host: true, // ← 讓 Vite 接受外部訪問（必要）
    allowedHosts: ['.ngrok-free.app', '.trycloudflare.com'],
    port: 5173, // 默認的端口
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      }
    },
    cors: true
  },
});