// API Types matching Python backend models

export interface WorkflowInput {
  workflow: string;
  inputs?: Record<string, unknown>;
  include_metrics?: boolean;
}

export interface ParseResponse {
  success: boolean;
  tree?: WorkflowTree | null;
  interface?: WorkflowInterface | null;
  error?: string | null;
}

export interface ValidateResponse {
  valid: boolean;
  errors: string[];
}

export interface ExecuteResponse {
  success: boolean;
  result?: unknown;
  output?: string;
  metrics?: Record<string, unknown> | null;
  error?: string | null;
}

export interface ExampleInfo {
  name: string;
  path: string;
  category: string;
}

export interface ExampleContent {
  name: string;
  path: string;
  content: string;
}

export interface OpcodeInterface {
  name: string;
  description?: string;
  parameters: OpcodeParameter[];
  return_type?: string;
}

export interface OpcodeParameter {
  name: string;
  type: string;
  required: boolean;
  default?: unknown;
}

// Visualization tree types
export interface WorkflowTree {
  type: "project";
  workflows: WorkflowNode[];
  interface?: WorkflowInterface;
}

export interface WorkflowInterface {
  inputs: string[];
  outputs: string[];
}

export interface WorkflowNode {
  type: "workflow";
  name: string;
  interface: WorkflowInterface;
  variables: Record<string, unknown>;
  children: TreeNode[];
  orphans?: TreeNode[]; // Nodes not connected to the main chain
}

export interface TreeNode {
  id: string;
  type: NodeType;
  opcode: string;
  isReporter?: boolean;
  inputs: Record<string, FormattedValue>;
  config?: LoopConfig;
  children: BranchNode[];
  next?: string; // Next node in chain (used for orphan chain visualization)
}

export interface BranchNode {
  type: "branch";
  name: string;
  children: TreeNode[];
  exception_type?: string;
  var_name?: string;
}

export type NodeType =
  | "control_flow"
  | "data"
  | "io"
  | "operator"
  | "workflow_op"
  | "opcode";

export interface FormattedValue {
  type:
    | "literal"
    | "variable"
    | "reporter"
    | "branch"
    | "workflow_call"
    | "dict"
    | "truncated";
  value?: unknown;
  name?: string;
  id?: string;
  opcode?: string;
  inputs?: Record<string, FormattedValue>;
  target?: string;
  display?: string;
}

export interface LoopConfig {
  var?: string;
  start?: number;
  end?: number;
  step?: number;
  iterable?: FormattedValue;
  condition?: FormattedValue;
}

// Node category colors (Scratch-inspired)
export const NODE_COLORS: Record<NodeType | string, string> = {
  control_flow: "#FF9500", // Orange - control
  data: "#4CAF50", // Green - data
  io: "#22D3EE", // Cyan - I/O
  operator: "#9C27B0", // Purple - math/operators
  workflow_op: "#E91E63", // Magenta - workflow calls
  opcode: "#64748B", // Slate - generic
};
