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
export declare function getConstruct(grammar: Grammar, opcode: string): Construct | undefined;
/**
 * Helper function to get a category by ID.
 */
export declare function getCategory(grammar: Grammar, categoryId: string): Category | undefined;
/**
 * Helper function to get control flow opcodes (opcodes with branches).
 */
export declare function getControlFlowOpcodes(grammar: Grammar): Set<string>;
/**
 * Helper function to check if an opcode is a control flow construct.
 */
export declare function isControlFlowOpcode(grammar: Grammar, opcode: string): boolean;
/**
 * Helper function to get branch color by name.
 */
export declare function getBranchColor(grammar: Grammar, branchName: string): string;
/**
 * Helper function to get node color by type.
 */
export declare function getNodeColor(grammar: Grammar, nodeType: string): string;
/**
 * Helper function to get reporter color by opcode prefix.
 */
export declare function getReporterColor(grammar: Grammar, opcode: string): string;
/**
 * Helper function to get branch definitions for a construct.
 */
export declare function getConstructBranches(grammar: Grammar, opcode: string): ConstructBranch[];
