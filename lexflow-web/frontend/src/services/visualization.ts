// Visualization service for converting workflows to tree structures
// Uses grammar-driven extraction for dynamic node rendering

import type {
  WorkflowTree,
  WorkflowNode,
  TreeNode,
  BranchNode,
  FormattedValue,
  LoopConfig,
  NodeType,
  WorkflowInterface,
} from "../api/types";
import { getConstruct, getGrammar } from "./grammar";
import type { Construct } from "../types/grammar";

interface WorkflowData {
  workflows?: WorkflowDefinition[];
  nodes?: Record<string, NodeDefinition>;
  name?: string;
  interface?: { inputs?: string[]; outputs?: string[] };
  variables?: Record<string, unknown>;
}

interface WorkflowDefinition {
  name?: string;
  nodes?: Record<string, NodeDefinition>;
  interface?: { inputs?: string[]; outputs?: string[] };
  variables?: Record<string, unknown>;
}

interface NodeDefinition {
  opcode?: string;
  inputs?: Record<string, unknown>;
  next?: string;
  isReporter?: boolean;
}

interface InputValue {
  literal?: unknown;
  variable?: string;
  node?: string;
  branch?: string;
  workflow_call?: string;
}

interface CatchHandler {
  branch?: string;
  exception_type?: string;
  var_name?: string;
  var?: string;
  body?: InputValue;
}

export function workflowToTree(
  workflowData: WorkflowData,
): WorkflowTree | { error: string } {
  const workflows = workflowData.workflows || [];

  if (workflows.length === 0) {
    // Check if it's a single implicit workflow (keys at root)
    if (workflowData.nodes) {
      return {
        type: "project",
        workflows: [buildWorkflowTree(workflowData as WorkflowDefinition)],
      };
    }
    return { error: "No workflows found" };
  }

  // Build tree for all workflows
  const workflowTrees: WorkflowNode[] = [];
  let mainInterface: WorkflowInterface = { inputs: [], outputs: [] };

  for (const w of workflows) {
    const tree = buildWorkflowTree(w);
    workflowTrees.push(tree);
    if (tree.name === "main" || mainInterface.inputs.length === 0) {
      mainInterface = tree.interface;
    }
  }

  return {
    type: "project",
    workflows: workflowTrees,
    interface: mainInterface,
  };
}

function buildWorkflowTree(workflow: WorkflowDefinition): WorkflowNode {
  const nodes = workflow.nodes || {};
  const iface = workflow.interface || {};

  const tree: WorkflowNode = {
    type: "workflow",
    name: workflow.name || "main",
    interface: {
      inputs: iface.inputs || [],
      outputs: iface.outputs || [],
    },
    variables: workflow.variables || {},
    children: [],
    orphans: [],
  };

  // Track all visited nodes (including branch nodes and reporters)
  const allVisited = new Set<string>();

  // Follow node chain from start
  const startNode = nodes["start"] || {};
  let currentId = startNode.next;

  while (currentId && !allVisited.has(currentId)) {
    allVisited.add(currentId);
    const node = nodes[currentId];
    if (!node) break;

    const treeNode = nodeToTree(currentId, node, nodes, allVisited);
    tree.children.push(treeNode);
    currentId = node.next;
  }

  // Find orphan nodes (nodes not in the connected chain)
  const allNodeIds = new Set(Object.keys(nodes).filter((id) => id !== "start"));
  const potentialOrphanIds = new Set(
    [...allNodeIds].filter((id) => !allVisited.has(id)),
  );

  // Collect reporter IDs from ALL potential orphan nodes
  for (const nodeId of potentialOrphanIds) {
    const node = nodes[nodeId] || {};
    collectReporterIds(node.inputs || {}, nodes, allVisited);
  }

  // Recalculate orphan_ids with reporter references accounted for
  const orphanIds = new Set(
    [...allNodeIds].filter((id) => !allVisited.has(id)),
  );

  // Build orphan chains: find chain heads (orphans not pointed to by other orphans)
  const orphanNextTargets = new Set<string>();
  for (const nodeId of orphanIds) {
    const node = nodes[nodeId] || {};
    const nextId = node.next;
    if (nextId && orphanIds.has(nextId)) {
      orphanNextTargets.add(nextId);
    }
  }

  // Chain heads are orphans that no other orphan points to
  const orphanHeads = [...orphanIds]
    .filter((oid) => !orphanNextTargets.has(oid))
    .sort();

  // Process each orphan chain starting from its head
  const processedOrphans = new Set<string>();
  for (const headId of orphanHeads) {
    let currentOrphanId: string | undefined = headId;
    while (currentOrphanId && !processedOrphans.has(currentOrphanId)) {
      const node: NodeDefinition | undefined = nodes[currentOrphanId];
      if (!node) break;

      // Skip reporter nodes (they're embedded in other nodes)
      if (node.isReporter) {
        processedOrphans.add(currentOrphanId);
        currentOrphanId =
          node.next && orphanIds.has(node.next) ? node.next : undefined;
        continue;
      }

      processedOrphans.add(currentOrphanId);
      const orphanTree = nodeToTree(currentOrphanId, node, nodes, allVisited);

      // Include next pointer if it points to another orphan (for chain visualization)
      const nextId = node.next;
      if (nextId && orphanIds.has(nextId)) {
        orphanTree.next = nextId;
      }

      tree.orphans!.push(orphanTree);
      currentOrphanId = nextId && orphanIds.has(nextId) ? nextId : undefined;
    }
  }

  return tree;
}

