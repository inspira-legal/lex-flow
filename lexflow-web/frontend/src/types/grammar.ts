/**
 * TypeScript types for the LexFlow Grammar Schema.
 *
 * This file defines types matching the grammar.json schema
 * used as the single source of truth for language constructs.
 */

/**
 * Input type for construct inputs.
 * - "expression": Value input (literal, variable, or reporter node)
 * - "variable_name": Literal string for variable binding
 */
export type InputType = "expression" | "variable_name";

/**
 * Definition of an input parameter for a construct.
 */
export interface ConstructInput {
  name: string;
  type: InputType;
  label: string;
  value_type?: string;
  required: boolean;
  default?: unknown;
}

/**
 * Definition of a branch for control flow constructs.
 */
export interface ConstructBranch {
  name: string;
  label: string;
  color: string;
  required: boolean;
  catch_config?: {
    exception_type: string;
    var_name: string;
  };
}

/**
 * A language construct definition (control flow opcode).
 */
export interface Construct {
  opcode: string;
  display_name: string;
  ast_class: string | null;
  category: string;
  description: string;
  inputs: ConstructInput[];
  branches: ConstructBranch[];
  dynamic_branches?: boolean;
  dynamic_inputs?: boolean;
}

/**
 * A category definition for grouping opcodes.
 */
export interface Category {
  id: string;
  prefix: string;
  label: string;
  color: string;
  icon: string;
}

/**
 * Branch color mapping.
 */
export type BranchColors = Record<string, string>;

/**
 * Node color mapping by node type.
 */
export type NodeColors = Record<string, string>;

/**
 * Reporter color mapping by category.
 */
export type ReporterColors = Record<string, string>;

/**
 * The complete grammar schema.
 */
export interface Grammar {
  version: string;
  categories: Category[];
  constructs: Construct[];
  branch_colors: BranchColors;
  node_colors: NodeColors;
  reporter_colors: ReporterColors;
}

/**
 * Helper function to get a construct by opcode name.
 */
export function getConstruct(
  grammar: Grammar,
  opcode: string,
): Construct | undefined {
  return grammar.constructs.find((c) => c.opcode === opcode);
}

/**
 * Helper function to get a category by ID.
 */
export function getCategory(
  grammar: Grammar,
  categoryId: string,
): Category | undefined {
  return grammar.categories.find((c) => c.id === categoryId);
}

/**
 * Helper function to get control flow opcodes (opcodes with branches).
 */
export function getControlFlowOpcodes(grammar: Grammar): Set<string> {
  return new Set(
    grammar.constructs
      .filter((c) => c.branches && c.branches.length > 0)
      .map((c) => c.opcode),
  );
}

/**
 * Helper function to check if an opcode is a control flow construct.
 */
export function isControlFlowOpcode(grammar: Grammar, opcode: string): boolean {
  const construct = getConstruct(grammar, opcode);
  return construct ? construct.branches.length > 0 : false;
}

/**
 * Helper function to get branch color by name.
 */
export function getBranchColor(grammar: Grammar, branchName: string): string {
  const colors = grammar.branch_colors;
  // Check for CATCH prefix
  if (branchName.startsWith("CATCH")) {
    return colors["CATCH"] || colors["default"] || "#9C27B0";
  }
  // Check for BRANCH prefix
  if (branchName.startsWith("BRANCH")) {
    return colors["BRANCH"] || colors["default"] || "#9C27B0";
  }
  return colors[branchName] || colors["default"] || "#9C27B0";
}

/**
 * Helper function to get node color by type.
 */
export function getNodeColor(grammar: Grammar, nodeType: string): string {
  const colors = grammar.node_colors;
  return colors[nodeType] || colors["opcode"] || "#64748B";
}

/**
 * Helper function to get reporter color by opcode prefix.
 */
export function getReporterColor(grammar: Grammar, opcode: string): string {
  const colors = grammar.reporter_colors;
  for (const category of grammar.categories) {
    if (opcode.startsWith(category.prefix)) {
      return colors[category.id] || colors["default"] || "#64748B";
    }
  }
  return colors["default"] || "#64748B";
}

/**
 * Helper function to get branch definitions for a construct.
 */
export function getConstructBranches(
  grammar: Grammar,
  opcode: string,
): ConstructBranch[] {
  const construct = getConstruct(grammar, opcode);
  return construct?.branches || [];
}
