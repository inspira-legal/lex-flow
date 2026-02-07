// Factory for creating isolated Zustand stores for each editor instance

import { create, type StateCreator } from "zustand";
import { persist } from "zustand/middleware";
import type { WorkflowTree, ExampleInfo, OpcodeInterface, DetailedInput } from "../../api/types";
import * as WorkflowService from "../../services/workflow/WorkflowService";
import type { LayoutWorkflowGroup } from "../../services/layout/LayoutService";
import type { FormattedValue } from "../../api/types";

const MAX_HISTORY = 50;

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

// Slot position (absolute canvas coordinates)
export interface SlotPosition {
  x: number;
  y: number;
}

export interface NodeSlotPositions {
  input: SlotPosition;
  output: SlotPosition;
  branches: Record<string, SlotPosition>;
}

// Wire dragging info
export interface DraggingWire {
  sourceNodeId: string;
  sourcePort: "input" | "output";
  sourceX: number;
  sourceY: number;
  dragX: number;
  dragY: number;
  nearbyPort: {
    nodeId: string;
    port: "input" | "output";
    x: number;
    y: number;
  } | null;
  branchLabel?: string;
}

// Orphan node dragging info
export interface DraggingOrphan {
  nodeId: string;
  opcode: string;
  returnType: string | undefined;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
}

// Variable dragging info
export interface DraggingVariable {
  name: string;
  workflowName: string;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
}

// Workflow call dragging info
export interface DraggingWorkflowCall {
  workflowName: string;
  params: string[];
}

// Reporter selection info
export interface SelectedReporter {
  parentNodeId: string;
  inputPath: string[];
  reporterNodeId: string | undefined;
  opcode: string;
  inputs: Record<string, FormattedValue>;
}

// Selected connection info
export interface SelectedConnection {
  fromNodeId: string;
  toNodeId: string;
  label?: string;
}

