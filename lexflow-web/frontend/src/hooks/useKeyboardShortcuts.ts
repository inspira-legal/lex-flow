import { useEffect } from "react";
import { useUiStore, useWorkflowStore, useSelectionStore } from "../store";

export function useKeyboardShortcuts() {
  const {
    closeNodeEditor,
    isNodeEditorOpen,
    isPaletteOpen,
    togglePalette,
    toggleEditor,
    toggleExecutionPanel,
  } = useUiStore();
  const {
    undo,
    redo,
    canUndo,
    canRedo,
    deleteNode,
    duplicateNode,
  } = useWorkflowStore();
  const { selectNode, selectedNodeId, clearSelection } = useSelectionStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs (except undo/redo)
      const target = e.target as HTMLElement;
      const isInput =
        target.tagName === "INPUT" || target.tagName === "TEXTAREA";

      // Handle Escape in inputs
      if (isInput && e.key === "Escape") {
        target.blur();
        return;
      }

      // Ctrl/Cmd shortcuts (work even in Monaco editor context)
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case "z":
            // Undo (but let Monaco handle its own undo in editor)
            if (!isInput && !isMonacoEditor(target)) {
              e.preventDefault();
              if (e.shiftKey) {
                if (canRedo) redo();
              } else {
                if (canUndo) undo();
              }
            }
            break;
          case "y":
            // Redo
            if (!isInput && !isMonacoEditor(target)) {
              e.preventDefault();
              if (canRedo) redo();
            }
            break;
          case "b":
            // Toggle editor panel
            if (!isInput) {
              e.preventDefault();
              toggleEditor();
            }
            break;
          case "e":
            // Toggle execution panel
            if (!isInput) {
              e.preventDefault();
              toggleExecutionPanel();
            }
            break;
          case "p":
            // Toggle palette
            if (!isInput) {
              e.preventDefault();
              togglePalette();
            }
            break;
          case "0":
            // Reset zoom
            if (!isInput) {
              e.preventDefault();
              useUiStore.getState().resetView();
            }
            break;
          case "d":
            // Duplicate node
            if (!isInput && selectedNodeId && selectedNodeId !== "start") {
              e.preventDefault();
              duplicateNode(selectedNodeId);
            }
            break;
        }
        return;
      }

      // Non-modifier shortcuts (skip if in input)
      if (isInput) return;

      // Escape - close panels/deselect
      if (e.key === "Escape") {
        if (isNodeEditorOpen) {
          closeNodeEditor();
          clearSelection();
        } else if (isPaletteOpen) {
          togglePalette();
        } else if (selectedNodeId) {
          clearSelection();
        }
        return;
      }

      // Delete/Backspace
      if (e.key === "Delete" || e.key === "Backspace") {
        if (selectedNodeId && selectedNodeId !== "start") {
          useUiStore.getState().showConfirmDialog({
            title: "Delete Node",
            message: `Delete node "${selectedNodeId}"? This action can be undone with Ctrl+Z.`,
            confirmLabel: "Delete",
            variant: "danger",
            onConfirm: () => {
              deleteNode(selectedNodeId);
              clearSelection();
              closeNodeEditor();
            },
          });
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    closeNodeEditor,
    isNodeEditorOpen,
    isPaletteOpen,
    togglePalette,
    toggleEditor,
    toggleExecutionPanel,
    selectNode,
    selectedNodeId,
    clearSelection,
    undo,
    redo,
    canUndo,
    canRedo,
    deleteNode,
    duplicateNode,
  ]);
}

function isMonacoEditor(element: HTMLElement): boolean {
  // Check if element is inside Monaco editor
  return element.closest(".monaco-editor") !== null;
}
