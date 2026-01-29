// Selection state management with Zustand
// Unified store for all selection-related state

import { create } from "zustand";
import type { FormattedValue } from "../api/types";

// Reporter selection info
export interface SelectedReporter {
  parentNodeId: string;
  inputPath: string[]; // Path to reach this reporter (e.g., ['condition'] or ['condition', 'left'])
  reporterNodeId: string | undefined; // The actual reporter node's ID (for editing/finding)
  opcode: string;
  inputs: Record<string, FormattedValue>;
}

// Selected connection info
export interface SelectedConnection {
  fromNodeId: string;
  toNodeId: string;
  label?: string; // "THEN", "ELSE", "BODY", "TRY", "CATCH", "FINALLY", etc.
}

interface SelectionState {
  // Node selection
  selectedNodeId: string | null;
  selectNode: (id: string | null) => void;

  // Reporter selection
  selectedReporter: SelectedReporter | null;
  selectReporter: (reporter: SelectedReporter | null) => void;

  // Connection selection
  selectedConnection: SelectedConnection | null;
  selectConnection: (conn: SelectedConnection | null) => void;

  // Start node selection (for editing workflow variables/interface)
  selectedStartNode: string | null;
  selectStartNode: (workflowName: string | null) => void;

  // Clear all selections
  clearSelection: () => void;
}

export const useSelectionStore = create<SelectionState>((set) => ({
  // Node selection
  selectedNodeId: null,
  selectNode: (id) => set({ selectedNodeId: id }),

  // Reporter selection
  selectedReporter: null,
  selectReporter: (reporter) => set({ selectedReporter: reporter }),

  // Connection selection
  selectedConnection: null,
  selectConnection: (conn) => set({ selectedConnection: conn }),

  // Start node selection
  selectedStartNode: null,
  selectStartNode: (workflowName) => set({ selectedStartNode: workflowName }),

  // Clear all selections
  clearSelection: () =>
    set({
      selectedNodeId: null,
      selectedReporter: null,
      selectedConnection: null,
      selectedStartNode: null,
    }),
}));
