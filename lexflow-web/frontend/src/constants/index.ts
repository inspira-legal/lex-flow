// Consolidated constants for LexFlow Web Frontend

import type { NodeType } from "../api/types";
import {
  getGrammar,
  getBranchColor,
  getNodeColor,
  getReporterColor,
  getControlFlowOpcodeSet,
  getBranchSlots,
  getCategories,
  getCategoryIcon,
} from "../services/grammar";

// Re-export grammar service functions for convenience
export {
  getBranchColor,
  getNodeColor,
  getReporterColor,
  getControlFlowOpcodeSet,
  getBranchSlots,
  getCategories,
  getCategoryIcon,
  getGrammar,
};

// Node layout dimensions (balanced square-ish proportions)
export const NODE_DIMENSIONS = {
  WIDTH: 110,
  HEIGHT: 70,
  MIN_HEIGHT: 70,
  EXPANDED_INPUT_HEIGHT: 30,
  SLOT_HEIGHT: 24,
  HEADER_HEIGHT: 32,
  PADDING: 8,
} as const;

// Canvas layout gaps
export const LAYOUT_GAPS = {
  HORIZONTAL: 60,
  VERTICAL: 40,
  WORKFLOW: 80,
} as const;

// Start node dimensions (from StartNode.tsx)
export const START_NODE_DIMENSIONS = {
  WIDTH: 140,
  HEIGHT: 60,
} as const;

// Canvas view defaults
export const CANVAS_DEFAULTS = {
  ZOOM: 1,
  MIN_ZOOM: 0.25,
  MAX_ZOOM: 2,
  PAN_X: 0,
  PAN_Y: 0,
} as const;

// Node type display labels (used for UI display)
export const NODE_TYPE_LABELS: Record<NodeType | string, string> = {
  control_flow: "Control Flow",
  data: "Data",
  io: "I/O",
  operator: "Operator",
  workflow_op: "Workflow",
  opcode: "Opcode",
};

// History stack size limit
export const MAX_UNDO_HISTORY = 50;
