// Vanilla JavaScript mount API for LexFlow Editor

import { createRoot, type Root } from "react-dom/client";
import { createElement, type RefObject, createRef } from "react";
import { LexFlowEditor, type LexFlowEditorHandle } from "./components/LexFlowEditor";
import type { MountOptions, EditorInstance, ExecuteResult, ThemeOption } from "./types";

// Import styles for bundling
import "../styles/variables.css";
import "../styles/index.css";

interface MountedEditor {
  root: Root;
  editorRef: RefObject<LexFlowEditorHandle | null>;
  container: HTMLElement;
  instanceId: string;
}

// Store for mounted instances
const mountedEditors = new Map<string, MountedEditor>();

// Generate unique instance ID
let instanceCounter = 0;
function generateInstanceId(): string {
  return `lexflow-vanilla-${++instanceCounter}-${Date.now().toString(36)}`;
}

// Resolve container from selector or element
function resolveContainer(container: HTMLElement | string | undefined): HTMLElement {
  if (!container) {
    throw new Error("Container is required");
  }

  if (typeof container === "string") {
    const element = document.querySelector(container);
    if (!element) {
      throw new Error(`Container not found: ${container}`);
    }
    return element as HTMLElement;
  }

  return container;
}

// Mount editor to DOM
export function mount(
  container: HTMLElement | string,
  options: Omit<MountOptions, "container"> = {}
): EditorInstance {
  const containerElement = resolveContainer(container);
  const instanceId = generateInstanceId();

  // Create React ref for imperative handle
  const editorRef = createRef<LexFlowEditorHandle>();

  // Create React root
  const root = createRoot(containerElement);

  // Render editor
  root.render(
    createElement(LexFlowEditor, {
      ...options,
      instanceId,
      ref: editorRef,
    })
  );

  // Store mounted instance
  mountedEditors.set(instanceId, {
    root,
    editorRef,
    container: containerElement,
    instanceId,
  });

  // Return editor instance API
  const instance: EditorInstance = {
    getSource: () => {
      return editorRef.current?.getSource() ?? "";
    },

    setSource: (source: string) => {
      editorRef.current?.setSource(source);
    },

    execute: async (inputs?: Record<string, unknown>): Promise<ExecuteResult> => {
      if (!editorRef.current) {
        return { success: false, error: "Editor not initialized" };
      }
      return editorRef.current.execute(inputs);
    },

    setTheme: (theme: ThemeOption) => {
      editorRef.current?.setTheme(theme);
    },

    getTheme: () => {
      // Theme state is managed internally
      return "dark"; // Default
    },

    toggleCodeEditor: () => {
      editorRef.current?.toggleCodeEditor();
    },

    togglePalette: () => {
      editorRef.current?.togglePalette();
    },

    toggleExecutionPanel: () => {
      editorRef.current?.toggleExecutionPanel();
    },

    destroy: () => {
      const mounted = mountedEditors.get(instanceId);
      if (mounted) {
        mounted.root.unmount();
        mountedEditors.delete(instanceId);
      }
    },
  };

  return instance;
}

// Unmount all editors
export function unmountAll(): void {
  for (const [id, mounted] of mountedEditors) {
    mounted.root.unmount();
    mountedEditors.delete(id);
  }
}

// Get mounted instance count
export function getMountedCount(): number {
  return mountedEditors.size;
}

// Default export for UMD
export default {
  mount,
  unmountAll,
  getMountedCount,
};
