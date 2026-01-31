import { useEffect } from "react";
import { MainLayout } from "./components/layout";
import { Canvas } from "./components/canvas";
import { CodeEditor } from "./components/editor";
import { ExecutionPanel } from "./components/execution";
import { NodeEditorPanel } from "./components/node-editor";
import { NodePalette, DragPreview } from "./components/palette";
import { ConfirmDialog, NewWorkflowModal, ExtractWorkflowModal } from "./components/ui";
import { useSelectionStore } from "./store";
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

// Global extract workflow modal connected to store
function GlobalExtractWorkflowModal() {
  const extractWorkflowModal = useUiStore((s) => s.extractWorkflowModal);
  const hideExtractWorkflowModal = useUiStore((s) => s.hideExtractWorkflowModal);
  const tree = useWorkflowStore((s) => s.tree);
  const extractToWorkflow = useWorkflowStore((s) => s.extractToWorkflow);
  const clearMultiSelection = useSelectionStore((s) => s.clearMultiSelection);
  const showConfirmDialog = useUiStore((s) => s.showConfirmDialog);

  // Get existing workflow names for validation
  const existingWorkflowNames = tree?.workflows.map((w) => w.name) ?? [];

  if (!extractWorkflowModal) return null;

  return (
    <ExtractWorkflowModal
      isOpen={extractWorkflowModal.isOpen}
      existingWorkflowNames={existingWorkflowNames}
      nodeIds={extractWorkflowModal.nodeIds}
      suggestedInputs={extractWorkflowModal.suggestedInputs}
      suggestedOutputs={extractWorkflowModal.suggestedOutputs}
      onConfirm={(data) => {
        const result = extractToWorkflow(
          extractWorkflowModal.nodeIds,
          extractWorkflowModal.workflowName,
          data.name,
          data.inputs,
          data.outputs,
          data.variables
        );
        if (result.success) {
          clearMultiSelection();
          hideExtractWorkflowModal();
        } else {
          // Show error dialog
          showConfirmDialog({
            title: "Extraction Failed",
            message: result.errors.join("\n"),
            confirmLabel: "OK",
            onConfirm: () => {},
          });
        }
      }}
      onCancel={hideExtractWorkflowModal}
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
      <GlobalExtractWorkflowModal />
    </>
  );
}

export default App;
