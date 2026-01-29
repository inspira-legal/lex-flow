// UI state management with Zustand
// Manages visual/interaction state (canvas, panels, dragging)
// Selection state moved to selectionStore.ts

import { create } from "zustand";
import type { OpcodeInterface } from "../api/types";
import type { LayoutWorkflowGroup } from "../services/layout/LayoutService";

// Slot position (absolute canvas coordinates)
export interface SlotPosition {
  x: number;
  y: number;
}

export interface NodeSlotPositions {
  input: SlotPosition;
  output: SlotPosition;
  branches: Record<string, SlotPosition>; // "THEN", "ELSE", "TRY", etc.
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
  branchLabel?: string; // For branch connections: "THEN", "ELSE", "BODY", "TRY", "CATCH1", "FINALLY"
}

// Orphan node dragging info (for orphan-to-reporter conversion)
export interface DraggingOrphan {
  nodeId: string;
  opcode: string;
  returnType: string | undefined;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
}

// Variable dragging info (for dragging variables from palette to input slots)
export interface DraggingVariable {
  name: string;
  workflowName: string;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
}

// Workflow call dragging info (for dragging workflow calls from palette)
export interface DraggingWorkflowCall {
  workflowName: string;
  params: string[];
}

interface UiState {
  // Canvas
  zoom: number;
  panX: number;
  panY: number;
  isDraggingWorkflow: boolean;
  setZoom: (zoom: number) => void;
  setPan: (x: number, y: number) => void;
  resetView: () => void;
  setIsDraggingWorkflow: (dragging: boolean) => void;

  // Panels
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

  // Node execution status (for visualization)
  nodeStatus: Record<string, "idle" | "running" | "success" | "error">;
  setNodeStatus: (
    nodeId: string,
    status: "idle" | "running" | "success" | "error",
  ) => void;
  clearNodeStatuses: () => void;

  // Node search
  searchQuery: string;
  searchResults: string[];
  setSearchQuery: (query: string) => void;
  setSearchResults: (results: string[]) => void;

  // Workflow positions (for dragging)
  workflowPositions: Record<string, { x: number; y: number }>;
  setWorkflowPosition: (name: string, x: number, y: number) => void;
  resetWorkflowPositions: () => void;

  // Drag-drop from palette
  draggingOpcode: OpcodeInterface | null;
  setDraggingOpcode: (opcode: OpcodeInterface | null) => void;

  // Wire dragging for connections
  draggingWire: DraggingWire | null;
  setDraggingWire: (wire: DraggingWire | null) => void;
  updateDraggingWire: (updates: Partial<DraggingWire>) => void;

  // Orphan dragging for orphan-to-reporter conversion
  draggingOrphan: DraggingOrphan | null;
  setDraggingOrphan: (orphan: DraggingOrphan | null) => void;
  updateDraggingOrphanEnd: (toX: number, toY: number) => void;

  // Node positions (offsets from auto-layout)
  nodePositions: Record<string, { x: number; y: number }>;
  setNodePosition: (nodeId: string, x: number, y: number) => void;
  resetNodePositions: () => void;
  clearNodePosition: (nodeId: string) => void;

  // Layout mode
  layoutMode: "auto" | "free";
  setLayoutMode: (mode: "auto" | "free") => void;

  // Node dragging (prevent canvas pan during node drag)
  isDraggingNode: boolean;
  setIsDraggingNode: (dragging: boolean) => void;

  // Variable dragging for palette to input slot
  draggingVariable: DraggingVariable | null;
  setDraggingVariable: (v: DraggingVariable | null) => void;
  updateDraggingVariableEnd: (toX: number, toY: number) => void;

  // Workflow call dragging from palette
  draggingWorkflowCall: DraggingWorkflowCall | null;
  setDraggingWorkflowCall: (wc: DraggingWorkflowCall | null) => void;

  // Slot positions registry (single source of truth for wire endpoints)
  slotPositions: Record<string, NodeSlotPositions>;
  registerSlotPositions: (nodeId: string, positions: NodeSlotPositions) => void;
  unregisterSlotPositions: (nodeId: string) => void;

  // Layout groups (for drop target detection)
  layoutGroups: LayoutWorkflowGroup[];
  setLayoutGroups: (groups: LayoutWorkflowGroup[]) => void;

  // Canvas center (for coordinate transformation)
  canvasCenter: { x: number; y: number };
  setCanvasCenter: (x: number, y: number) => void;
}

