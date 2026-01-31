import { useEffect } from "react";
import { MainLayout } from "./components/layout";
import { Canvas } from "./components/canvas";
import { CodeEditor } from "./components/editor";
import { ExecutionPanel } from "./components/execution";
import { NodeEditorPanel } from "./components/node-editor";
import { NodePalette, DragPreview } from "./components/palette";
import { ConfirmDialog, NewWorkflowModal } from "./components/ui";
import { useWorkflowStore, useUiStore } from "./store";
import { useKeyboardShortcuts, useWorkflowParsing } from "./hooks";
import { useBackendProvider, supportsExamples } from "./providers";

// Global confirm dialog connected to store
function GlobalConfirmDialog() {
  const confirmDialog = useUiStore((s) => s.confirmDialog);

  if (!confirmDialog) return null;

  return (
    <ConfirmDialog
      isOpen={confirmDialog.isOpen}
      title={confirmDialog.title}
      message={confirmDialog.message}
      confirmLabel={confirmDialog.confirmLabel}
      cancelLabel={confirmDialog.cancelLabel}
      variant={confirmDialog.variant}
      onConfirm={confirmDialog.onConfirm}
      onCancel={confirmDialog.onCancel}
    />
  );
}

// Global new workflow modal connected to store
function GlobalNewWorkflowModal() {
  const createWorkflowModal = useUiStore((s) => s.createWorkflowModal);
  const hideCreateWorkflowModal = useUiStore((s) => s.hideCreateWorkflowModal);
  const tree = useWorkflowStore((s) => s.tree);
  const addWorkflow = useWorkflowStore((s) => s.addWorkflow);

  // Get existing workflow names for validation
  const existingWorkflowNames = tree?.workflows.map((w) => w.name) ?? [];

  if (!createWorkflowModal) return null;

  return (
    <NewWorkflowModal
      isOpen={createWorkflowModal.isOpen}
      existingWorkflowNames={existingWorkflowNames}
      onConfirm={(data) => {
        addWorkflow(data.name, data.inputs, data.outputs, data.variables);
        hideCreateWorkflowModal();
      }}
      onCancel={hideCreateWorkflowModal}
    />
  );
}

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
      <GlobalConfirmDialog />
      <GlobalNewWorkflowModal />
    </>
  );
}

export default App;
