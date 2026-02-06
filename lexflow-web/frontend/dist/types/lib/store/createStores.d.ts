import type { WorkflowTree, ExampleInfo, OpcodeInterface, DetailedInput } from "../../api/types";
import type { LayoutWorkflowGroup } from "../../services/layout/LayoutService";
import type { FormattedValue } from "../../api/types";
export interface SlotPosition {
    x: number;
    y: number;
}
export interface NodeSlotPositions {
    input: SlotPosition;
    output: SlotPosition;
    branches: Record<string, SlotPosition>;
}
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
export interface DraggingOrphan {
    nodeId: string;
    opcode: string;
    returnType: string | undefined;
    fromX: number;
    fromY: number;
    toX: number;
    toY: number;
}
export interface DraggingVariable {
    name: string;
    workflowName: string;
    fromX: number;
    fromY: number;
    toX: number;
    toY: number;
}
export interface DraggingWorkflowCall {
    workflowName: string;
    params: string[];
}
export interface SelectedReporter {
    parentNodeId: string;
    inputPath: string[];
    reporterNodeId: string | undefined;
    opcode: string;
    inputs: Record<string, FormattedValue>;
}
export interface SelectedConnection {
    fromNodeId: string;
    toNodeId: string;
    label?: string;
}
export interface PendingPrompt {
    type: "input" | "select" | "confirm" | "button";
    prompt: string;
    options?: string[];
    message?: string;
    label?: string;
}
export interface RenderedContent {
    type: "html" | "markdown" | "table" | "image";
    content: string | Record<string, unknown>[] | {
        src: string;
        alt: string;
    };
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
export interface EditorStoreState {
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
    addWorkflowCallNode: (workflowName: string, params: string[], targetWorkflow?: string) => string | null;
    duplicateNode: (nodeId: string) => string | null;
    updateNodeInput: (nodeId: string, inputKey: string, newValue: string) => boolean;
    connectNodes: (fromNodeId: string, toNodeId: string) => boolean;
    connectBranch: (fromNodeId: string, toNodeId: string, branchLabel: string) => boolean;
    disconnectNode: (nodeId: string) => boolean;
    disconnectConnection: (fromNodeId: string, toNodeId: string, branchLabel?: string) => boolean;
    convertOrphanToReporter: (orphanNodeId: string, targetNodeId: string, inputKey: string) => boolean;
    updateReporterInput: (reporterNodeId: string, inputKey: string, newValue: string) => boolean;
    deleteReporter: (parentNodeId: string, inputPath: string[]) => boolean;
    updateWorkflowInterface: (workflowName: string, inputs: DetailedInput[], outputs: string[]) => boolean;
    addVariable: (workflowName: string, name: string, defaultValue: unknown) => boolean;
    updateVariable: (workflowName: string, oldName: string, newName: string, newValue: unknown) => boolean;
    deleteVariable: (workflowName: string, name: string) => boolean;
    addDynamicBranch: (nodeId: string, branchPrefix: string) => boolean;
    removeDynamicBranch: (nodeId: string, branchName: string) => boolean;
    addDynamicInput: (nodeId: string, inputPrefix: string) => boolean;
    removeDynamicInput: (nodeId: string, inputName: string) => boolean;
    examples: ExampleInfo[];
    setExamples: (examples: ExampleInfo[]) => void;
    opcodes: OpcodeInterface[];
    setOpcodes: (opcodes: OpcodeInterface[]) => void;
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
    setNodeStatus: (nodeId: string, status: "idle" | "running" | "success" | "error") => void;
    clearNodeStatuses: () => void;
    searchQuery: string;
    searchResults: string[];
    setSearchQuery: (query: string) => void;
    setSearchResults: (results: string[]) => void;
    workflowPositions: Record<string, {
        x: number;
        y: number;
    }>;
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
    nodePositions: Record<string, {
        x: number;
        y: number;
    }>;
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
    canvasCenter: {
        x: number;
        y: number;
    };
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
export interface CreateStoresOptions {
    instanceId: string;
    initialSource?: string;
    persistSource?: boolean;
}
export type EditorStore = ReturnType<typeof createEditorStore>;
export declare function createEditorStore(options: CreateStoresOptions): import("zustand").UseBoundStore<import("zustand").StoreApi<EditorStoreState>>;
