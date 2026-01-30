// LayoutService - Business logic for canvas layout calculations

import type {
  FormattedValue,
  TreeNode,
  WorkflowNode,
  WorkflowInterface,
} from "../../api/types";
import { NODE_DIMENSIONS, LAYOUT_GAPS } from "../../constants";
import { getControlFlowOpcodeSet, getBranchColor as grammarGetBranchColor } from "../../services/grammar";
import { START_NODE_WIDTH, START_NODE_HEIGHT } from "../../components/canvas/StartNode";

// Layout constants
const NODE_WIDTH = NODE_DIMENSIONS.WIDTH;
const NODE_HEIGHT = NODE_DIMENSIONS.HEIGHT;
const H_GAP = LAYOUT_GAPS.HORIZONTAL;
const V_GAP = LAYOUT_GAPS.VERTICAL;
const WORKFLOW_GAP = LAYOUT_GAPS.WORKFLOW;
const START_NODE_GAP = 40;

// Layout types
export interface LayoutNode {
  node: TreeNode;
  x: number;
  y: number;
  width: number;
  height: number;
  isOrphan?: boolean;
}

export interface LayoutConnection {
  from: string;
  to: string;
  fromPort: "input" | "output" | string; // string for branch names
  toPort: "input" | "output";
  color: string;
  label?: string;
}

export interface LayoutWorkflowGroup {
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  isMain: boolean;
}

export interface LayoutStartNode {
  workflowName: string;
  workflowInterface: WorkflowInterface;
  variables: Record<string, unknown>;
  x: number;
  y: number;
}

export interface FullLayout {
  nodes: LayoutNode[];
  connections: LayoutConnection[];
  groups: LayoutWorkflowGroup[];
  startNodes: LayoutStartNode[];
}

// Calculate total height of a reporter pill (including its content and label)
export function calculateReporterTotalHeight(
  value: FormattedValue,
  includeLabel = true,
): number {
  if (value.type !== "reporter") return 0;

  const labelHeight = includeLabel ? 14 : 0;
  const headerHeight = 22;

  let regularInputsCount = 0;
  let nestedReportersCount = 0;
  let nestedReportersHeight = 0;

  if (value.inputs) {
    for (const nestedValue of Object.values(value.inputs)) {
      if (nestedValue.type === "reporter" && nestedValue.opcode) {
        nestedReportersCount++;
        nestedReportersHeight +=
          calculateReporterTotalHeight(nestedValue, true) + 4;
      } else {
        const formatted = formatValueShort(nestedValue);
        if (formatted) regularInputsCount++;
      }
    }
  }

  const nestedLabelHeight = nestedReportersCount * 14;
  return (
    labelHeight +
    headerHeight +
    regularInputsCount * 14 +
    nestedLabelHeight +
    nestedReportersHeight +
    4
  );
}

// Format value for short display
export function formatValueShort(value: FormattedValue): string {
  switch (value.type) {
    case "literal": {
      const v = value.value;
      if (typeof v === "string")
        return `"${v.length > 10 ? v.slice(0, 10) + "..." : v}"`;
      return String(v);
    }
    case "variable":
      return `$${value.name}`;
    case "reporter":
      return `[reporter]`;
    case "workflow_call":
      return `→ ${value.name}`;
    default:
      return "";
  }
}

// Reporter nesting constants (must match WorkflowNode.tsx)
const REPORTER_PADDING = 12;
const REPORTER_GAP = 8;
const REPORTER_LABEL_HEIGHT = 16;
const INPUT_SLOT_HEIGHT = 28;

