import { useEffect, useRef } from 'react'
import { useWorkflowStore } from '../store'
import { api } from '../api'

// Hook to handle workflow parsing - runs regardless of editor visibility
export function useWorkflowParsing() {
  const { source, setTree, setParseError, setIsParsing } = useWorkflowStore()
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    debounceRef.current = setTimeout(async () => {
      setIsParsing(true)
      try {
        const result = await api.parse(source)
        if (result.success && result.tree) {
          setTree(result.tree)
        } else {
          setParseError(result.error || 'Parse failed')
        }
      } catch (err) {
        setParseError(err instanceof Error ? err.message : 'Parse failed')
      } finally {
        setIsParsing(false)
      }
    }, 500)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [source, setTree, setParseError, setIsParsing])
}
