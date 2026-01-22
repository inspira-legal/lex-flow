import { useRef, useCallback } from 'react'
import { useWorkflowStore } from '../store'

interface ExecuteMessage {
  type: 'start'
  workflow: string
  inputs?: Record<string, unknown>
  include_metrics?: boolean
}

interface OutputMessage {
  type: 'output'
  line: string
}

interface CompleteMessage {
  type: 'complete'
  result: unknown
  metrics?: Record<string, unknown>
}

interface ErrorMessage {
  type: 'error'
  message: string
}

type ServerMessage = OutputMessage | CompleteMessage | ErrorMessage

export function useWebSocketExecution() {
  const wsRef = useRef<WebSocket | null>(null)
  const {
    setIsExecuting,
    appendExecutionOutput,
    setExecutionResult,
    setExecutionError,
    clearExecution,
  } = useWorkflowStore()

  const execute = useCallback(
    (workflow: string, inputs?: Record<string, unknown>, includeMetrics?: boolean) => {
      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close()
      }

      clearExecution()
      setIsExecuting(true)

      // Determine WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws/execute`

      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        const message: ExecuteMessage = {
          type: 'start',
          workflow,
          inputs,
          include_metrics: includeMetrics,
        }
        ws.send(JSON.stringify(message))
      }

      ws.onmessage = (event) => {
        try {
          const data: ServerMessage = JSON.parse(event.data)

          switch (data.type) {
            case 'output':
              appendExecutionOutput(data.line + '\n')
              break

            case 'complete':
              setExecutionResult(data.result)
              setIsExecuting(false)
              ws.close()
              break

            case 'error':
              setExecutionError(data.message)
              setIsExecuting(false)
              ws.close()
              break
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onerror = () => {
        setExecutionError('WebSocket connection failed')
        setIsExecuting(false)
      }

      ws.onclose = () => {
        wsRef.current = null
      }
    },
    [clearExecution, setIsExecuting, appendExecutionOutput, setExecutionResult, setExecutionError]
  )

  const cancel = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
      setIsExecuting(false)
    }
  }, [setIsExecuting])

  return { execute, cancel }
}