// Calculate reporter dimensions recursively (mirrors WorkflowNode logic)
function calculateReporterDimensions(
  value: FormattedValue,
  expandedReporters: Record<string, boolean>,
): { width: number; height: number } {
  if (value.type !== "reporter" || !value.opcode) {
    return { width: 0, height: 0 };
  }

  const reporterId = value.id || "";
  const isExpanded = expandedReporters[reporterId] ?? false;

  // If collapsed, just return minimum node size
  if (!isExpanded) {
    return { width: NODE_WIDTH, height: NODE_HEIGHT };
  }

  // Separate nested reporters from regular inputs
  const nestedReporters: FormattedValue[] = [];
  let regularInputCount = 0;

  if (value.inputs) {
    for (const nestedValue of Object.values(value.inputs)) {
      if (nestedValue.type === "reporter" && nestedValue.opcode) {
        nestedReporters.push(nestedValue);
      } else {
        regularInputCount++;
      }
    }
  }

  let contentWidth: number = NODE_WIDTH;
  let contentHeight: number = NODE_HEIGHT;

  // Add height for nested reporters
  if (nestedReporters.length > 0) {
    let childrenHeight = 0;
    let maxChildWidth = 0;

    for (const nested of nestedReporters) {
      const childDims = calculateReporterDimensions(nested, expandedReporters);
      childrenHeight += REPORTER_LABEL_HEIGHT + childDims.height + REPORTER_GAP;
      maxChildWidth = Math.max(maxChildWidth, childDims.width);
    }

    contentWidth = Math.max(contentWidth, maxChildWidth + REPORTER_PADDING * 2);
    contentHeight = NODE_HEIGHT + childrenHeight;
  }

  // Add height for input slots when expanded
  if (regularInputCount > 0) {
    contentHeight += regularInputCount * INPUT_SLOT_HEIGHT + REPORTER_GAP;
  }

  // Add bottom padding if there's content
  if (nestedReporters.length > 0 || regularInputCount > 0) {
    contentHeight += REPORTER_PADDING;
  }

  return { width: contentWidth, height: contentHeight };
}

// Calculate total dimensions for all reporter inputs on a node
function calculateAllReportersDimensions(
  inputs: Record<string, FormattedValue>,
  expandedReporters: Record<string, boolean>,
): { width: number; height: number } {
  let totalHeight = 0;
  let maxWidth: number = NODE_WIDTH;

  for (const value of Object.values(inputs)) {
    if (value.type === "reporter" && value.opcode) {
      const dims = calculateReporterDimensions(value, expandedReporters);
      totalHeight += REPORTER_LABEL_HEIGHT + dims.height + REPORTER_GAP;
      maxWidth = Math.max(maxWidth, dims.width);
    }
  }

  return { width: maxWidth, height: totalHeight };
}

// Calculate node dimensions based on inputs, branches, and expansion state
export function calculateNodeDimensions(
  nodeId: string,
  inputs: Record<string, FormattedValue>,
  opcode: string | undefined,
  expandedReporters: Record<string, boolean>,
): { width: number; height: number } {
  // Check if this node is expanded
  const isExpanded = expandedReporters[nodeId] ?? false;

  const controlFlowOpcodes = getControlFlowOpcodeSet();
  const hasBranchSlots = opcode && controlFlowOpcodes.has(opcode);
  const branchSlotsHeight = hasBranchSlots ? 20 : 0;

  // If not expanded, return minimum size
  if (!isExpanded) {
    return { width: NODE_WIDTH, height: NODE_HEIGHT + branchSlotsHeight };
  }

  // Calculate expanded dimensions
  const reporterDims = calculateAllReportersDimensions(inputs, expandedReporters);
  const reporterWidth = reporterDims.width + REPORTER_PADDING * 2;
  const reporterHeight = reporterDims.height;

  return {
    width: Math.max(NODE_WIDTH, reporterWidth),
    height: NODE_HEIGHT + reporterHeight + branchSlotsHeight,
  };
}

// Calculate node height based on inputs and branches (legacy, uses minimum height)
export function calculateNodeHeight(
  _inputs: Record<string, FormattedValue>,
  opcode?: string,
): number {
  // Compact node design - minimal height, reporters hidden by default
  const controlFlowOpcodes = getControlFlowOpcodeSet();
  const hasBranchSlots = opcode && controlFlowOpcodes.has(opcode);
  const branchSlotsHeight = hasBranchSlots ? 20 : 0;

  return NODE_HEIGHT + branchSlotsHeight;
}

// Position interface
export interface Position {
  x: number;
  y: number;
}

// Calculate position with offset
export function applyPositionOffset(
  basePosition: Position,
  offset: Position | undefined,
): Position {
  if (!offset) return basePosition;
  return {
    x: basePosition.x + offset.x,
    y: basePosition.y + offset.y,
  };
}