function nodeToTree(
  nodeId: string,
  node: NodeDefinition,
  allNodes: Record<string, NodeDefinition>,
  allVisited: Set<string>,
): TreeNode {
  const opcode = node.opcode || "";
  const inputs = node.inputs || {};
  const isReporter = node.isReporter || false;

  // Track reporter nodes referenced in inputs
  collectReporterIds(inputs, allNodes, allVisited);

  const treeNode: TreeNode = {
    id: nodeId,
    type: getNodeType(opcode),
    opcode,
    isReporter,
    inputs: formatInputs(inputs, allNodes, opcode),
    children: [],
  };

  // Get construct from grammar for grammar-driven extraction
  const construct = getConstruct(opcode);

  if (construct && construct.branches.length > 0) {
    // Extract config for loops and other constructs with special inputs
    treeNode.config = extractConfig(opcode, inputs, allNodes, construct);

    // Grammar-driven branch extraction
    treeNode.children = extractBranches(inputs, allNodes, allVisited, construct);
  }

  return treeNode;
}

/**
 * Extract config values from construct inputs (for loops, etc.)
 */
function extractConfig(
  opcode: string,
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
  construct: Construct,
): LoopConfig {
  const config: LoopConfig = {};

  // Extract values for non-branch inputs
  for (const inputDef of construct.inputs) {
    const value = getInputValue(inputs, inputDef.name);
    if (value !== undefined) {
      const key = inputDef.name.toLowerCase();

      if (inputDef.type === "variable_name") {
        // Variable name inputs are stored as raw string
        config[key] = getRawValue(value) as string;
      } else if (inputDef.type === "expression") {
        // Expression inputs need formatting
        if (key === "condition" || key === "iterable" || key === "resource") {
          config[key] = formatValue(value, allNodes);
        } else {
          // Numeric values (start, end, step, timeout)
          config[key] = getRawValue(value) as number;
        }
      }
    }
  }

  // Legacy support: ensure var is set for loops
  if (["control_for", "control_foreach", "control_spawn", "control_async_foreach", "control_with"].includes(opcode)) {
    if (!config.var) {
      config.var = getRawValue(inputs["VAR"] ?? inputs["var"] ?? "i") as string;
    }
  }

  return config;
}

/**
 * Grammar-driven branch extraction.
 * Handles both static and dynamic branches based on construct definition.
 * Includes empty branches (with branch: null) so slots render in UI.
 */
function extractBranches(
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
  allVisited: Set<string>,
  construct: Construct,
): BranchNode[] {
  const branches: BranchNode[] = [];

  if (construct.dynamic_branches) {
    // Handle dynamic branches (try/fork patterns)
    return extractDynamicBranches(inputs, allNodes, allVisited, construct);
  }

  // Standard branch extraction from grammar
  for (const branchDef of construct.branches) {
    const branchInput = getInputValue(inputs, branchDef.name) as InputValue | undefined;
    const branchId = typeof branchInput === "object" && branchInput !== null
      ? branchInput.branch
      : undefined;

    if (branchId) {
      branches.push(buildBranch(branchDef.name, branchId, allNodes, allVisited));
    } else if (branchInput !== undefined) {
      // Empty branch slot (branch: null) - include as empty branch
      branches.push({ type: "branch", name: branchDef.name, children: [] });
    }
  }

  return branches;
}

