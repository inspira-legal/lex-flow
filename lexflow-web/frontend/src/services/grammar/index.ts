/**
 * Grammar service for loading and caching the LexFlow grammar schema.
 *
 * The grammar is fetched from the API on first use and cached.
 * Until loaded, fallback values are used.
 */

import type { Grammar } from "../../types/grammar";
import {
  getBranchColor as grammarGetBranchColor,
  getNodeColor as grammarGetNodeColor,
  getReporterColor as grammarGetReporterColor,
  getControlFlowOpcodes,
} from "../../types/grammar";

// Cached grammar instance
let _grammar: Grammar | null = null;
let _isLoading = false;
let _loadPromise: Promise<Grammar> | null = null;

// Fallback grammar for use before API loads
const FALLBACK_GRAMMAR: Grammar = {
  version: "1.0",
  categories: [
    { id: "control", prefix: "control_", label: "Control", color: "#FF9500", icon: "⟳" },
    { id: "data", prefix: "data_", label: "Data", color: "#4CAF50", icon: "📦" },
    { id: "io", prefix: "io_", label: "I/O", color: "#22D3EE", icon: "📤" },
    { id: "operator", prefix: "operator_", label: "Operators", color: "#9C27B0", icon: "⚡" },
    { id: "list", prefix: "list_", label: "Lists", color: "#3B82F6", icon: "📋" },
    { id: "dict", prefix: "dict_", label: "Dicts", color: "#F59E0B", icon: "📖" },
    { id: "string", prefix: "string_", label: "Strings", color: "#F472B6", icon: "📝" },
    { id: "math", prefix: "math_", label: "Math", color: "#8B5CF6", icon: "🔢" },
    { id: "workflow", prefix: "workflow_", label: "Workflow", color: "#E91E63", icon: "🔗" },
  ],
  constructs: [
    {
      opcode: "control_if",
      display_name: "If",
      ast_class: "If",
      category: "control",
      description: "Execute branch if condition is true.",
      inputs: [{ name: "CONDITION", type: "expression", label: "Condition", value_type: "bool", required: true }],
      branches: [{ name: "THEN", label: "Then", color: "#66BB6A", required: true }],
    },
    {
      opcode: "control_if_else",
      display_name: "If-Else",
      ast_class: "If",
      category: "control",
      description: "Execute then-branch if condition is true, else-branch otherwise.",
      inputs: [{ name: "CONDITION", type: "expression", label: "Condition", value_type: "bool", required: true }],
      branches: [
        { name: "THEN", label: "Then", color: "#66BB6A", required: true },
        { name: "ELSE", label: "Else", color: "#EF5350", required: true },
      ],
    },
    {
      opcode: "control_while",
      display_name: "While",
      ast_class: "While",
      category: "control",
      description: "Repeat body while condition is true.",
      inputs: [{ name: "CONDITION", type: "expression", label: "Condition", value_type: "bool", required: true }],
      branches: [{ name: "BODY", label: "Body", color: "#22D3EE", required: true }],
    },
    {
      opcode: "control_for",
      display_name: "For",
      ast_class: "For",
      category: "control",
      description: "For loop with counter variable.",
      inputs: [],
      branches: [{ name: "BODY", label: "Body", color: "#22D3EE", required: true }],
    },
    {
      opcode: "control_foreach",
      display_name: "ForEach",
      ast_class: "ForEach",
      category: "control",
      description: "Iterate over each item in a collection.",
      inputs: [],
      branches: [{ name: "BODY", label: "Body", color: "#22D3EE", required: true }],
    },
    {
      opcode: "control_try",
      display_name: "Try",
      ast_class: "Try",
      category: "control",
      description: "Exception handling with try/catch/finally.",
      inputs: [],
      branches: [
        { name: "TRY", label: "Try", color: "#3B82F6", required: true },
        { name: "CATCH1", label: "Catch", color: "#F87171", required: false },
        { name: "FINALLY", label: "Finally", color: "#FACC15", required: false },
      ],
      dynamic_branches: true,
    },
  ],
  branch_colors: {
    THEN: "#34D399",
    ELSE: "#F87171",
    BODY: "#22D3EE",
    TRY: "#3B82F6",
    CATCH: "#F87171",
    FINALLY: "#FACC15",
    ON_TIMEOUT: "#FACC15",
    BRANCH: "#9C27B0",
    default: "#9C27B0",
  },
  node_colors: {
    control_flow: "#FF9500",
    data: "#4CAF50",
    io: "#22D3EE",
    operator: "#9C27B0",
    workflow_op: "#E91E63",
    opcode: "#64748B",
  },
  reporter_colors: {
    data: "#4CAF50",
    operator: "#9C27B0",
    io: "#22D3EE",
    workflow: "#E91E63",
    default: "#64748B",
  },
};

