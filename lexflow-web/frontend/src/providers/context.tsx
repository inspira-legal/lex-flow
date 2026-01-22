// React context for BackendProvider injection

import { createContext, useContext, type ReactNode } from 'react'
import type { BackendProvider } from './types'

const BackendProviderContext = createContext<BackendProvider | null>(null)

interface BackendProviderWrapperProps {
  provider: BackendProvider
  children: ReactNode
}

export function BackendProviderWrapper({
  provider,
  children,
}: BackendProviderWrapperProps) {
  return (
    <BackendProviderContext.Provider value={provider}>
      {children}
    </BackendProviderContext.Provider>
  )
}

export function useBackendProvider(): BackendProvider {
  const provider = useContext(BackendProviderContext)
  if (!provider) {
    throw new Error(
      'useBackendProvider must be used within a BackendProviderWrapper'
    )
  }
  return provider
}
