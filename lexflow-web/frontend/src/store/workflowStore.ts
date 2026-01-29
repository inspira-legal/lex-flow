// Workflow state management with Zustand

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { WorkflowTree, ExampleInfo, OpcodeInterface } from "../api/types";
import * as WorkflowService from "../services/workflow/WorkflowService";

const MAX_HISTORY = 50;

interface WorkflowState {
  // Source code
  source: string;
  setSource: (source: string, addToHistory?: boolean) => void;

  // History for undo/redo
  history: string[];
  historyIndex: number;
  canUndo: boolean;
  canRedo: boolean;
  undo: () => void;
  redo: () => void;

  // Parsed tree
  tree: WorkflowTree | null;
  parseError: string | null;
  isParsing: boolean;
  setTree: (tree: WorkflowTree | null) => void;
  setParseError: (error: string | null) => void;
  setIsParsing: (isParsing: boolean) => void;

  // Node operations (pure - no selection side effects)
  deleteNode: (nodeId: string) => boolean;
  addNode: (opcode: OpcodeInterface, workflowName?: string) => string | null;
  addWorkflowCallNode: (
    workflowName: string,
    params: string[],
    targetWorkflow?: string,
  ) => string | null;
  duplicateNode: (nodeId: string) => string | null;
  updateNodeInput: (
    nodeId: string,
    inputKey: string,
    newValue: string,
  ) => boolean;
  connectNodes: (fromNodeId: string, toNodeId: string) => boolean;
  connectBranch: (
    fromNodeId: string,
    toNodeId: string,
    branchLabel: string,
  ) => boolean;
  disconnectNode: (nodeId: string) => boolean;
  disconnectConnection: (
    fromNodeId: string,
    toNodeId: string,
    branchLabel?: string,
  ) => boolean;
  convertOrphanToReporter: (
    orphanNodeId: string,
    targetNodeId: string,
    inputKey: string,
  ) => boolean;
  updateReporterInput: (
    reporterNodeId: string,
    inputKey: string,
    newValue: string,
  ) => boolean;
  deleteReporter: (parentNodeId: string, inputPath: string[]) => boolean;

  // Variable and interface operations
  updateWorkflowInterface: (
    workflowName: string,
    inputs: string[],
    outputs: string[],
  ) => boolean;
  addVariable: (
    workflowName: string,
    name: string,
    defaultValue: unknown,
  ) => boolean;
  updateVariable: (
    workflowName: string,
    oldName: string,
    newName: string,
    newValue: unknown,
  ) => boolean;
  deleteVariable: (workflowName: string, name: string) => boolean;

  // Dynamic branch/input operations
  addDynamicBranch: (nodeId: string, branchPrefix: string) => boolean;
  removeDynamicBranch: (nodeId: string, branchName: string) => boolean;
  addDynamicInput: (nodeId: string, inputPrefix: string) => boolean;
  removeDynamicInput: (nodeId: string, inputName: string) => boolean;

  // Examples
  examples: ExampleInfo[];
  setExamples: (examples: ExampleInfo[]) => void;

  // Opcodes catalog
  opcodes: OpcodeInterface[];
  setOpcodes: (opcodes: OpcodeInterface[]) => void;

  // Execution
  isExecuting: boolean;
  executionOutput: string;
  executionResult: unknown;
  executionError: string | null;
  setIsExecuting: (isExecuting: boolean) => void;
  setExecutionOutput: (output: string) => void;
  appendExecutionOutput: (chunk: string) => void;
  setExecutionResult: (result: unknown) => void;
  setExecutionError: (error: string | null) => void;
  clearExecution: () => void;

  // Inputs for execution
  workflowInputs: Record<string, unknown>;
  setWorkflowInput: (key: string, value: unknown) => void;
  clearWorkflowInputs: () => void;
}

