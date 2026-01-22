// Backend Provider Types
// Abstraction layer for different backend implementations

import type {
  ParseResponse,
  ValidateResponse,
  ExecuteResponse,
  ExampleInfo,
  ExampleContent,
  OpcodeInterface,
} from '../api/types'

export interface BackendConfig {
  apiBaseUrl: string              // e.g., '/api' or 'https://remote.example.com/api'
  wsUrl?: string                  // WebSocket URL (auto-derived if not set)
  supportsExamples?: boolean      // Whether backend supports examples endpoint
  supportsWebSocket?: boolean     // Whether backend supports WebSocket execution
}

export interface BackendProvider {
  name: string
  config: BackendConfig

  // Required methods
  listOpcodes(): Promise<OpcodeInterface[]>
  executeWorkflow(
    source: string,
    inputs?: Record<string, unknown>,
    includeMetrics?: boolean
  ): Promise<ExecuteResponse>
  getWebSocketUrl(): string | null

  // Client-side parsing (no backend needed)
  parseWorkflow(source: string): Promise<ParseResponse>

  // Optional methods
  validateWorkflow?(source: string): Promise<ValidateResponse>
  listExamples?(): Promise<ExampleInfo[]>
  getExample?(path: string): Promise<ExampleContent>
}

// Type guard for checking if provider supports examples
export function supportsExamples(
  provider: BackendProvider
): provider is BackendProvider & {
  listExamples: () => Promise<ExampleInfo[]>
  getExample: (path: string) => Promise<ExampleContent>
} {
  return (
    typeof provider.listExamples === 'function' &&
    typeof provider.getExample === 'function'
  )
}

// Type guard for checking if provider supports validation
export function supportsValidation(
  provider: BackendProvider
): provider is BackendProvider & {
  validateWorkflow: (source: string) => Promise<ValidateResponse>
} {
  return typeof provider.validateWorkflow === 'function'
}
