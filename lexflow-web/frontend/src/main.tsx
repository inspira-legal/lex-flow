import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./styles/variables.css"
import "./styles/index.css"
import { App } from "./App"
import { ThemeProvider } from "./lib/theme"
import { BackendProviderWrapper, createLexFlowProvider } from "./providers"
import { getConfig } from "./config"

const config = getConfig()
const provider = createLexFlowProvider({
  apiBaseUrl: config.apiBaseUrl,
  wsUrl: config.wsUrl,
  supportsExamples: true,
  supportsWebSocket: true,
})

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <BackendProviderWrapper provider={provider}>
        <App />
      </BackendProviderWrapper>
    </ThemeProvider>
  </StrictMode>
)
