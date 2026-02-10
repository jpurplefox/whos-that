import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './i18n/index.ts'
import { initAnalytics } from './services/analytics'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary.tsx'

initAnalytics()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
