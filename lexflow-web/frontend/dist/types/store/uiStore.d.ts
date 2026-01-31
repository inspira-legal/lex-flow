import type { OpcodeInterface } from "../api/types";
import type { LayoutWorkflowGroup } from "../services/layout/LayoutService";
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
interface UiState {
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
    canvasContextMenu: {
        x: number;
        y: number;
        workflowName?: string;
    } | null;
    showCanvasContextMenu: (x: number, y: number, workflowName?: string) => void;
    hideCanvasContextMenu: () => void;
    createWorkflowModal: {
        isOpen: boolean;
    } | null;
    showCreateWorkflowModal: () => void;
    hideCreateWorkflowModal: () => void;
    extractWorkflowModal: {
        isOpen: boolean;
        nodeIds: string[];
        workflowName: string;
        suggestedInputs: string[];
        suggestedOutputs: string[];
    } | null;
    showExtractWorkflowModal: (nodeIds: string[], workflowName: string, suggestedInputs?: string[], suggestedOutputs?: string[]) => void;
    hideExtractWorkflowModal: () => void;
}
export declare const useUiStore: import("zustand").UseBoundStore<import("zustand").StoreApi<UiState>>;
export {};
