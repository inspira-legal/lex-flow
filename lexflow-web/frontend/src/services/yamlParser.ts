// YAML/JSON parsing utility for workflow source code
// Uses js-yaml library for YAML parsing, native JSON.parse for JSON

import yaml from 'js-yaml'

export interface ParseResult<T> {
  success: boolean
  data?: T
  error?: string
}

export function parseWorkflowSource<T = unknown>(source: string): ParseResult<T> {
  const trimmed = source.trim()
  if (!trimmed) {
    return { success: false, error: 'Empty source' }
  }

  // Try JSON first (faster if it's valid JSON)
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      const data = JSON.parse(trimmed) as T
      return { success: true, data }
    } catch {
      // Not valid JSON, try YAML
    }
  }

  // Try YAML
  try {
    const data = yaml.load(trimmed) as T
    if (data === null || data === undefined) {
      return { success: false, error: 'Empty workflow' }
    }
    return { success: true, data }
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Parse failed'
    return { success: false, error: message }
  }
}
