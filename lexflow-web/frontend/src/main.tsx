import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/variables.css'
import { App } from './App'
import { BackendProviderWrapper, createLexFlowProvider } from './providers'
import { getConfig } from './config'

// Create the default LexFlow provider with environment configuration
const config = getConfig()
const provider = createLexFlowProvider({
  apiBaseUrl: config.apiBaseUrl,
  wsUrl: config.wsUrl,
  supportsExamples: true,
  supportsWebSocket: true,
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BackendProviderWrapper provider={provider}>
      <App />
    </BackendProviderWrapper>
  </StrictMode>,
)