/**
 * Extract dynamic branches for constructs like try/fork.
 * Uses grammar to identify patterns and extract all matching branches.
 * Includes empty branches (with branch: null) so slots render in UI.
 */
function extractDynamicBranches(
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
  allVisited: Set<string>,
  construct: Construct,
): BranchNode[] {
  const branches: BranchNode[] = [];

  // Identify static vs dynamic branch patterns from grammar
  const staticBranchNames: string[] = [];
  const dynamicPrefixes: string[] = [];

  for (const branchDef of construct.branches) {
    const match = branchDef.name.match(/^([A-Z]+)(\d+)$/);
    if (match) {
      const prefix = match[1];
      if (!dynamicPrefixes.includes(prefix)) {
        dynamicPrefixes.push(prefix);
      }
    } else {
      staticBranchNames.push(branchDef.name);
    }
  }

  // Extract static branches first (e.g., TRY, FINALLY)
  for (const branchName of staticBranchNames) {
    const branchInput = getInputValue(inputs, branchName) as InputValue | undefined;
    const branchId = typeof branchInput === "object" && branchInput !== null
      ? branchInput.branch
      : undefined;

    if (branchId) {
      branches.push(buildBranch(branchName, branchId, allNodes, allVisited));
    } else if (branchInput !== undefined) {
      // Empty branch slot (branch: null) - include as empty branch
      branches.push({ type: "branch", name: branchName, children: [] });
    }
  }

  // Extract dynamic branches by pattern
  for (const prefix of dynamicPrefixes) {
    // Check for list format (HANDLERS, BRANCHES)
    const listKey = prefix === "CATCH" ? "HANDLERS" : prefix === "BRANCH" ? "BRANCHES" : null;
    const listInput = listKey ? (inputs[listKey] ?? inputs[listKey.toLowerCase()]) : null;

    if (Array.isArray(listInput) && listInput.length > 0) {
      // List format
      listInput.forEach((item, i) => {
        if (typeof item === "object" && item !== null) {
          const handler = item as CatchHandler;
          const branchId = handler.branch ?? (handler.body as InputValue | undefined)?.branch;
          const branchName = `${prefix}${i + 1}`;

          if (branchId) {
            const branch = buildBranch(branchName, branchId, allNodes, allVisited);
            if (prefix === "CATCH") {
              branch.exception_type = handler.exception_type || "Exception";
              branch.var_name = handler.var_name ?? handler.var;
            }
            branches.push(branch);
          } else {
            // Empty branch slot - include so UI can show the slot
            const emptyBranch: BranchNode = { type: "branch", name: branchName, children: [] };
            if (prefix === "CATCH") {
              emptyBranch.exception_type = handler.exception_type || "Exception";
              emptyBranch.var_name = handler.var_name ?? handler.var;
            }
            branches.push(emptyBranch);
          }
        }
      });
    } else {
      // Individual keys format (CATCH1, CATCH2, BRANCH1, BRANCH2, etc.)
      let i = 1;
      while (true) {
        const key = `${prefix}${i}`;
        const branchInput = inputs[key];
        if (branchInput === undefined) break;

        if (typeof branchInput === "object" && branchInput !== null) {
          const handler = branchInput as CatchHandler;
          // Try different branch reference formats
          const branchId = handler.branch
            ?? (handler.body as InputValue | undefined)?.branch
            ?? (branchInput as InputValue).branch;

          if (branchId) {
            const branch = buildBranch(key, branchId, allNodes, allVisited);
            if (prefix === "CATCH") {
              branch.exception_type = handler.exception_type || "Exception";
              branch.var_name = handler.var_name ?? handler.var;
            }
            branches.push(branch);
          } else {
            // Empty branch slot - include so UI can show the slot
            const emptyBranch: BranchNode = { type: "branch", name: key, children: [] };
            if (prefix === "CATCH") {
              emptyBranch.exception_type = handler.exception_type || "Exception";
              emptyBranch.var_name = handler.var_name ?? handler.var;
            }
            branches.push(emptyBranch);
          }
        }
        i++;
      }
    }
  }

  return branches;
}

/**
 * Get input value with case-insensitive key lookup.
 */
function getInputValue(inputs: Record<string, unknown>, key: string): unknown {
  return inputs[key] ?? inputs[key.toLowerCase()];
}

