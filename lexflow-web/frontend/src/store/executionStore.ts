// Execution state management with Zustand

import { create } from "zustand";

interface ExecutionState {
  // Execution status
  isExecuting: boolean;
  executionOutput: string;
  executionResult: unknown;
  executionError: string | null;

  // Workflow inputs for execution
  workflowInputs: Record<string, unknown>;

  // Actions
  setIsExecuting: (isExecuting: boolean) => void;
  setExecutionOutput: (output: string) => void;
  appendExecutionOutput: (chunk: string) => void;
  setExecutionResult: (result: unknown) => void;
  setExecutionError: (error: string | null) => void;
  clearExecution: () => void;
  setWorkflowInput: (key: string, value: unknown) => void;
  clearWorkflowInputs: () => void;
}

export const useExecutionStore = create<ExecutionState>((set) => ({
  // Initial state
  isExecuting: false,
  executionOutput: "",
  executionResult: null,
  executionError: null,
  workflowInputs: {},

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
    }),
  setWorkflowInput: (key, value) =>
    set((state) => ({
      workflowInputs: { ...state.workflowInputs, [key]: value },
    })),
  clearWorkflowInputs: () => set({ workflowInputs: {} }),
}));