// Calculate canvas coordinates from screen coordinates
export function screenToCanvas(
  screenX: number,
  screenY: number,
  panX: number,
  panY: number,
  zoom: number,
): Position {
  return {
    x: (screenX - panX) / zoom,
    y: (screenY - panY) / zoom,
  };
}

// Calculate screen coordinates from canvas coordinates
export function canvasToScreen(
  canvasX: number,
  canvasY: number,
  panX: number,
  panY: number,
  zoom: number,
): Position {
  return {
    x: canvasX * zoom + panX,
    y: canvasY * zoom + panY,
  };
}

// Clamp zoom to valid range
export function clampZoom(zoom: number, minZoom = 0.25, maxZoom = 2): number {
  return Math.max(minZoom, Math.min(maxZoom, zoom));
}

// Calculate bounding box for a set of positions
export interface BoundingBox {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
  width: number;
  height: number;
}

export function calculateBoundingBox(
  positions: Position[],
): BoundingBox | null {
  if (positions.length === 0) return null;

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const pos of positions) {
    minX = Math.min(minX, pos.x);
    minY = Math.min(minY, pos.y);
    maxX = Math.max(maxX, pos.x);
    maxY = Math.max(maxY, pos.y);
  }

  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

// Calculate center of a bounding box
export function calculateCenter(box: BoundingBox): Position {
  return {
    x: box.minX + box.width / 2,
    y: box.minY + box.height / 2,
  };
}

// Get branch color by name
export function getBranchColor(name: string): string {
  return grammarGetBranchColor(name);
}

// Layout all workflows with custom position offsets
export function layoutAllWorkflows(
  workflows: WorkflowNode[],
  positionOffsets: Record<string, { x: number; y: number }>,
  nodePositionOffsets: Record<string, { x: number; y: number }> = {},
  expandedReporters: Record<string, boolean> = {},
): FullLayout {
  const allNodes: LayoutNode[] = [];
  const allConnections: LayoutConnection[] = [];
  const groups: LayoutWorkflowGroup[] = [];
  const startNodes: LayoutStartNode[] = [];

  // First pass: calculate default positions (stacked vertically)
  let defaultY = 0;
  const defaultPositions: Record<string, { x: number; y: number }> = {};

  for (const workflow of workflows) {
    defaultPositions[workflow.name] = { x: 0, y: defaultY };
    const estimatedHeight = Math.max(
      workflow.children.length * (NODE_HEIGHT + V_GAP),
      NODE_HEIGHT + 100,
    );
    defaultY += estimatedHeight + WORKFLOW_GAP;
  }

  // Second pass: layout each workflow at default position + offset
  for (const workflow of workflows) {
    const defaultPos = defaultPositions[workflow.name];
    const offset = positionOffsets[workflow.name] || { x: 0, y: 0 };
    const pos = { x: defaultPos.x + offset.x, y: defaultPos.y + offset.y };

    const { nodes, connections, bounds, startNode } = layoutSingleWorkflow(
      workflow,
      pos.x,
      pos.y,
      nodePositionOffsets,
      expandedReporters,
    );

    allNodes.push(...nodes);
    allConnections.push(...connections);
    if (startNode) {
      startNodes.push(startNode);
    }

    groups.push({
      name: workflow.name,
      x: bounds.minX,
      y: bounds.minY,
      width: bounds.maxX - bounds.minX,
      height: bounds.maxY - bounds.minY,
      isMain: workflow.name === "main",
    });
  }

  return { nodes: allNodes, connections: allConnections, groups, startNodes };
}