function collectReporterIds(
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
  allVisited: Set<string>,
): void {
  for (const value of Object.values(inputs)) {
    if (typeof value === "object" && value !== null) {
      const inputValue = value as InputValue;
      if (inputValue.node) {
        const nodeId = inputValue.node;
        if (!allVisited.has(nodeId)) {
          allVisited.add(nodeId);
          const node = allNodes[nodeId] || {};
          // Recursively collect from reporter's inputs
          const nodeInputs = node.inputs || {};
          collectReporterIds(nodeInputs, allNodes, allVisited);
        }
      }
    }
  }
}

function getNodeType(opcode: string): NodeType {
  const grammar = getGrammar();
  for (const category of grammar.categories) {
    if (opcode.startsWith(category.prefix)) {
      // Map category id to NodeType
      switch (category.id) {
        case "control":
        case "async":
          return "control_flow";
        case "data":
          return "data";
        case "io":
          return "io";
        case "operator":
        case "math":
        case "string":
        case "list":
        case "dict":
          return "operator";
        case "workflow":
          return "workflow_op";
        default:
          return "opcode";
      }
    }
  }
  return "opcode";
}

/**
 * Format inputs for display, filtering out branch inputs based on grammar.
 */
function formatInputs(
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
  opcode: string,
): Record<string, FormattedValue> {
  const formatted: Record<string, FormattedValue> = {};
  const construct = getConstruct(opcode);

  // Build set of branch input names to filter out
  const branchInputNames = new Set<string>();
  if (construct) {
    for (const branch of construct.branches) {
      branchInputNames.add(branch.name);
      branchInputNames.add(branch.name.toLowerCase());
    }
  }

  // Always filter these special keys
  const specialKeys = new Set([
    "BODY", "body", "THEN", "then", "ELSE", "else",
    "TRY", "FINALLY", "HANDLERS", "handlers", "BRANCHES", "branches"
  ]);

  for (const [key, value] of Object.entries(inputs)) {
    // Skip branch inputs
    if (branchInputNames.has(key) || specialKeys.has(key)) {
      continue;
    }
    // Skip dynamic branch patterns
    if (/^(CATCH|BRANCH)\d+$/.test(key)) {
      continue;
    }

    formatted[key] = formatValue(value, allNodes);
  }

  return formatted;
}

function formatValue(
  value: unknown,
  allNodes: Record<string, NodeDefinition>,
  _depth: number = 0,
): FormattedValue {
  if (typeof value === "object" && value !== null) {
    const inputValue = value as Record<string, unknown>;

    if ("literal" in inputValue) {
      return { type: "literal", value: inputValue.literal };
    }
    if ("variable" in inputValue) {
      return { type: "variable", name: inputValue.variable as string };
    }
    if ("node" in inputValue) {
      const nodeId = inputValue.node as string;
      const node = allNodes[nodeId] || {};
      const opcode = node.opcode || "";
      const nodeInputs = node.inputs || {};
      return {
        type: "reporter",
        id: nodeId,
        opcode,
        inputs: Object.fromEntries(
          Object.entries(nodeInputs)
            .filter(
              ([k]) =>
                !k.startsWith("CATCH") && !["BODY", "THEN", "ELSE"].includes(k),
            )
            .map(([k, v]) => [k, formatValue(v, allNodes, _depth + 1)]),
        ),
      };
    }
    if ("branch" in inputValue) {
      return { type: "branch", target: inputValue.branch as string };
    }
    if ("workflow_call" in inputValue) {
      return {
        type: "workflow_call",
        name: inputValue.workflow_call as string,
      };
    }
    return { type: "dict", value };
  }

  return { type: "literal", value };
}

function getRawValue(value: unknown): unknown {
  if (
    typeof value === "object" &&
    value !== null &&
    "literal" in (value as Record<string, unknown>)
  ) {
    return (value as { literal: unknown }).literal;
  }
  return value;
}

function buildBranch(
  name: string,
  startId: string,
  allNodes: Record<string, NodeDefinition>,
  allVisited: Set<string>,
): BranchNode {
  const branch: BranchNode = {
    type: "branch",
    name,
    children: [],
  };

  let currentId: string | undefined = startId;
  while (currentId && !allVisited.has(currentId)) {
    allVisited.add(currentId);
    const node: NodeDefinition | undefined = allNodes[currentId];
    if (!node) break;
    branch.children.push(nodeToTree(currentId, node, allNodes, allVisited));
    currentId = node.next;
  }

  return branch;
}
