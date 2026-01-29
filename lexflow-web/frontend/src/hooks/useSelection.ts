// useSelection - Abstraction hook for selection state
// Uses selectionStore as single source of truth for all selection state

import { useMemo } from "react";
import { useWorkflowStore, useSelectionStore } from "../store";
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
  // Tree for finding selected node
  const tree = useWorkflowStore((state) => state.tree);

  // All selection state from selectionStore
  const selectedNodeId = useSelectionStore((state) => state.selectedNodeId);
  const selectNode = useSelectionStore((state) => state.selectNode);
  const selectedReporter = useSelectionStore((state) => state.selectedReporter);
  const selectReporter = useSelectionStore((state) => state.selectReporter);
  const selectedConnection = useSelectionStore((state) => state.selectedConnection);
  const selectConnection = useSelectionStore((state) => state.selectConnection);
  const selectedStartNode = useSelectionStore((state) => state.selectedStartNode);
  const selectStartNode = useSelectionStore((state) => state.selectStartNode);
  const clearSelection = useSelectionStore((state) => state.clearSelection);

  // Computed: selected node object
  const selectedNode = useMemo(() => {
    if (!selectedNodeId) return null;
    return findNodeInTree(tree, selectedNodeId);
  }, [selectedNodeId, tree]);

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
