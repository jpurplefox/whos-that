import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'serve-auth-callback',
      configureServer(server) {
        server.middlewares.use('/auth/callback', (_req, res) => {
          const filePath = join(server.config.root, 'public', 'auth', 'callback', 'index.html')
          const html = readFileSync(filePath, 'utf-8')
          res.setHeader('Content-Type', 'text/html')
          res.statusCode = 200
          res.end(html)
        })
      },
    },
  ],
  server: {
    proxy: {
      '/api': {
        target: process.env.API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
  },
})