const DEFAULT_WORKFLOW = `workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        next: hello
      hello:
        opcode: io_print
        inputs:
          MESSAGE: { literal: "Hello, LexFlow!" }
`;

export const useWorkflowStore = create<WorkflowState>()(
  persist(
    (set, get) => ({
      // Source
      source: DEFAULT_WORKFLOW,
      setSource: (source, addToHistory = true) => {
        const state = get();
        if (addToHistory && source !== state.source) {
          // Add to history
          const newHistory = state.history.slice(0, state.historyIndex + 1);
          newHistory.push(source);
          // Limit history size
          if (newHistory.length > MAX_HISTORY) {
            newHistory.shift();
          }
          set({
            source,
            history: newHistory,
            historyIndex: newHistory.length - 1,
            canUndo: newHistory.length > 1,
            canRedo: false,
          });
        } else {
          set({ source });
        }
      },

      // History
      history: [DEFAULT_WORKFLOW],
      historyIndex: 0,
      canUndo: false,
      canRedo: false,

      undo: () => {
        const state = get();
        if (state.historyIndex > 0) {
          const newIndex = state.historyIndex - 1;
          set({
            source: state.history[newIndex],
            historyIndex: newIndex,
            canUndo: newIndex > 0,
            canRedo: true,
          });
        }
      },

      redo: () => {
        const state = get();
        if (state.historyIndex < state.history.length - 1) {
          const newIndex = state.historyIndex + 1;
          set({
            source: state.history[newIndex],
            historyIndex: newIndex,
            canUndo: true,
            canRedo: newIndex < state.history.length - 1,
          });
        }
      },

      // Parsed tree
      tree: null,
      parseError: null,
      isParsing: false,
      setTree: (tree) => set({ tree, parseError: null }),
      setParseError: (error) => set({ parseError: error, tree: null }),
      setIsParsing: (isParsing) => set({ isParsing }),

      // Node operations (pure - no selection side effects)
      deleteNode: (nodeId) => {
        const state = get();
        const result = WorkflowService.deleteNode(state.source, nodeId);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Add a new node to a workflow
      addNode: (opcode, workflowName = "main") => {
        const state = get();
        const result = WorkflowService.addNode(state.source, opcode, workflowName);
        if (result.nodeId) {
          state.setSource(result.source);
        }
        return result.nodeId;
      },

      // Add a workflow_call node with ARG inputs
      addWorkflowCallNode: (workflowName, params, targetWorkflow = "main") => {
        const state = get();
        const result = WorkflowService.addWorkflowCallNode(
          state.source,
          workflowName,
          params,
          targetWorkflow,
        );
        if (result.nodeId) {
          state.setSource(result.source);
        }
        return result.nodeId;
      },

      // Duplicate an existing node
      duplicateNode: (nodeId) => {
        const state = get();
        const result = WorkflowService.duplicateNode(state.source, nodeId);
        if (result.nodeId) {
          state.setSource(result.source);
        }
        return result.nodeId;
      },

      // Update a node input value
      updateNodeInput: (nodeId, inputKey, newValue) => {
        const state = get();
        const result = WorkflowService.updateNodeInput(state.source, nodeId, inputKey, newValue);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Connect two nodes (set fromNodeId.next = toNodeId)
      connectNodes: (fromNodeId, toNodeId) => {
        const state = get();
        const result = WorkflowService.connectNodes(state.source, fromNodeId, toNodeId);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Connect a branch (set branch: toNodeId in the appropriate branch slot)
      connectBranch: (fromNodeId, toNodeId, branchLabel) => {
        const state = get();
        const result = WorkflowService.connectBranch(state.source, fromNodeId, toNodeId, branchLabel);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Disconnect a node (set its next: to null)
      disconnectNode: (nodeId) => {
        const state = get();
        const result = WorkflowService.disconnectNode(state.source, nodeId);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Convert an orphan node to a reporter by linking it to a target node's input
      // Note: Type compatibility check moved to caller (UI layer)
      convertOrphanToReporter: (orphanNodeId, targetNodeId, inputKey) => {
        const state = get();
        const result = WorkflowService.convertOrphanToReporter(
          state.source,
          orphanNodeId,
          targetNodeId,
          inputKey,
        );
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Update a reporter's input value (reporters are nodes, so we just use updateNodeInput logic)
      updateReporterInput: (reporterNodeId, inputKey, newValue) => {
        console.log(
          "[updateReporterInput] reporterNodeId:",
          reporterNodeId,
          "key:",
          inputKey,
          "value:",
          newValue,
        );

        if (!reporterNodeId) {
          console.warn("[updateReporterInput] No reporter node ID provided");
          return false;
        }

        // Reporter nodes are just nodes, so use the same logic as updateNodeInput
        return get().updateNodeInput(reporterNodeId, inputKey, newValue);
      },

      // Delete a reporter (replace with a literal placeholder)
      deleteReporter: (parentNodeId, inputPath) => {
        const state = get();
        const result = WorkflowService.deleteReporter(state.source, parentNodeId, inputPath);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Update workflow interface (inputs/outputs)
      updateWorkflowInterface: (workflowName, inputs, outputs) => {
        const state = get();
        const result = WorkflowService.updateWorkflowInterface(state.source, workflowName, inputs, outputs);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Add a new variable to a workflow
      addVariable: (workflowName, name, defaultValue) => {
        const state = get();
        const result = WorkflowService.addVariable(state.source, workflowName, name, defaultValue);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Update an existing variable
      updateVariable: (workflowName, oldName, newName, newValue) => {
        const state = get();
        const result = WorkflowService.updateVariable(state.source, workflowName, oldName, newName, newValue);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Disconnect a specific connection between two nodes
      disconnectConnection: (fromNodeId, toNodeId, branchLabel) => {
        const state = get();
        const result = WorkflowService.disconnectConnection(state.source, fromNodeId, toNodeId, branchLabel);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Delete a variable from a workflow
      deleteVariable: (workflowName, name) => {
        const state = get();
        const result = WorkflowService.deleteVariable(state.source, workflowName, name);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Add a dynamic branch to a node (e.g., CATCH2 for try, BRANCH3 for fork)
      addDynamicBranch: (nodeId, branchPrefix) => {
        const state = get();
        const result = WorkflowService.addDynamicBranch(state.source, nodeId, branchPrefix);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Remove a dynamic branch from a node
      removeDynamicBranch: (nodeId, branchName) => {
        const state = get();
        const result = WorkflowService.removeDynamicBranch(state.source, nodeId, branchName);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Add a dynamic input to a node (e.g., ARG2 for workflow_call)
      addDynamicInput: (nodeId, inputPrefix) => {
        const state = get();
        const result = WorkflowService.addDynamicInput(state.source, nodeId, inputPrefix);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Remove a dynamic input from a node
      removeDynamicInput: (nodeId, inputName) => {
        const state = get();
        const result = WorkflowService.removeDynamicInput(state.source, nodeId, inputName);
        if (result.success) {
          state.setSource(result.source);
        }
        return result.success;
      },

      // Examples
      examples: [],
      setExamples: (examples) => set({ examples }),

      // Opcodes
      opcodes: [],
      setOpcodes: (opcodes) => set({ opcodes }),

      // Execution
      isExecuting: false,
      executionOutput: "",
      executionResult: null,
      executionError: null,
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

      // Inputs
      workflowInputs: {},
      setWorkflowInput: (key, value) =>
        set((state) => ({
          workflowInputs: { ...state.workflowInputs, [key]: value },
        })),
      clearWorkflowInputs: () => set({ workflowInputs: {} }),
    }),
    {
      name: "lexflow-workflow",
      // Only persist the source code, not transient state
      partialize: (state) => ({ source: state.source }),
    },
  ),
);
