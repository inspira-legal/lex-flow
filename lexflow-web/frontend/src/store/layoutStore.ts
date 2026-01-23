// Layout state management with Zustand
// Manages node positions, slot positions, and layout mode

import { create } from "zustand";

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

interface LayoutState {
  // Node positions (offsets from auto-layout)
  nodePositions: Record<string, { x: number; y: number }>;
  setNodePosition: (nodeId: string, x: number, y: number) => void;
  resetNodePositions: () => void;
  clearNodePosition: (nodeId: string) => void;

  // Workflow group positions
  workflowPositions: Record<string, { x: number; y: number }>;
  setWorkflowPosition: (name: string, x: number, y: number) => void;
  resetWorkflowPositions: () => void;

  // Layout mode
  layoutMode: "auto" | "free";
  setLayoutMode: (mode: "auto" | "free") => void;

  // Slot positions registry (single source of truth for wire endpoints)
  slotPositions: Record<string, NodeSlotPositions>;
  registerSlotPositions: (nodeId: string, positions: NodeSlotPositions) => void;
  unregisterSlotPositions: (nodeId: string) => void;
}

export const useLayoutStore = create<LayoutState>((set) => ({
  // Node positions
  nodePositions: {},
  setNodePosition: (nodeId, x, y) =>
    set((s) => ({ nodePositions: { ...s.nodePositions, [nodeId]: { x, y } } })),
  resetNodePositions: () => set({ nodePositions: {} }),
  clearNodePosition: (nodeId) =>
    set((s) => {
      const { [nodeId]: _, ...rest } = s.nodePositions;
      return { nodePositions: rest };
    }),

  // Workflow positions
  workflowPositions: {},
  setWorkflowPosition: (name, x, y) =>
    set((s) => ({
      workflowPositions: { ...s.workflowPositions, [name]: { x, y } },
    })),
  resetWorkflowPositions: () => set({ workflowPositions: {} }),

  // Layout mode
  layoutMode: "auto",
  setLayoutMode: (mode) => set({ layoutMode: mode }),

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
}));
