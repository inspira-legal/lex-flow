import type { WorkflowTree, FormattedValue } from "../api/types";
/**
 * Get mapping from ARG keys to parameter names for a workflow_call.
 * Returns { ARG1: "paramName1", ARG2: "paramName2", ... }
 */
export declare function getWorkflowCallParamMapping(tree: WorkflowTree | null, targetWorkflowName: string): Record<string, string>;
/**
 * Get display name for an input key.
 * For workflow_call, shows the parameter name directly (e.g., "name" instead of "ARG1").
 * Falls back to ARG1 if the workflow interface is unknown.
 */
export declare function getInputDisplayName(inputKey: string, opcode: string, tree: WorkflowTree | null, inputs: Record<string, FormattedValue>): string;
/**
 * Get callable workflows (non-main) from the tree.
 */
export declare function getCallableWorkflows(tree: WorkflowTree | null): Array<{
    name: string;
    params: string[];
}>;
