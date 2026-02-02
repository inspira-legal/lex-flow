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

/**
 * Mount a LexFlow Editor instance to a DOM element.
 *
 * @param container - DOM element or CSS selector string
 * @param options - Editor configuration options
 * @param options.initialSource - Initial workflow YAML/JSON source
 * @param options.executionUrl - Base URL for API endpoints (default: "/api")
 * @param options.websocketUrl - WebSocket URL for streaming execution
 * @param options.backendProvider - Custom backend provider implementation
 * @param options.theme - Theme preset ("light", "dark", "system") or config object
 * @param options.lite - Use textarea fallback instead of Monaco editor
 * @param options.showCodeEditor - Show code editor panel (default: true)
 * @param options.showPalette - Show node palette (default: true)
 * @param options.showExecutionPanel - Show execution output panel (default: true)
 * @param options.showNodeEditor - Show node editor panel (default: true)
 * @param options.onSourceChange - Callback when workflow source changes
 * @param options.onExecute - Callback when execution completes
 * @param options.onError - Callback when an error occurs
 * @param options.onReady - Callback when editor is ready
 * @param options.onSave - Callback when save button clicked, receives (source, metadata)
 * @param options.showSaveButton - Show save button (default: true if onSave provided)
 * @param options.saveButtonLabel - Custom label for save button (default: "Save")
 * @param options.showExamples - Show examples dropdown (default: true, auto-hides if empty)
 * @param options.opcodesUrl - Custom URL for opcodes endpoint
 * @param options.opcodeAdapter - Transform function for opcode API response
 * @param options.executeOverride - Custom execution function, bypasses normal flow
 * @returns EditorInstance with methods to control the editor
 *
 * @example
 * // Basic usage
 * const editor = LexFlow.mount('#editor');
 *
 * @example
 * // With save callback
 * const editor = LexFlow.mount('#editor', {
 *   onSave: async (source, metadata) => {
 *     await fetch('/api/save', { method: 'POST', body: source });
 *   },
 *   saveButtonLabel: 'Save to Cloud'
 * });
 *
 * @example
 * // With custom opcode endpoint and adapter
 * const editor = LexFlow.mount('#editor', {
 *   opcodesUrl: 'https://my-api.com/nodes',
 *   opcodeAdapter: (raw) => raw.operations.map(op => ({
 *     name: op.op_name,
 *     description: op.desc,
 *     parameters: op.args.map(a => ({
 *       name: a.name,
 *       type: a.type,
 *       required: !a.optional
 *     }))
 *   }))
 * });
 *
 * @example
 * // With execution override
 * const editor = LexFlow.mount('#editor', {
 *   executeOverride: async (source, inputs) => ({
 *     success: true,
 *     output: 'Custom execution result!',
 *     result: { custom: true }
 *   })
 * });
 */
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
