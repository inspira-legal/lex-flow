// Workflow utility functions

import type { WorkflowTree, FormattedValue } from "../api/types";

/**
 * Get mapping from ARG keys to parameter names for a workflow_call.
 * Returns { ARG1: "paramName1", ARG2: "paramName2", ... }
 */
export function getWorkflowCallParamMapping(
  tree: WorkflowTree | null,
  targetWorkflowName: string,
): Record<string, string> {
  if (!tree) return {};

  const workflow = tree.workflows.find((w) => w.name === targetWorkflowName);
  if (!workflow) return {};

  const mapping: Record<string, string> = {};
  workflow.interface.inputs.forEach((param, i) => {
    mapping[`ARG${i + 1}`] = param.name;
  });
  return mapping;
}

/**
 * Get display name for an input key.
 * For workflow_call, shows the parameter name directly (e.g., "name" instead of "ARG1").
 * Falls back to ARG1 if the workflow interface is unknown.
 */
export function getInputDisplayName(
  inputKey: string,
  opcode: string,
  tree: WorkflowTree | null,
  inputs: Record<string, FormattedValue>,
): string {
  if (opcode !== "workflow_call") return inputKey;

  // Get the target workflow name from WORKFLOW input
  const workflowInput = inputs["WORKFLOW"];
  if (!workflowInput || workflowInput.type !== "literal") return inputKey;
  const targetName = workflowInput.value as string;
  if (!targetName) return inputKey;

  const mapping = getWorkflowCallParamMapping(tree, targetName);
  if (inputKey.startsWith("ARG") && mapping[inputKey]) {
    return mapping[inputKey];
  }
  return inputKey;
}

/**
 * Get callable workflows (non-main) from the tree.
 */
export function getCallableWorkflows(
  tree: WorkflowTree | null,
): Array<{ name: string; params: string[] }> {
  if (!tree) return [];

  return tree.workflows
    .filter((w) => w.name !== "main")
    .map((w) => ({
      name: w.name,
      params: w.interface.inputs.map((i) => i.name),
    }));
}
