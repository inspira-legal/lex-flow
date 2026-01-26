// Execution state management with Zustand

import { create } from "zustand";

// Types for web opcodes
export interface PendingPrompt {
  type: "input" | "select" | "confirm" | "button";
  prompt: string;
  options?: string[]; // for select
  message?: string; // for confirm
  label?: string; // for button
}

export interface RenderedContent {
  type: "html" | "markdown" | "table" | "image";
  content: string | Record<string, unknown>[] | { src: string; alt: string };
}

export interface AlertItem {
  id: string;
  message: string;
  variant: "info" | "success" | "warning" | "error";
}

export interface ProgressState {
  value: number;
  max: number;
  label: string;
}

interface ExecutionState {
  // Execution status
  isExecuting: boolean;
  executionOutput: string;
  executionResult: unknown;
  executionError: string | null;

  // Workflow inputs for execution
  workflowInputs: Record<string, unknown>;

  // Web opcode state
  pendingPrompt: PendingPrompt | null;
  renderedContent: RenderedContent[];
  alerts: AlertItem[];
  progress: ProgressState | null;

  // Actions
  setIsExecuting: (isExecuting: boolean) => void;
  setExecutionOutput: (output: string) => void;
  appendExecutionOutput: (chunk: string) => void;
  setExecutionResult: (result: unknown) => void;
  setExecutionError: (error: string | null) => void;
  clearExecution: () => void;
  setWorkflowInput: (key: string, value: unknown) => void;
  clearWorkflowInputs: () => void;

  // Web opcode actions
  setPendingPrompt: (prompt: PendingPrompt | null) => void;
  addRenderedContent: (content: RenderedContent) => void;
  clearRenderedContent: () => void;
  addAlert: (alert: Omit<AlertItem, "id">) => void;
  removeAlert: (id: string) => void;
  setProgress: (progress: ProgressState | null) => void;
}

export const useExecutionStore = create<ExecutionState>((set) => ({
  // Initial state
  isExecuting: false,
  executionOutput: "",
  executionResult: null,
  executionError: null,
  workflowInputs: {},

  // Web opcode initial state
  pendingPrompt: null,
  renderedContent: [],
  alerts: [],
  progress: null,

  // Actions
  setIsExecuting: (isExecuting) => set({ isExecuting }),
  setExecutionOutput: (output) => set({ executionOutput: output }),
  appendExecutionOutput: (chunk) =>
    set((state) => ({ executionOutput: state.executionOutput + chunk })),
  setExecutionResult: (result) => set({ executionResult: result }),
  setExecutionError: (error) => set({ executionError: error }),
  clearExecution: () =>
    set({
      executionOutput: "",
      executionResult: null,
      executionError: null,
      pendingPrompt: null,
      renderedContent: [],
      alerts: [],
      progress: null,
    }),
  setWorkflowInput: (key, value) =>
    set((state) => ({
      workflowInputs: { ...state.workflowInputs, [key]: value },
    })),
  clearWorkflowInputs: () => set({ workflowInputs: {} }),

  // Web opcode actions
  setPendingPrompt: (prompt) => set({ pendingPrompt: prompt }),
  addRenderedContent: (content) =>
    set((state) => ({
      renderedContent: [...state.renderedContent, content],
    })),
  clearRenderedContent: () => set({ renderedContent: [] }),
  addAlert: (alert) =>
    set((state) => ({
      alerts: [...state.alerts, { ...alert, id: crypto.randomUUID() }],
    })),
  removeAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
    })),
  setProgress: (progress) => set({ progress }),
}));
