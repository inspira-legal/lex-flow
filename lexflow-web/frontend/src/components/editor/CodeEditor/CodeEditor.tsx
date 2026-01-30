import Editor, { type Monaco } from "@monaco-editor/react"
import type { editor } from "monaco-editor"
import { useWorkflowStore } from "@/store"
import { useTheme } from "@/lib/theme"
import { useEffect, useRef } from "react"
import { cn } from "@/lib/cn"
import {
  editorContainerVariants,
  editorHeaderVariants,
  editorTitleVariants,
  editorStatusVariants,
  editorWrapperVariants,
} from "./styles"
import type { CodeEditorProps } from "./types"

export function CodeEditor({ className }: CodeEditorProps) {
  const { source, setSource, isParsing } = useWorkflowStore()
  const { theme } = useTheme()
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)
  const monacoRef = useRef<Monaco | null>(null)

  useEffect(() => {
    const handleGotoLine = (e: CustomEvent<{ line: number }>) => {
      const editor = editorRef.current
      if (editor) {
        const line = e.detail.line
        editor.revealLineInCenter(line)
        editor.setPosition({ lineNumber: line, column: 1 })
        editor.focus()
        editor.deltaDecorations(
          [],
          [
            {
              range: {
                startLineNumber: line,
                startColumn: 1,
                endLineNumber: line,
                endColumn: 1,
              },
              options: {
                isWholeLine: true,
                className: "highlighted-line",
                glyphMarginClassName: "highlighted-glyph",
              },
            },
          ]
        )
      }
    }

    window.addEventListener(
      "lexflow:goto-line",
      handleGotoLine as EventListener
    )
    return () => {
      window.removeEventListener(
        "lexflow:goto-line",
        handleGotoLine as EventListener
      )
    }
  }, [])

  useEffect(() => {
    if (monacoRef.current && editorRef.current) {
      const monaco = monacoRef.current
      const themeName = theme === "light" ? "lexflow-light" : "lexflow-dark"
      monaco.editor.setTheme(themeName)
    }
  }, [theme])

  const handleEditorMount = (
    editor: editor.IStandaloneCodeEditor,
    monaco: Monaco
  ) => {
    editorRef.current = editor
    monacoRef.current = monaco

    monaco.editor.defineTheme("lexflow-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#1e1e1e",
        "editor.lineHighlightBackground": "#2d2d2d",
      },
    })

    monaco.editor.defineTheme("lexflow-light", {
      base: "vs",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#fafafa",
        "editor.lineHighlightBackground": "#f0f0f0",
      },
    })

    const themeName = theme === "light" ? "lexflow-light" : "lexflow-dark"
    monaco.editor.setTheme(themeName)
  }

  return (
    <div className={cn(editorContainerVariants(), className)}>
      <div className={editorHeaderVariants()}>
        <span className={editorTitleVariants()}>Editor</span>
        {isParsing && <span className={editorStatusVariants()}>Parsing...</span>}
      </div>
      <div className={editorWrapperVariants()}>
        <Editor
          height="100%"
          language="yaml"
          theme={theme === "light" ? "lexflow-light" : "lexflow-dark"}
          value={source}
          onChange={(value) => setSource(value || "")}
          onMount={handleEditorMount}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: "on",
            scrollBeyondLastLine: false,
            wordWrap: "on",
            tabSize: 2,
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  )
}
