// Visualization service for converting workflows to tree structures
// Ported from Python backend visualization.py to enable client-side parsing

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
    inputs: formatInputs(inputs, allNodes),
    children: [],
  };

  // Handle control flow branches
  if (["control_for", "control_foreach", "control_while"].includes(opcode)) {
    treeNode.config = extractLoopConfig(opcode, inputs, allNodes);
    const bodyInput = (inputs["BODY"] || inputs["body"] || {}) as InputValue;
    const bodyBranch =
      typeof bodyInput === "object" ? bodyInput.branch : undefined;
    if (bodyBranch) {
      treeNode.children.push(
        buildBranch("BODY", bodyBranch, allNodes, allVisited),
      );
    }
  } else if (["control_if", "control_if_else"].includes(opcode)) {
    const thenInput = (inputs["THEN"] || inputs["then"] || {}) as InputValue;
    const thenBranch =
      typeof thenInput === "object" ? thenInput.branch : undefined;
    if (thenBranch) {
      treeNode.children.push(
        buildBranch("THEN", thenBranch, allNodes, allVisited),
      );
    }

    const elseInput = (inputs["ELSE"] || inputs["else"] || {}) as InputValue;
    const elseBranch =
      typeof elseInput === "object" ? elseInput.branch : undefined;
    if (elseBranch) {
      treeNode.children.push(
        buildBranch("ELSE", elseBranch, allNodes, allVisited),
      );
    }
  } else if (opcode === "control_fork") {
    treeNode.children = extractForkBranches(inputs, allNodes, allVisited);
  } else if (opcode === "control_try") {
    treeNode.children = extractTryBranches(inputs, allNodes, allVisited);
  }

  return treeNode;
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
  if (opcode.startsWith("control_")) return "control_flow";
  if (opcode.startsWith("data_")) return "data";
  if (opcode.startsWith("io_")) return "io";
  if (opcode.startsWith("operator_")) return "operator";
  if (opcode.startsWith("workflow_")) return "workflow_op";
  return "opcode";
}

function formatInputs(
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
): Record<string, FormattedValue> {
  const formatted: Record<string, FormattedValue> = {};

  for (const [key, value] of Object.entries(inputs)) {
    // Skip branch inputs for control flow (handled separately)
    if (
      [
        "BODY",
        "body",
        "THEN",
        "then",
        "ELSE",
        "else",
        "TRY",
        "FINALLY",
      ].includes(key)
    ) {
      continue;
    }
    if (key.startsWith("CATCH") || key.startsWith("BRANCH")) {
      continue;
    }
    if (["HANDLERS", "handlers", "BRANCHES", "branches"].includes(key)) {
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

function extractLoopConfig(
  opcode: string,
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
): LoopConfig {
  const config: LoopConfig = {};

  if (opcode === "control_for") {
    config.var = getRawValue(inputs["VAR"] ?? inputs["var"] ?? "i") as string;
    config.start = getRawValue(
      inputs["START"] ?? inputs["start"] ?? 0,
    ) as number;
    config.end = getRawValue(inputs["END"] ?? inputs["end"] ?? 0) as number;
    const step = inputs["STEP"] ?? inputs["step"];
    if (step !== undefined) {
      config.step = getRawValue(step) as number;
    }
  } else if (opcode === "control_foreach") {
    config.var = getRawValue(
      inputs["VAR"] ?? inputs["var"] ?? "item",
    ) as string;
    config.iterable = formatValue(
      inputs["ITERABLE"] ?? inputs["iterable"] ?? [],
      allNodes,
    );
  } else if (opcode === "control_while") {
    config.condition = formatValue(
      inputs["CONDITION"] ?? inputs["condition"] ?? true,
      allNodes,
    );
  }

  return config;
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

function extractForkBranches(
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
  allVisited: Set<string>,
): BranchNode[] {
  const branches: BranchNode[] = [];

  // Try list format first
  const branchList = (inputs["BRANCHES"] ??
    inputs["branches"] ??
    []) as InputValue[];
  if (Array.isArray(branchList) && branchList.length > 0) {
    branchList.forEach((branchRef, i) => {
      const branchId =
        typeof branchRef === "object" && branchRef !== null
          ? (branchRef as InputValue).branch
          : undefined;
      if (branchId) {
        branches.push(
          buildBranch(`BRANCH${i + 1}`, branchId, allNodes, allVisited),
        );
      }
    });
  } else {
    // Try individual keys
    let i = 1;
    while (`BRANCH${i}` in inputs) {
      const branchRef = inputs[`BRANCH${i}`] as InputValue;
      const branchId =
        typeof branchRef === "object" && branchRef !== null
          ? branchRef.branch
          : undefined;
      if (branchId) {
        branches.push(
          buildBranch(`BRANCH${i}`, branchId, allNodes, allVisited),
        );
      }
      i++;
    }
  }

  return branches;
}

function extractTryBranches(
  inputs: Record<string, unknown>,
  allNodes: Record<string, NodeDefinition>,
  allVisited: Set<string>,
): BranchNode[] {
  const branches: BranchNode[] = [];

  // TRY body
  const tryInput = (inputs["TRY"] ??
    inputs["BODY"] ??
    inputs["body"] ??
    {}) as InputValue;
  const tryBranch = typeof tryInput === "object" ? tryInput.branch : undefined;
  if (tryBranch) {
    branches.push(buildBranch("TRY", tryBranch, allNodes, allVisited));
  }

  // CATCH handlers
  const handlers = (inputs["HANDLERS"] ??
    inputs["handlers"] ??
    []) as CatchHandler[];
  if (Array.isArray(handlers) && handlers.length > 0) {
    handlers.forEach((handler, i) => {
      if (typeof handler === "object" && handler !== null) {
        const handlerBranch = handler.branch;
        if (handlerBranch) {
          const branch = buildBranch(
            `CATCH${i + 1}`,
            handlerBranch,
            allNodes,
            allVisited,
          );
          branch.exception_type = handler.exception_type || "Exception";
          branch.var_name = handler.var_name;
          branches.push(branch);
        }
      }
    });
  } else {
    // Try individual CATCH keys
    let i = 1;
    while (`CATCH${i}` in inputs) {
      const catchInput = inputs[`CATCH${i}`] as CatchHandler;
      if (typeof catchInput === "object" && catchInput !== null) {
        const bodyInfo = catchInput.body;
        const handlerBranch =
          typeof bodyInfo === "object" && bodyInfo !== null
            ? (bodyInfo as InputValue).branch
            : undefined;
        if (handlerBranch) {
          const branch = buildBranch(
            `CATCH${i}`,
            handlerBranch,
            allNodes,
            allVisited,
          );
          branch.exception_type = catchInput.exception_type || "Exception";
          branch.var_name = catchInput.var ?? catchInput.var_name;
          branches.push(branch);
        }
      }
      i++;
    }
  }

  // FINALLY
  const finallyInput = (inputs["FINALLY"] ??
    inputs["finally"] ??
    {}) as InputValue;
  const finallyBranch =
    typeof finallyInput === "object" ? finallyInput.branch : undefined;
  if (finallyBranch) {
    branches.push(buildBranch("FINALLY", finallyBranch, allNodes, allVisited));
  }

  return branches;
}
