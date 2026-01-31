/**
 * Grammar service for the LexFlow grammar schema.
 *
 * The grammar is imported directly from the copied grammar.json file.
 * This eliminates async loading and provides synchronous access.
 */
import type { Grammar, Construct } from "../../types/grammar";
/**
 * Get the grammar schema (synchronous).
 */
export declare function getGrammar(): Grammar;
/**
 * Get branch color by name.
 */
export declare function getBranchColor(branchName: string): string;
/**
 * Get node color by type.
 */
export declare function getNodeColor(nodeType: string): string;
/**
 * Get reporter color by opcode.
 */
export declare function getReporterColor(opcode: string): string;
/**
 * Get the set of control flow opcodes.
 */
export declare function getControlFlowOpcodeSet(): Set<string>;
/**
 * Get a construct by opcode.
 */
export declare function getConstruct(opcode: string): Construct | undefined;
/**
 * Get branch slots for a control flow opcode.
 * Uses grammar-driven logic with support for dynamic branches.
 */
export declare function getBranchSlots(opcode: string, connectedBranches: string[]): Array<{
    name: string;
    connected: boolean;
}>;
/**
 * Get categories from grammar.
 */
export declare function getCategories(): import("../../types/grammar").Category[];
/**
 * Get category icon by opcode prefix.
 */
export declare function getCategoryIcon(opcode: string): string;
/**
 * Get category by opcode prefix.
 */
export declare function getCategoryByOpcode(opcode: string): import("../../types/grammar").Category | null;
export type { Grammar, Construct } from "../../types/grammar";