// Types for web opcodes
export interface PendingPrompt {
  type: "input" | "select" | "confirm" | "button";
  prompt: string;
  options?: string[];
  message?: string;
  label?: string;
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

// Combined store state interface
export interface EditorStoreState {
  // === Workflow State ===
  source: string;
  setSource: (source: string, addToHistory?: boolean) => void;
  history: string[];
  historyIndex: number;
  canUndo: boolean;
  canRedo: boolean;
  undo: () => void;
  redo: () => void;
  tree: WorkflowTree | null;
  parseError: string | null;
  isParsing: boolean;
  setTree: (tree: WorkflowTree | null) => void;
  setParseError: (error: string | null) => void;
  setIsParsing: (isParsing: boolean) => void;
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
  updateWorkflowInterface: (
    workflowName: string,
    inputs: DetailedInput[],
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
  addDynamicBranch: (nodeId: string, branchPrefix: string) => boolean;
  removeDynamicBranch: (nodeId: string, branchName: string) => boolean;
  addDynamicInput: (nodeId: string, inputPrefix: string) => boolean;
  removeDynamicInput: (nodeId: string, inputName: string) => boolean;
  examples: ExampleInfo[];
  setExamples: (examples: ExampleInfo[]) => void;
  opcodes: OpcodeInterface[];
  setOpcodes: (opcodes: OpcodeInterface[]) => void;

  // === Execution State ===
  isExecuting: boolean;
  executionOutput: string;
  executionResult: unknown;
  executionError: string | null;
  workflowInputs: Record<string, unknown>;
  pendingPrompt: PendingPrompt | null;
  renderedContent: RenderedContent[];
  alerts: AlertItem[];
  progress: ProgressState | null;
  setIsExecuting: (isExecuting: boolean) => void;
  setExecutionOutput: (output: string) => void;
  appendExecutionOutput: (chunk: string) => void;
  setExecutionResult: (result: unknown) => void;
  setExecutionError: (error: string | null) => void;
  clearExecution: () => void;
  setWorkflowInput: (key: string, value: unknown) => void;
  clearWorkflowInputs: () => void;
  setPendingPrompt: (prompt: PendingPrompt | null) => void;
  addRenderedContent: (content: RenderedContent) => void;
  clearRenderedContent: () => void;
  addAlert: (alert: Omit<AlertItem, "id">) => void;
  removeAlert: (id: string) => void;
  setProgress: (progress: ProgressState | null) => void;

  // === UI State ===
  zoom: number;
  panX: number;
  panY: number;
  isDraggingWorkflow: boolean;
  setZoom: (zoom: number) => void;
  setPan: (x: number, y: number) => void;
  resetView: () => void;
  setIsDraggingWorkflow: (dragging: boolean) => void;
  isEditorOpen: boolean;
  isNodeEditorOpen: boolean;
  isPaletteOpen: boolean;
  isExecutionPanelOpen: boolean;
  toggleEditor: () => void;
  toggleNodeEditor: () => void;
  togglePalette: () => void;
  toggleExecutionPanel: () => void;
  openNodeEditor: () => void;
  closeNodeEditor: () => void;
  nodeStatus: Record<string, "idle" | "running" | "success" | "error">;
  setNodeStatus: (
    nodeId: string,
    status: "idle" | "running" | "success" | "error",
  ) => void;
  clearNodeStatuses: () => void;
  searchQuery: string;
  searchResults: string[];
  setSearchQuery: (query: string) => void;
  setSearchResults: (results: string[]) => void;
  workflowPositions: Record<string, { x: number; y: number }>;
  setWorkflowPosition: (name: string, x: number, y: number) => void;
  resetWorkflowPositions: () => void;
  draggingOpcode: OpcodeInterface | null;
  setDraggingOpcode: (opcode: OpcodeInterface | null) => void;
  draggingWire: DraggingWire | null;
  setDraggingWire: (wire: DraggingWire | null) => void;
  updateDraggingWire: (updates: Partial<DraggingWire>) => void;
  draggingOrphan: DraggingOrphan | null;
  setDraggingOrphan: (orphan: DraggingOrphan | null) => void;
  updateDraggingOrphanEnd: (toX: number, toY: number) => void;
  nodePositions: Record<string, { x: number; y: number }>;
  setNodePosition: (nodeId: string, x: number, y: number) => void;
  resetNodePositions: () => void;
  clearNodePosition: (nodeId: string) => void;
  layoutMode: "auto" | "free";
  setLayoutMode: (mode: "auto" | "free") => void;
  isDraggingNode: boolean;
  setIsDraggingNode: (dragging: boolean) => void;
  draggingVariable: DraggingVariable | null;
  setDraggingVariable: (v: DraggingVariable | null) => void;
  updateDraggingVariableEnd: (toX: number, toY: number) => void;
  draggingWorkflowCall: DraggingWorkflowCall | null;
  setDraggingWorkflowCall: (wc: DraggingWorkflowCall | null) => void;
  slotPositions: Record<string, NodeSlotPositions>;
  registerSlotPositions: (nodeId: string, positions: NodeSlotPositions) => void;
  unregisterSlotPositions: (nodeId: string) => void;
  layoutGroups: LayoutWorkflowGroup[];
  setLayoutGroups: (groups: LayoutWorkflowGroup[]) => void;
  canvasCenter: { x: number; y: number };
  setCanvasCenter: (x: number, y: number) => void;
  contextMenu: {
    nodeId: string;
    x: number;
    y: number;
    hasReporters: boolean;
    reportersExpanded: boolean;
    isOrphan: boolean;
  } | null;
  showContextMenu: (data: {
    nodeId: string;
    x: number;
    y: number;
    hasReporters: boolean;
    reportersExpanded: boolean;
    isOrphan: boolean;
  }) => void;
  hideContextMenu: () => void;
  expandedReporters: Record<string, boolean>;
  toggleReportersExpanded: (nodeId: string) => void;
  setReportersExpanded: (nodeId: string, expanded: boolean) => void;
  confirmDialog: {
    isOpen: boolean;
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    variant?: "default" | "danger";
    onConfirm: () => void;
    onCancel: () => void;
  } | null;
  showConfirmDialog: (options: {
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    variant?: "default" | "danger";
    onConfirm: () => void;
    onCancel?: () => void;
  }) => void;
  hideConfirmDialog: () => void;

  // === Selection State ===
  selectedNodeId: string | null;
  selectNode: (id: string | null) => void;
  selectedReporter: SelectedReporter | null;
  selectReporter: (reporter: SelectedReporter | null) => void;
  selectedConnection: SelectedConnection | null;
  selectConnection: (conn: SelectedConnection | null) => void;
  selectedStartNode: string | null;
  selectStartNode: (workflowName: string | null) => void;
  clearSelection: () => void;
}

// Store creation options
export interface CreateStoresOptions {
  instanceId: string;
  initialSource?: string;
  persistSource?: boolean;
}

// Create store state creator
function createEditorStoreState(options: CreateStoresOptions): StateCreator<EditorStoreState> {
  const { initialSource } = options;

  return (set, get) => ({
    // === Workflow State ===
    source: initialSource ?? DEFAULT_WORKFLOW,
    setSource: (source, addToHistory = true) => {
      const state = get();
      if (addToHistory && source !== state.source) {
        const newHistory = state.history.slice(0, state.historyIndex + 1);
        newHistory.push(source);
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
    history: [initialSource ?? DEFAULT_WORKFLOW],
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
    tree: null,
    parseError: null,
    isParsing: false,
    setTree: (tree) => set({ tree, parseError: null }),
    setParseError: (error) => set({ parseError: error, tree: null }),
    setIsParsing: (isParsing) => set({ isParsing }),
    deleteNode: (nodeId) => {
      const state = get();
      const result = WorkflowService.deleteNode(state.source, nodeId);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    addNode: (opcode, workflowName = "main") => {
      const state = get();
      const result = WorkflowService.addNode(state.source, opcode, workflowName);
      if (result.nodeId) {
        state.setSource(result.source);
      }
      return result.nodeId;
    },
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
    duplicateNode: (nodeId) => {
      const state = get();
      const result = WorkflowService.duplicateNode(state.source, nodeId);
      if (result.nodeId) {
        state.setSource(result.source);
      }
      return result.nodeId;
    },
    updateNodeInput: (nodeId, inputKey, newValue) => {
      const state = get();
      const result = WorkflowService.updateNodeInput(state.source, nodeId, inputKey, newValue);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    connectNodes: (fromNodeId, toNodeId) => {
      const state = get();
      const result = WorkflowService.connectNodes(state.source, fromNodeId, toNodeId);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    connectBranch: (fromNodeId, toNodeId, branchLabel) => {
      const state = get();
      const result = WorkflowService.connectBranch(state.source, fromNodeId, toNodeId, branchLabel);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    disconnectNode: (nodeId) => {
      const state = get();
      const result = WorkflowService.disconnectNode(state.source, nodeId);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    disconnectConnection: (fromNodeId, toNodeId, branchLabel) => {
      const state = get();
      const result = WorkflowService.disconnectConnection(state.source, fromNodeId, toNodeId, branchLabel);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
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
    updateReporterInput: (reporterNodeId, inputKey, newValue) => {
      if (!reporterNodeId) {
        return false;
      }
      return get().updateNodeInput(reporterNodeId, inputKey, newValue);
    },
    deleteReporter: (parentNodeId, inputPath) => {
      const state = get();
      const result = WorkflowService.deleteReporter(state.source, parentNodeId, inputPath);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    updateWorkflowInterface: (workflowName, inputs, outputs) => {
      const state = get();
      const result = WorkflowService.updateWorkflowInterface(state.source, workflowName, inputs, outputs);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    addVariable: (workflowName, name, defaultValue) => {
      const state = get();
      const result = WorkflowService.addVariable(state.source, workflowName, name, defaultValue);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    updateVariable: (workflowName, oldName, newName, newValue) => {
      const state = get();
      const result = WorkflowService.updateVariable(state.source, workflowName, oldName, newName, newValue);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    deleteVariable: (workflowName, name) => {
      const state = get();
      const result = WorkflowService.deleteVariable(state.source, workflowName, name);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    addDynamicBranch: (nodeId, branchPrefix) => {
      const state = get();
      const result = WorkflowService.addDynamicBranch(state.source, nodeId, branchPrefix);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    removeDynamicBranch: (nodeId, branchName) => {
      const state = get();
      const result = WorkflowService.removeDynamicBranch(state.source, nodeId, branchName);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    addDynamicInput: (nodeId, inputPrefix) => {
      const state = get();
      const result = WorkflowService.addDynamicInput(state.source, nodeId, inputPrefix);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    removeDynamicInput: (nodeId, inputName) => {
      const state = get();
      const result = WorkflowService.removeDynamicInput(state.source, nodeId, inputName);
      if (result.success) {
        state.setSource(result.source);
      }
      return result.success;
    },
    examples: [],
    setExamples: (examples) => set({ examples }),
    opcodes: [],
    setOpcodes: (opcodes) => set({ opcodes }),

    // === Execution State ===
    isExecuting: false,
    executionOutput: "",
    executionResult: null,
    executionError: null,
    workflowInputs: {},
    pendingPrompt: null,
    renderedContent: [],
    alerts: [],
    progress: null,
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

    // === UI State ===
    zoom: 1,
    panX: 0,
    panY: 0,
    isDraggingWorkflow: false,
    setZoom: (zoom) => set({ zoom: Math.max(0.25, Math.min(2, zoom)) }),
    setPan: (x, y) => set({ panX: x, panY: y }),
    resetView: () => set({ zoom: 1, panX: 0, panY: 0 }),
    setIsDraggingWorkflow: (dragging) => set({ isDraggingWorkflow: dragging }),
    isEditorOpen: false,
    isNodeEditorOpen: false,
    isPaletteOpen: false,
    isExecutionPanelOpen: true,
    toggleEditor: () => set((s) => ({ isEditorOpen: !s.isEditorOpen })),
    toggleNodeEditor: () => set((s) => ({ isNodeEditorOpen: !s.isNodeEditorOpen })),
    togglePalette: () => set((s) => ({ isPaletteOpen: !s.isPaletteOpen })),
    toggleExecutionPanel: () => set((s) => ({ isExecutionPanelOpen: !s.isExecutionPanelOpen })),
    openNodeEditor: () => set({ isNodeEditorOpen: true }),
    closeNodeEditor: () => set({ isNodeEditorOpen: false }),
    nodeStatus: {},
    setNodeStatus: (nodeId, status) =>
      set((s) => ({ nodeStatus: { ...s.nodeStatus, [nodeId]: status } })),
    clearNodeStatuses: () => set({ nodeStatus: {} }),
    searchQuery: "",
    searchResults: [],
    setSearchQuery: (query) => set({ searchQuery: query }),
    setSearchResults: (results) => set({ searchResults: results }),
    workflowPositions: {},
    setWorkflowPosition: (name, x, y) =>
      set((s) => ({
        workflowPositions: { ...s.workflowPositions, [name]: { x, y } },
      })),
    resetWorkflowPositions: () => set({ workflowPositions: {} }),
    draggingOpcode: null,
    setDraggingOpcode: (opcode) => set({ draggingOpcode: opcode }),
    draggingWire: null,
    setDraggingWire: (wire) => set({ draggingWire: wire }),
    updateDraggingWire: (updates) =>
      set((s) => ({
        draggingWire: s.draggingWire ? { ...s.draggingWire, ...updates } : null,
      })),
    draggingOrphan: null,
    setDraggingOrphan: (orphan) => set({ draggingOrphan: orphan }),
    updateDraggingOrphanEnd: (toX, toY) =>
      set((s) => ({
        draggingOrphan: s.draggingOrphan
          ? { ...s.draggingOrphan, toX, toY }
          : null,
      })),
    nodePositions: {},
    setNodePosition: (nodeId, x, y) =>
      set((s) => ({ nodePositions: { ...s.nodePositions, [nodeId]: { x, y } } })),
    resetNodePositions: () => set({ nodePositions: {} }),
    clearNodePosition: (nodeId) =>
      set((s) => {
        const { [nodeId]: _, ...rest } = s.nodePositions;
        return { nodePositions: rest };
      }),
    layoutMode: "free",
    setLayoutMode: (mode) => set({ layoutMode: mode }),
    isDraggingNode: false,
    setIsDraggingNode: (dragging) => set({ isDraggingNode: dragging }),
    draggingVariable: null,
    setDraggingVariable: (v) => set({ draggingVariable: v }),
    updateDraggingVariableEnd: (toX, toY) =>
      set((s) => ({
        draggingVariable: s.draggingVariable
          ? { ...s.draggingVariable, toX, toY }
          : null,
      })),
    draggingWorkflowCall: null,
    setDraggingWorkflowCall: (wc) => set({ draggingWorkflowCall: wc }),
    slotPositions: {},
    registerSlotPositions: (nodeId, positions) =>
      set((s) => ({
        slotPositions: { ...s.slotPositions, [nodeId]: positions },
      })),
    unregisterSlotPositions: (nodeId) =>
      set((s) => {
        const { [nodeId]: _, ...rest } = s.slotPositions;
        return { slotPositions: rest };
      }),
    layoutGroups: [],
    setLayoutGroups: (groups) => set({ layoutGroups: groups }),
    canvasCenter: { x: 400, y: 300 },
    setCanvasCenter: (x, y) => set({ canvasCenter: { x, y } }),
    contextMenu: null,
    showContextMenu: (data) => set({ contextMenu: data }),
    hideContextMenu: () => set({ contextMenu: null }),
    expandedReporters: {},
    toggleReportersExpanded: (nodeId) =>
      set((s) => ({
        expandedReporters: {
          ...s.expandedReporters,
          [nodeId]: !s.expandedReporters[nodeId],
        },
      })),
    setReportersExpanded: (nodeId, expanded) =>
      set((s) => ({
        expandedReporters: {
          ...s.expandedReporters,
          [nodeId]: expanded,
        },
      })),
    confirmDialog: null,
    showConfirmDialog: (options) =>
      set({
        confirmDialog: {
          isOpen: true,
          title: options.title,
          message: options.message,
          confirmLabel: options.confirmLabel,
          cancelLabel: options.cancelLabel,
          variant: options.variant,
          onConfirm: () => {
            options.onConfirm();
            set({ confirmDialog: null });
          },
          onCancel: () => {
            options.onCancel?.();
            set({ confirmDialog: null });
          },
        },
      }),
    hideConfirmDialog: () => set({ confirmDialog: null }),

    // === Selection State ===
    selectedNodeId: null,
    selectNode: (id) => set({ selectedNodeId: id }),
    selectedReporter: null,
    selectReporter: (reporter) => set({ selectedReporter: reporter }),
    selectedConnection: null,
    selectConnection: (conn) => set({ selectedConnection: conn }),
    selectedStartNode: null,
    selectStartNode: (workflowName) => set({ selectedStartNode: workflowName }),
    clearSelection: () =>
      set({
        selectedNodeId: null,
        selectedReporter: null,
        selectedConnection: null,
        selectedStartNode: null,
      }),
  });
}

// Type for the combined store
export type EditorStore = ReturnType<typeof createEditorStore>;

// Create a new isolated store
export function createEditorStore(options: CreateStoresOptions) {
  const { instanceId, persistSource = false } = options;

  if (persistSource) {
    return create<EditorStoreState>()(
      persist(createEditorStoreState(options), {
        name: `lexflow-editor-${instanceId}`,
        partialize: (state) => ({ source: state.source }),
      })
    );
  }

  return create<EditorStoreState>()(createEditorStoreState(options));
}
