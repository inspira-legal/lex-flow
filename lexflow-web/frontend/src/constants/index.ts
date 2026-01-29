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
} from "../services/grammar";

// Re-export grammar service functions for convenience
export {
  getBranchColor,
  getNodeColor,
  getReporterColor,
  getControlFlowOpcodeSet,
  getBranchSlots,
  getCategories,
  getGrammar,
};

// Node layout dimensions
export const NODE_DIMENSIONS = {
  WIDTH: 180,
  HEIGHT: 80,
  MIN_HEIGHT: 60,
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

// Control flow opcodes that have branch slots
// NOTE: Now sourced from grammar. Use getControlFlowOpcodeSet() for runtime access.
// This array is kept for backward compatibility with static imports.
export const CONTROL_FLOW_OPCODES = [
  "control_if",
  "control_if_else",
  "control_for",
  "control_while",
  "control_foreach",
  "control_try",
  "control_fork",
  "control_spawn",
  "control_async_foreach",
  "async_timeout",
  "control_with",
] as const;

// Node type display labels
export const NODE_TYPE_LABELS: Record<NodeType | string, string> = {
  control_flow: "Control Flow",
  data: "Data",
  io: "I/O",
  operator: "Operator",
  workflow_op: "Workflow",
  opcode: "Opcode",
};

// Node type colors (Scratch-inspired)
// NOTE: Now sourced from grammar. Use getNodeColor() for runtime access.
export const NODE_COLORS: Record<NodeType | string, string> = {
  control_flow: "#FF9500", // Orange - control
  data: "#4CAF50", // Green - data
  io: "#22D3EE", // Cyan - I/O
  operator: "#9C27B0", // Purple - math/operators
  workflow_op: "#E91E63", // Magenta - workflow calls
  opcode: "#64748B", // Slate - generic
};

// Reporter pill colors by category
// NOTE: Now sourced from grammar. Use getReporterColor() for runtime access.
export const REPORTER_COLORS: Record<string, string> = {
  data: "#4CAF50",
  operator: "#9C27B0",
  io: "#22D3EE",
  workflow: "#E91E63",
  default: "#64748B",
};

// History stack size limit
export const MAX_UNDO_HISTORY = 50;
