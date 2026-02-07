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
  category?: string;
}

export interface OpcodeParameter {
  name: string;
  type: string;
  required: boolean;
  default?: unknown;
}

// Detailed input types for workflow interfaces
export type InputType =
  | "string"
  | "number"
  | "boolean"
  | "list"
  | "dict"
  | "any";

export interface DetailedInput {
  name: string;
  type: InputType;
  required: boolean;
}

export function normalizeInput(input: string | DetailedInput): DetailedInput {
  if (typeof input === "string") {
    return { name: input, type: "string", required: false };
  }
  return {
    name: input.name,
    type: input.type || "string",
    required: input.required ?? false,
  };
}

// Visualization tree types
export interface WorkflowTree {
  type: "project";
  workflows: WorkflowNode[];
  interface?: WorkflowInterface;
}

export interface WorkflowInterface {
  inputs: DetailedInput[];
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
  timeout?: number;
  iterable?: FormattedValue;
  condition?: FormattedValue;
  resource?: FormattedValue;
  // Index signature for grammar-driven dynamic properties
  [key: string]: string | number | FormattedValue | undefined;
}

// Node colors are now sourced from grammar via getNodeColor()
// Re-export for backwards compatibility
export { getNodeColor } from "../constants";
