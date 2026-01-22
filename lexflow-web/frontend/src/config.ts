// Environment configuration for the frontend
// Uses Vite environment variables

export interface AppConfig {
  apiBaseUrl: string
  wsUrl?: string
}

export function getConfig(): AppConfig {
  return {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
    wsUrl: import.meta.env.VITE_WS_URL || undefined,
  }
}