/**
 * Load the grammar from the API.
 */
export async function loadGrammar(): Promise<Grammar> {
  if (_grammar) {
    return _grammar;
  }

  if (_loadPromise) {
    return _loadPromise;
  }

  _isLoading = true;
  _loadPromise = fetch("/api/grammar")
    .then((res) => {
      if (!res.ok) {
        throw new Error(`Failed to load grammar: ${res.statusText}`);
      }
      return res.json();
    })
    .then((data: Grammar) => {
      _grammar = data;
      _isLoading = false;
      return data;
    })
    .catch((err) => {
      console.warn("Failed to load grammar from API, using fallback:", err);
      _grammar = FALLBACK_GRAMMAR;
      _isLoading = false;
      return FALLBACK_GRAMMAR;
    });

  return _loadPromise;
}

/**
 * Get the cached grammar (or fallback if not loaded).
 */
export function getGrammar(): Grammar {
  return _grammar || FALLBACK_GRAMMAR;
}

/**
 * Check if grammar has been loaded from API.
 */
export function isGrammarLoaded(): boolean {
  return _grammar !== null;
}

/**
 * Check if grammar is currently loading.
 */
export function isGrammarLoading(): boolean {
  return _isLoading;
}

/**
 * Get branch color by name (uses cached grammar).
 */
export function getBranchColor(branchName: string): string {
  return grammarGetBranchColor(getGrammar(), branchName);
}

/**
 * Get node color by type (uses cached grammar).
 */
export function getNodeColor(nodeType: string): string {
  return grammarGetNodeColor(getGrammar(), nodeType);
}

/**
 * Get reporter color by opcode (uses cached grammar).
 */
export function getReporterColor(opcode: string): string {
  return grammarGetReporterColor(getGrammar(), opcode);
}

/**
 * Get the set of control flow opcodes (uses cached grammar).
 */
export function getControlFlowOpcodeSet(): Set<string> {
  return getControlFlowOpcodes(getGrammar());
}

/**
 * Get branch slots for a control flow opcode.
 */
export function getBranchSlots(
  opcode: string,
  connectedBranches: string[],
): Array<{ name: string; connected: boolean }> {
  const grammar = getGrammar();
  const construct = grammar.constructs.find((c) => c.opcode === opcode);

  if (!construct || !construct.branches) {
    return [];
  }

  const connectedSet = new Set(connectedBranches);
  const slots: Array<{ name: string; connected: boolean }> = [];

  // Handle dynamic branches for try/catch
  if (opcode === "control_try") {
    // TRY branch
    slots.push({ name: "TRY", connected: connectedSet.has("TRY") });

    // Find all CATCH branches
    const catchBranches = connectedBranches.filter((n) => n.startsWith("CATCH"));
    const maxCatch = catchBranches.length > 0
      ? Math.max(...catchBranches.map((n) => parseInt(n.replace("CATCH", "")) || 1))
      : 0;

    // Always show at least CATCH1 slot
    for (let i = 1; i <= Math.max(1, maxCatch); i++) {
      const name = `CATCH${i}`;
      slots.push({ name, connected: connectedSet.has(name) });
    }

    // FINALLY branch
    slots.push({ name: "FINALLY", connected: connectedSet.has("FINALLY") });

    return slots;
  }

  // Handle dynamic branches for fork
  if (opcode === "control_fork") {
    const branchBranches = connectedBranches.filter((n) => n.startsWith("BRANCH"));
    const maxBranch = branchBranches.length > 0
      ? Math.max(...branchBranches.map((n) => parseInt(n.replace("BRANCH", "")) || 1))
      : 0;

    // Always show at least BRANCH1 and BRANCH2 slots
    for (let i = 1; i <= Math.max(2, maxBranch); i++) {
      const name = `BRANCH${i}`;
      slots.push({ name, connected: connectedSet.has(name) });
    }

    return slots;
  }

  // Standard branches from schema
  for (const branch of construct.branches) {
    slots.push({ name: branch.name, connected: connectedSet.has(branch.name) });
  }

  return slots;
}

/**
 * Get categories from grammar.
 */
export function getCategories() {
  return getGrammar().categories;
}

// Export types
export type { Grammar } from "../../types/grammar";
