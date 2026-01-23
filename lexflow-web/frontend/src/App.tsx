import { useEffect } from "react";
import { MainLayout } from "./components/layout";
import { Canvas } from "./components/visualization";
import { CodeEditor } from "./components/editor";
import { ExecutionPanel } from "./components/execution";
import { NodeEditorPanel } from "./components/node-editor";
import { NodePalette, DragPreview } from "./components/palette";
import { useWorkflowStore } from "./store";
import { useKeyboardShortcuts, useWorkflowParsing } from "./hooks";
import { useBackendProvider, supportsExamples } from "./providers";

export function App() {
  const { setExamples, setOpcodes } = useWorkflowStore();
  const provider = useBackendProvider();

  // Enable keyboard shortcuts
  useKeyboardShortcuts();

  // Parse workflow on source changes (runs regardless of editor visibility)
  useWorkflowParsing();

  // Load examples and opcodes on mount
  useEffect(() => {
    // Load opcodes from provider
    provider.listOpcodes().then(setOpcodes).catch(console.error);

    // Load examples if provider supports them
    if (supportsExamples(provider)) {
      provider.listExamples().then(setExamples).catch(console.error);
    }
  }, [setExamples, setOpcodes, provider]);

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
  );
}

export default App;