// Layout a single workflow starting at given offset
export function layoutSingleWorkflow(
  workflow: WorkflowNode,
  offsetX: number,
  offsetY: number,
  nodePositionOffsets: Record<string, { x: number; y: number }> = {},
  expandedReporters: Record<string, boolean> = {},
): {
  nodes: LayoutNode[];
  connections: LayoutConnection[];
  bounds: { minX: number; minY: number; maxX: number; maxY: number };
  startNode: LayoutStartNode | null;
} {
  const layoutNodes: LayoutNode[] = [];
  const connections: LayoutConnection[] = [];
  const nodePositions = new Map<
    string,
    { x: number; y: number; width: number; height: number }
  >();

  // Calculate start node position
  const startNodeX = offsetX;
  const startNodeY = offsetY;
  const startNode: LayoutStartNode = {
    workflowName: workflow.name,
    workflowInterface: workflow.interface,
    variables: workflow.variables,
    x: startNodeX,
    y: startNodeY,
  };

  // Offset for real nodes (after the start node)
  const realNodeOffsetX = offsetX + START_NODE_WIDTH + START_NODE_GAP;

  // Track bounds
  let minX = Infinity,
    minY = Infinity,
    maxX = -Infinity,
    maxY = -Infinity;

  function updateBounds(x: number, y: number, width: number, height: number) {
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x + width);
    maxY = Math.max(maxY, y + height);
  }

  // Layout main flow
  function layoutNode(
    node: TreeNode,
    x: number,
    y: number,
    isOrphan: boolean = false,
  ): number {
    const dims = calculateNodeDimensions(node.id, node.inputs, node.opcode, expandedReporters);

    layoutNodes.push({
      node,
      x,
      y,
      width: dims.width,
      height: dims.height,
      isOrphan,
    });
    nodePositions.set(node.id, { x, y, width: dims.width, height: dims.height });
    updateBounds(x, y, dims.width, dims.height);

    let nextX = x + dims.width + H_GAP;

    // Layout branch children
    if (node.children.length > 0) {
      let branchOffset = y + dims.height + V_GAP;
      const numBranches = node.children.length;

      for (let branchIndex = 0; branchIndex < numBranches; branchIndex++) {
        const branch = node.children[branchIndex];
        const branchColor = getBranchColor(branch.name);

        let branchX = x + dims.width + H_GAP;
        let prevNodeId = node.id;
        let isFirstInBranch = true;

        for (const childNode of branch.children) {
          const childDims = calculateNodeDimensions(
            childNode.id,
            childNode.inputs,
            childNode.opcode,
            expandedReporters,
          );

          layoutNodes.push({
            node: childNode,
            x: branchX,
            y: branchOffset,
            width: childDims.width,
            height: childDims.height,
          });
          nodePositions.set(childNode.id, {
            x: branchX,
            y: branchOffset,
            width: childDims.width,
            height: childDims.height,
          });
          updateBounds(branchX, branchOffset, childDims.width, childDims.height);

          connections.push({
            from: prevNodeId,
            to: childNode.id,
            fromPort: isFirstInBranch ? branch.name : "output",
            toPort: "input",
            color: branchColor,
            label: isFirstInBranch ? branch.name : undefined,
          });

          prevNodeId = childNode.id;
          isFirstInBranch = false;
          branchX += childDims.width + H_GAP;

          if (childNode.children.length > 0) {
            branchX = Math.max(
              branchX,
              layoutBranches(childNode, branchX, branchOffset),
            );
          }
        }

        nextX = Math.max(nextX, branchX);
        branchOffset += NODE_HEIGHT + V_GAP * 2;
      }
    }

    return nextX;
  }

  function layoutBranches(
    node: TreeNode,
    startX: number,
    startY: number,
  ): number {
    let maxX = startX;
    const nodePos = nodePositions.get(node.id);
    const nodeHeight = nodePos?.height || NODE_HEIGHT;
    let branchY = startY + nodeHeight + V_GAP;
    const numBranches = node.children.length;

    for (let branchIndex = 0; branchIndex < numBranches; branchIndex++) {
      const branch = node.children[branchIndex];
      const branchColor = getBranchColor(branch.name);
      let branchX = startX;

      let prevNodeId = node.id;
      let isFirstInBranch = true;

      for (const childNode of branch.children) {
        const childDims = calculateNodeDimensions(
          childNode.id,
          childNode.inputs,
          childNode.opcode,
          expandedReporters,
        );

        layoutNodes.push({
          node: childNode,
          x: branchX,
          y: branchY,
          width: childDims.width,
          height: childDims.height,
        });
        nodePositions.set(childNode.id, {
          x: branchX,
          y: branchY,
          width: childDims.width,
          height: childDims.height,
        });
        updateBounds(branchX, branchY, childDims.width, childDims.height);

        connections.push({
          from: prevNodeId,
          to: childNode.id,
          fromPort: isFirstInBranch ? branch.name : "output",
          toPort: "input",
          color: branchColor,
          label: isFirstInBranch ? branch.name : undefined,
        });

        prevNodeId = childNode.id;
        isFirstInBranch = false;
        branchX += childDims.width + H_GAP;
      }

      maxX = Math.max(maxX, branchX);
      branchY += NODE_HEIGHT + V_GAP;
    }

    return maxX;
  }

  // Include start node in bounds
  updateBounds(startNodeX, startNodeY, START_NODE_WIDTH, START_NODE_HEIGHT);

  // Layout all nodes in the workflow
  let x = realNodeOffsetX;
  let prevNode: TreeNode | null = null;
  let isFirstNode = true;

  for (const node of workflow.children) {
    const y = offsetY;
    const nextX = layoutNode(node, x, y);

    // Connect start node to first real node
    if (isFirstNode) {
      connections.push({
        from: `start-${workflow.name}`,
        to: node.id,
        fromPort: "output",
        toPort: "input",
        color: "#22C55E",
      });
      isFirstNode = false;
    }

    // Connect sequential nodes
    if (prevNode) {
      connections.push({
        from: prevNode.id,
        to: node.id,
        fromPort: "output",
        toPort: "input",
        color: "#475569",
      });
    }

    prevNode = node;
    x = nextX;
  }

  // Handle empty workflow
  if (workflow.children.length === 0) {
    minX = Math.min(minX, startNodeX);
    minY = Math.min(minY, startNodeY);
    maxX = Math.max(maxX, startNodeX + START_NODE_WIDTH + 20);
    maxY = Math.max(maxY, startNodeY + START_NODE_HEIGHT);
  }

  // Layout orphan nodes
  const orphans = workflow.orphans || [];
  if (orphans.length > 0) {
    const orphanY = maxY + WORKFLOW_GAP;
    let orphanX = startNodeX;

    for (const orphan of orphans) {
      orphanX = layoutNode(orphan, orphanX, orphanY, true);
    }

    // Create connections between orphan chain nodes
    for (const orphan of orphans) {
      if (orphan.next) {
        connections.push({
          from: orphan.id,
          to: orphan.next,
          fromPort: "output",
          toPort: "input",
          color: "#6B7280",
        });
      }
    }
  }

  // Apply node position offsets (for free layout mode)
  for (const layoutNode of layoutNodes) {
    const offset = nodePositionOffsets[layoutNode.node.id];
    if (offset) {
      layoutNode.x += offset.x;
      layoutNode.y += offset.y;
      updateBounds(
        layoutNode.x,
        layoutNode.y,
        layoutNode.width,
        layoutNode.height,
      );
    }
  }

  return {
    nodes: layoutNodes,
    connections,
    bounds: { minX, minY, maxX, maxY },
    startNode,
  };
}

// Find which workflow group contains a given point
export function getWorkflowUnderPoint(
  groups: LayoutWorkflowGroup[],
  x: number,
  y: number,
): string | null {
  // Padding for hit detection - accounts for label area above group and general tolerance
  const labelHeight = 28;
  const padding = 16;

  // Sort by y position descending (bottom to top) so lower workflows take priority
  // This handles the case where dropping near the top border of a workflow
  const sortedGroups = [...groups].sort((a, b) => b.y - a.y);

  for (const group of sortedGroups) {
    // Expand hit area to include label above and some padding around edges
    if (
      x >= group.x - padding &&
      x <= group.x + group.width + padding &&
      y >= group.y - labelHeight - padding &&
      y <= group.y + group.height + padding
    ) {
      return group.name;
    }
  }
  return null;
}

// Export as service object
export const layoutService = {
  calculateReporterTotalHeight,
  formatValueShort,
  calculateNodeHeight,
  applyPositionOffset,
  screenToCanvas,
  canvasToScreen,
  clampZoom,
  calculateBoundingBox,
  calculateCenter,
  getBranchColor,
  layoutAllWorkflows,
  layoutSingleWorkflow,
  getWorkflowUnderPoint,
};
