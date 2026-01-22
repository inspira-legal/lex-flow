import Editor, { type Monaco } from '@monaco-editor/react'
import type { editor } from 'monaco-editor'
import { useWorkflowStore } from '../../store'
import { api } from '../../api'
import { useEffect, useRef } from 'react'
import styles from './CodeEditor.module.css'

export function CodeEditor() {
  const { source, setSource, setTree, setParseError, setIsParsing, isParsing } =
    useWorkflowStore()
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)

  // Parse on source change (debounced)
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

  // Listen for goto-line events from the node editor
  useEffect(() => {
    const handleGotoLine = (e: CustomEvent<{ line: number }>) => {
      const editor = editorRef.current
      if (editor) {
        const line = e.detail.line
        editor.revealLineInCenter(line)
        editor.setPosition({ lineNumber: line, column: 1 })
        editor.focus()
        // Highlight the line briefly
        editor.deltaDecorations([], [
          {
            range: {
              startLineNumber: line,
              startColumn: 1,
              endLineNumber: line,
              endColumn: 1,
            },
            options: {
              isWholeLine: true,
              className: 'highlighted-line',
              glyphMarginClassName: 'highlighted-glyph',
            },
          },
        ])
      }
    }

    window.addEventListener('lexflow:goto-line', handleGotoLine as EventListener)
    return () => {
      window.removeEventListener('lexflow:goto-line', handleGotoLine as EventListener)
    }
  }, [])

  const handleEditorMount = (editor: editor.IStandaloneCodeEditor, monaco: Monaco) => {
    editorRef.current = editor

    // Add custom CSS for line highlighting
    monaco.editor.defineTheme('lexflow-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#0F172A',
        'editor.lineHighlightBackground': '#1E293B',
      },
    })
    monaco.editor.setTheme('lexflow-dark')
  }

  return (
    <div className={styles.editor}>
      <div className={styles.header}>
        <span className={styles.title}>Editor</span>
        {isParsing && <span className={styles.status}>Parsing...</span>}
      </div>
      <div className={styles.editorWrapper}>
        <Editor
          height="100%"
          language="yaml"
          theme="vs-dark"
          value={source}
          onChange={(value) => setSource(value || '')}
          onMount={handleEditorMount}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            tabSize: 2,
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  )
}