export const useUiStore = create<UiState>((set) => ({
  // Canvas
  zoom: 1,
  panX: 0,
  panY: 0,
  isDraggingWorkflow: false,
  setZoom: (zoom) => set({ zoom: Math.max(0.25, Math.min(2, zoom)) }),
  setPan: (x, y) => set({ panX: x, panY: y }),
  resetView: () => set({ zoom: 1, panX: 0, panY: 0 }),
  setIsDraggingWorkflow: (dragging) => set({ isDraggingWorkflow: dragging }),

  // Panels
  isEditorOpen: false,
  isNodeEditorOpen: false,
  isPaletteOpen: false,
  isExecutionPanelOpen: true,
  toggleEditor: () => set((s) => ({ isEditorOpen: !s.isEditorOpen })),
  toggleNodeEditor: () =>
    set((s) => ({ isNodeEditorOpen: !s.isNodeEditorOpen })),
  togglePalette: () => set((s) => ({ isPaletteOpen: !s.isPaletteOpen })),
  toggleExecutionPanel: () =>
    set((s) => ({ isExecutionPanelOpen: !s.isExecutionPanelOpen })),
  openNodeEditor: () => set({ isNodeEditorOpen: true }),
  closeNodeEditor: () => set({ isNodeEditorOpen: false }),

  // Node status
  nodeStatus: {},
  setNodeStatus: (nodeId, status) =>
    set((s) => ({ nodeStatus: { ...s.nodeStatus, [nodeId]: status } })),
  clearNodeStatuses: () => set({ nodeStatus: {} }),

  // Node search
  searchQuery: "",
  searchResults: [],
  setSearchQuery: (query) => set({ searchQuery: query }),
  setSearchResults: (results) => set({ searchResults: results }),

  // Workflow positions
  workflowPositions: {},
  setWorkflowPosition: (name, x, y) =>
    set((s) => ({
      workflowPositions: { ...s.workflowPositions, [name]: { x, y } },
    })),
  resetWorkflowPositions: () => set({ workflowPositions: {} }),

  // Drag-drop from palette
  draggingOpcode: null,
  setDraggingOpcode: (opcode) => set({ draggingOpcode: opcode }),

  // Wire dragging for connections
  draggingWire: null,
  setDraggingWire: (wire) => set({ draggingWire: wire }),
  updateDraggingWire: (updates) =>
    set((s) => ({
      draggingWire: s.draggingWire ? { ...s.draggingWire, ...updates } : null,
    })),

  // Orphan dragging for orphan-to-reporter conversion
  draggingOrphan: null,
  setDraggingOrphan: (orphan) => set({ draggingOrphan: orphan }),
  updateDraggingOrphanEnd: (toX, toY) =>
    set((s) => ({
      draggingOrphan: s.draggingOrphan
        ? { ...s.draggingOrphan, toX, toY }
        : null,
    })),

  // Node positions (offsets from auto-layout)
  nodePositions: {},
  setNodePosition: (nodeId, x, y) =>
    set((s) => ({ nodePositions: { ...s.nodePositions, [nodeId]: { x, y } } })),
  resetNodePositions: () => set({ nodePositions: {} }),
  clearNodePosition: (nodeId) =>
    set((s) => {
      const { [nodeId]: _, ...rest } = s.nodePositions;
      return { nodePositions: rest };
    }),

  // Layout mode
  layoutMode: "free",
  setLayoutMode: (mode) => set({ layoutMode: mode }),

  // Node dragging
  isDraggingNode: false,
  setIsDraggingNode: (dragging) => set({ isDraggingNode: dragging }),

  // Variable dragging
  draggingVariable: null,
  setDraggingVariable: (v) => set({ draggingVariable: v }),
  updateDraggingVariableEnd: (toX, toY) =>
    set((s) => ({
      draggingVariable: s.draggingVariable
        ? { ...s.draggingVariable, toX, toY }
        : null,
    })),

  // Workflow call dragging
  draggingWorkflowCall: null,
  setDraggingWorkflowCall: (wc) => set({ draggingWorkflowCall: wc }),

  // Slot positions registry
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

  // Layout groups
  layoutGroups: [],
  setLayoutGroups: (groups) => set({ layoutGroups: groups }),

  // Canvas center
  canvasCenter: { x: 400, y: 300 },
  setCanvasCenter: (x, y) => set({ canvasCenter: { x, y } }),
}));
