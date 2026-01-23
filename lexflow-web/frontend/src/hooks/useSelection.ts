// useSelection - Abstraction hook for selection state

import { useMemo, useCallback } from "react";
import { useWorkflowStore, useUiStore } from "../store";
import type { TreeNode, WorkflowTree } from "../api/types";

// Helper to find a node by ID in the tree
function findNodeInTree(
  tree: WorkflowTree | null,
  nodeId: string,
): TreeNode | null {
  if (!tree) return null;

  for (const workflow of tree.workflows) {
    // Search in main children
    const found = findNodeRecursive(workflow.children, nodeId);
    if (found) return found;

    // Search in orphans
    if (workflow.orphans) {
      const foundOrphan = findNodeRecursive(workflow.orphans, nodeId);
      if (foundOrphan) return foundOrphan;
    }
  }

  return null;
}

function findNodeRecursive(nodes: TreeNode[], nodeId: string): TreeNode | null {
  for (const node of nodes) {
    if (node.id === nodeId) return node;

    // Search in branch children
    for (const branch of node.children) {
      const found = findNodeRecursive(branch.children, nodeId);
      if (found) return found;
    }

    // Search in reporter inputs
    for (const input of Object.values(node.inputs)) {
      if (input.type === "reporter" && input.id === nodeId) {
        // Create a TreeNode-like structure for the reporter
        return {
          id: input.id,
          type: "opcode",
          opcode: input.opcode || "",
          inputs: input.inputs || {},
          children: [],
          isReporter: true,
        };
      }
      // Recursively search nested reporters
      if (input.type === "reporter" && input.inputs) {
        const nestedFound = findReporterById(input.inputs, nodeId);
        if (nestedFound) return nestedFound;
      }
    }
  }
  return null;
}

function findReporterById(
  inputs: Record<
    string,
    {
      type: string;
      id?: string;
      opcode?: string;
      inputs?: Record<string, unknown>;
    }
  >,
  nodeId: string,
): TreeNode | null {
  for (const input of Object.values(inputs)) {
    if (input.type === "reporter" && input.id === nodeId) {
      return {
        id: input.id,
        type: "opcode",
        opcode: input.opcode || "",
        inputs: (input.inputs as Record<string, never>) || {},
        children: [],
        isReporter: true,
      };
    }
    if (input.type === "reporter" && input.inputs) {
      const found = findReporterById(
        input.inputs as Record<
          string,
          {
            type: string;
            id?: string;
            opcode?: string;
            inputs?: Record<string, unknown>;
          }
        >,
        nodeId,
      );
      if (found) return found;
    }
  }
  return null;
}

export function useSelection() {
  // Node selection
  const selectedNodeId = useWorkflowStore((state) => state.selectedNodeId);
  const selectNode = useWorkflowStore((state) => state.selectNode);
  const tree = useWorkflowStore((state) => state.tree);

  // Reporter selection
  const selectedReporter = useUiStore((state) => state.selectedReporter);
  const selectReporter = useUiStore((state) => state.selectReporter);

  // Connection selection
  const selectedConnection = useUiStore((state) => state.selectedConnection);
  const selectConnection = useUiStore((state) => state.selectConnection);

  // Start node selection
  const selectedStartNode = useUiStore((state) => state.selectedStartNode);
  const selectStartNode = useUiStore((state) => state.selectStartNode);

  // Computed: selected node object
  const selectedNode = useMemo(() => {
    if (!selectedNodeId) return null;
    return findNodeInTree(tree, selectedNodeId);
  }, [selectedNodeId, tree]);

  // Clear all selections
  const clearSelection = useCallback(() => {
    selectNode(null);
    selectReporter(null);
    selectConnection(null);
    selectStartNode(null);
  }, [selectNode, selectReporter, selectConnection, selectStartNode]);

  return {
    // Node selection
    selectedNodeId,
    selectedNode,
    selectNode,

    // Reporter selection
    selectedReporter,
    selectReporter,

    // Connection selection
    selectedConnection,
    selectConnection,

    // Start node selection
    selectedStartNode,
    selectStartNode,

    // Clear all
    clearSelection,
  };
}
