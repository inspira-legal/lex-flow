import { useEffect } from 'react'
import { MainLayout } from './components/layout'
import { Canvas } from './components/visualization'
import { CodeEditor } from './components/editor'
import { ExecutionPanel } from './components/execution'
import { NodeEditorPanel } from './components/node-editor'
import { NodePalette, DragPreview } from './components/palette'
import { useWorkflowStore } from './store'
import { useKeyboardShortcuts } from './hooks'
import { api } from './api'

export function App() {
  const { setExamples, setOpcodes } = useWorkflowStore()

  // Enable keyboard shortcuts
  useKeyboardShortcuts()

  // Load examples and opcodes on mount
  useEffect(() => {
    api.listExamples().then(setExamples).catch(console.error)
    api.listOpcodes().then(setOpcodes).catch(console.error)
  }, [setExamples, setOpcodes])

  return (
    <>
      <MainLayout
        canvas={<Canvas />}
        editor={<CodeEditor />}
        executionPanel={<ExecutionPanel />}
        nodeEditor={<NodeEditorPanel />}
        palette={<NodePalette />}
      />
      <DragPreview />
    </>
  )
}

export default App
