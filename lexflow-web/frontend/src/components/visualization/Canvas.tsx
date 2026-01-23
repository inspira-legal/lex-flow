import { useRef, useState, useCallback, useEffect, useMemo } from "react";
import { useUiStore, useWorkflowStore } from "../../store";
import { WorkflowNode } from "./WorkflowNode";
import { StartNode, START_NODE_WIDTH, START_NODE_HEIGHT } from "./StartNode";
import { Connection } from "./Connection";
import { WireDragPreview } from "./WireDragPreview";
import { OrphanDragPreview } from "./OrphanDragPreview";
import { VariableDragPreview } from "./VariableDragPreview";
import { MiniMap } from "./MiniMap";
import { NodeSearch } from "./NodeSearch";
import { WorkflowGroup } from "./WorkflowGroup";
import { findNearestPortFromRegistry } from "../../utils/wireUtils";
import { NODE_DIMENSIONS, LAYOUT_GAPS } from "../../constants";
import { calculateNodeHeight } from "../../services/layout/LayoutService";
import type {
  TreeNode,
  WorkflowNode as WorkflowNodeType,
  WorkflowInterface,
} from "../../api/types";
import styles from "./Canvas.module.css";

interface LayoutNode {
  node: TreeNode;
  x: number;
  y: number;
  width: number;
  height: number;
  isOrphan?: boolean; // Whether this node is disconnected from the main chain
}

interface LayoutConnection {
  from: string;
  to: string;
  fromPort: "input" | "output" | string; // string for branch names
  toPort: "input" | "output";
  color: string;
  label?: string;
}

interface LayoutWorkflowGroup {
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  isMain: boolean;
}

interface LayoutStartNode {
  workflowName: string;
  workflowInterface: WorkflowInterface;
  variables: Record<string, unknown>;
  x: number;
  y: number;
}

interface FullLayout {
  nodes: LayoutNode[];
  connections: LayoutConnection[];
  groups: LayoutWorkflowGroup[];
  startNodes: LayoutStartNode[];
}

// Use constants from centralized module
const NODE_WIDTH = NODE_DIMENSIONS.WIDTH;
const NODE_HEIGHT = NODE_DIMENSIONS.HEIGHT;
const H_GAP = LAYOUT_GAPS.HORIZONTAL;
const V_GAP = LAYOUT_GAPS.VERTICAL;
const WORKFLOW_GAP = LAYOUT_GAPS.WORKFLOW;

export function Canvas() {
  const {
    zoom,
    panX,
    panY,
    setZoom,
    setPan,
    resetView,
    workflowPositions,
    setWorkflowPosition,
    isDraggingWorkflow,
    draggingWire,
    setDraggingWire,
    updateDraggingWire,
    draggingOrphan,
    setDraggingOrphan,
    updateDraggingOrphanEnd,
    draggingVariable,
    setDraggingVariable,
    updateDraggingVariableEnd,
    nodePositions,
    setNodePosition,
    resetNodePositions,
    layoutMode,
    setLayoutMode,
    isDraggingNode,
    selectStartNode,
    selectedConnection,
    selectConnection,
    slotPositions,
  } = useUiStore();
  const {
    tree,
    parseError,
    selectNode,
    connectNodes,
    connectBranch,
    disconnectConnection,
  } = useWorkflowStore();

  const svgRef = useRef<SVGSVGElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });

  // Track canvas size for minimap viewport calculation
  useEffect(() => {
    const updateSize = () => {
      if (svgRef.current) {
        setCanvasSize({
          width: svgRef.current.clientWidth,
          height: svgRef.current.clientHeight,
        });
      }
    };

    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, []);

  // Layout all workflows (moved up for centerX/centerY calculation)
  const {
    nodes: layoutNodes,
    connections,
    groups,
    startNodes,
  } = tree
    ? layoutAllWorkflows(tree.workflows, workflowPositions, nodePositions)
    : { nodes: [], connections: [], groups: [], startNodes: [] };

  // Calculate canvas bounds (include group padding)
  const groupPadding = 24;
  const labelHeight = 28;
  const bounds =
    groups.length > 0
      ? groups.reduce(
          (acc, g) => ({
            minX: Math.min(acc.minX, g.x - groupPadding),
            minY: Math.min(acc.minY, g.y - groupPadding - labelHeight),
            maxX: Math.max(acc.maxX, g.x + g.width + groupPadding),
            maxY: Math.max(acc.maxY, g.y + g.height + groupPadding),
          }),
          { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity },
        )
      : { minX: 0, minY: 0, maxX: 800, maxY: 600 };

  // Calculate initial center only when tree changes (not when dragging workflows)
  const { centerX, centerY } = useMemo(() => {
    if (!tree) return { centerX: 400, centerY: 300 };

    // Calculate bounds based on default layout (no position offsets)
    const defaultLayout = layoutAllWorkflows(tree.workflows, {});
    const defaultBounds = defaultLayout.groups.reduce(
      (acc, g) => ({
        minX: Math.min(acc.minX, g.x - groupPadding),
        minY: Math.min(acc.minY, g.y - groupPadding - labelHeight),
        maxX: Math.max(acc.maxX, g.x + g.width + groupPadding),
        maxY: Math.max(acc.maxY, g.y + g.height + groupPadding),
      }),
      { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity },
    );

    return {
      centerX: (defaultBounds.maxX + defaultBounds.minX) / 2,
      centerY: (defaultBounds.maxY + defaultBounds.minY) / 2,
    };
  }, [tree]);

  // Handle zoom
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        setZoom(zoom + delta);
      }
    },
    [zoom, setZoom],
  );

  // Handle pan
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (isDraggingWorkflow || isDraggingNode) return;
      if (
        e.target === svgRef.current ||
        (e.target as Element).classList.contains(styles.background)
      ) {
        setIsDragging(true);
        setDragStart({ x: e.clientX - panX, y: e.clientY - panY });
        selectNode(null);
        selectStartNode(null);
        selectConnection(null);
      }
    },
    [
      panX,
      panY,
      selectNode,
      selectStartNode,
      selectConnection,
      isDraggingWorkflow,
      isDraggingNode,
    ],
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      // Handle wire dragging - update wire end position with proximity detection
      if (draggingWire && svgRef.current) {
        const rect = svgRef.current.getBoundingClientRect();
        // Convert screen coordinates to canvas coordinates (accounting for pan/zoom)
        const canvasX =
          (e.clientX - rect.left - panX - rect.width / 2) / zoom + centerX;
        const canvasY =
          (e.clientY - rect.top - panY - rect.height / 2) / zoom + centerY;

        // Find nearest valid port using slot registry
        const nearbyPort = findNearestPortFromRegistry(
          canvasX,
          canvasY,
          draggingWire.sourceNodeId,
          draggingWire.sourcePort,
          slotPositions,
        );

        // Update state with drag position and nearby port
        updateDraggingWire({
          dragX: canvasX,
          dragY: canvasY,
          nearbyPort,
        });
        return;
      }

      // Handle orphan dragging - update orphan end position
      if (draggingOrphan && svgRef.current) {
        const rect = svgRef.current.getBoundingClientRect();
        const canvasX =
          (e.clientX - rect.left - panX - rect.width / 2) / zoom + centerX;
        const canvasY =
          (e.clientY - rect.top - panY - rect.height / 2) / zoom + centerY;
        updateDraggingOrphanEnd(canvasX, canvasY);
        return;
      }

      // Handle variable dragging - update variable end position
      if (draggingVariable && svgRef.current) {
        const rect = svgRef.current.getBoundingClientRect();
        const canvasX =
          (e.clientX - rect.left - panX - rect.width / 2) / zoom + centerX;
        const canvasY =
          (e.clientY - rect.top - panY - rect.height / 2) / zoom + centerY;
        updateDraggingVariableEnd(canvasX, canvasY);
        return;
      }

      if (isDraggingWorkflow || isDraggingNode) return;
      if (isDragging) {
        setPan(e.clientX - dragStart.x, e.clientY - dragStart.y);
      }
    },
    [
      isDragging,
      dragStart,
      setPan,
      isDraggingWorkflow,
      isDraggingNode,
      draggingWire,
      updateDraggingWire,
      draggingOrphan,
      updateDraggingOrphanEnd,
      draggingVariable,
      updateDraggingVariableEnd,
      zoom,
      panX,
      panY,
      centerX,
      centerY,
      slotPositions,
    ],
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    // Complete wire connection if near a valid port, otherwise cancel
    if (draggingWire) {
      if (draggingWire.nearbyPort) {
        // Check if this is a branch connection
        if (draggingWire.branchLabel) {
          // Branch connection: connect branch to target node
          connectBranch(
            draggingWire.sourceNodeId,
            draggingWire.nearbyPort.nodeId,
            draggingWire.branchLabel,
          );
        } else if (draggingWire.sourcePort === "output") {
          // Regular connection: dragging from output to input
          connectNodes(
            draggingWire.sourceNodeId,
            draggingWire.nearbyPort.nodeId,
          );
        } else {
          // Reverse connection: dragging from input to output
          connectNodes(
            draggingWire.nearbyPort.nodeId,
            draggingWire.sourceNodeId,
          );
        }
      }
      setDraggingWire(null);
    }
    // Cancel orphan dragging if mouse released outside a valid drop target
    if (draggingOrphan) {
      setDraggingOrphan(null);
    }
    // Cancel variable dragging if mouse released outside a valid drop target
    if (draggingVariable) {
      setDraggingVariable(null);
    }
  }, [
    draggingWire,
    setDraggingWire,
    draggingOrphan,
    setDraggingOrphan,
    draggingVariable,
    setDraggingVariable,
    connectNodes,
    connectBranch,
  ]);

  // Handle minimap navigation
  const handleMinimapNavigate = useCallback(
    (newPanX: number, newPanY: number) => {
      setPan(newPanX, newPanY);
    },
    [setPan],
  );

  return (
    <div className={styles.canvas}>
      {/* Node Search */}
      <NodeSearch />

      {/* Zoom Controls */}
      <div className={styles.zoomControls}>
        <button onClick={() => setZoom(zoom - 0.1)} title="Zoom Out">
          −
        </button>
        <span className={styles.zoomLevel}>{Math.round(zoom * 100)}%</span>
        <button onClick={() => setZoom(zoom + 0.1)} title="Zoom In">
          +
        </button>
        <button onClick={resetView} title="Reset View">
          ⌂
        </button>
      </div>

      {/* Layout Mode Controls */}
      <div className={styles.layoutControls}>
        <button
          className={layoutMode === "auto" ? styles.active : ""}
          onClick={() => setLayoutMode("auto")}
          title="Auto Layout"
        >
          Auto
        </button>
        <button
          className={layoutMode === "free" ? styles.active : ""}
          onClick={() => setLayoutMode("free")}
          title="Free Layout (drag nodes)"
        >
          Free
        </button>
        {layoutMode === "free" && Object.keys(nodePositions).length > 0 && (
          <button onClick={resetNodePositions} title="Reset Node Positions">
            Reset
          </button>
        )}
      </div>

      {/* Mini-map */}
      {tree && (
        <MiniMap
          workflows={tree.workflows}
          bounds={bounds}
          zoom={zoom}
          panX={panX}
          panY={panY}
          canvasWidth={canvasSize.width}
          canvasHeight={canvasSize.height}
          onNavigate={handleMinimapNavigate}
        />
      )}

      {/* Error display */}
      {parseError && (
        <div className={styles.errorOverlay}>
          <span className={styles.errorIcon}>⚠</span>
          <span>{parseError}</span>
        </div>
      )}

      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        className={styles.svg}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isDragging ? "grabbing" : "grab" }}
      >
        {/* Background for click handling */}
        <rect
          className={styles.background}
          width="100%"
          height="100%"
          fill="transparent"
        />

        {/* Main group with pan/zoom transform */}
        <g
          transform={`translate(${panX + (svgRef.current?.clientWidth || 800) / 2 - centerX * zoom}, ${panY + (svgRef.current?.clientHeight || 600) / 2 - centerY * zoom}) scale(${zoom})`}
        >
          {/* Workflow groups (render first, as background) */}
          {groups.map((group) => (
            <WorkflowGroup
              key={group.name}
              name={group.name}
              x={group.x}
              y={group.y}
              width={group.width}
              height={group.height}
              isMain={group.isMain}
              zoom={zoom}
              onDrag={(dx, dy) => {
                // Read current position from store to avoid stale closure
                const currentOffset = useUiStore.getState().workflowPositions[
                  group.name
                ] || { x: 0, y: 0 };
                setWorkflowPosition(
                  group.name,
                  currentOffset.x + dx,
                  currentOffset.y + dy,
                );
              }}
            />
          ))}

          {/* Connections (render second, below nodes) */}
          {connections.map((conn, i) => (
            <Connection
              key={`${conn.from}-${conn.to}-${i}`}
              fromNodeId={conn.from}
              toNodeId={conn.to}
              fromPort={conn.fromPort}
              toPort={conn.toPort}
              color={conn.color}
              label={conn.label}
              isSelected={
                selectedConnection?.fromNodeId === conn.from &&
                selectedConnection?.toNodeId === conn.to
              }
              onSelect={() =>
                selectConnection({
                  fromNodeId: conn.from,
                  toNodeId: conn.to,
                  label: conn.label,
                })
              }
              onDelete={() => {
                disconnectConnection(conn.from, conn.to, conn.label);
                selectConnection(null);
              }}
            />
          ))}

          {/* Start Nodes */}
          {startNodes.map((sn) => (
            <StartNode
              key={`start-${sn.workflowName}`}
              workflowName={sn.workflowName}
              workflowInterface={sn.workflowInterface}
              variables={sn.variables}
              x={sn.x}
              y={sn.y}
              zoom={zoom}
              onDrag={
                layoutMode === "free"
                  ? (dx, dy) => {
                      const currentOffset = workflowPositions[
                        sn.workflowName
                      ] || { x: 0, y: 0 };
                      setWorkflowPosition(
                        sn.workflowName,
                        currentOffset.x + dx,
                        currentOffset.y + dy,
                      );
                    }
                  : undefined
              }
            />
          ))}

          {/* Nodes */}
          {layoutNodes.map((ln) => (
            <WorkflowNode
              key={ln.node.id}
              node={ln.node}
              x={ln.x}
              y={ln.y}
              isOrphan={ln.isOrphan}
              zoom={zoom}
              onDrag={
                layoutMode === "free"
                  ? (dx, dy) => {
                      const currentOffset = nodePositions[ln.node.id] || {
                        x: 0,
                        y: 0,
                      };
                      setNodePosition(
                        ln.node.id,
                        currentOffset.x + dx,
                        currentOffset.y + dy,
                      );
                    }
                  : undefined
              }
            />
          ))}

          {/* Wire drag preview (rendered last, on top) */}
          <WireDragPreview />

          {/* Orphan drag preview */}
          <OrphanDragPreview />

          {/* Variable drag preview */}
          <VariableDragPreview />
        </g>
      </svg>

      {/* Empty state */}
      {!parseError && !tree && (
        <div className={styles.emptyState}>
          <h2>No Workflow</h2>
          <p>Edit YAML in the editor or load an example</p>
        </div>
      )}
    </div>
  );
}

// Gap between start node and first real node
const START_NODE_GAP = 40;

// Layout all workflows with custom position offsets
function layoutAllWorkflows(
  workflows: WorkflowNodeType[],
  positionOffsets: Record<string, { x: number; y: number }>,
  nodePositionOffsets: Record<string, { x: number; y: number }> = {},
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
    // Estimate height for default stacking
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
    );

    allNodes.push(...nodes);
    allConnections.push(...connections);
    if (startNode) {
      startNodes.push(startNode);
    }

    // Add workflow group
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
function layoutSingleWorkflow(
  workflow: WorkflowNodeType,
  offsetX: number,
  offsetY: number,
  nodePositionOffsets: Record<string, { x: number; y: number }> = {},
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
    { x: number; y: number; height: number }
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
    // Calculate height including nested reporters
    const height = calculateNodeHeight(node.inputs, node.opcode);

    layoutNodes.push({
      node,
      x,
      y,
      width: NODE_WIDTH,
      height,
      isOrphan,
    });
    nodePositions.set(node.id, { x, y, height });
    updateBounds(x, y, NODE_WIDTH, height);

    let nextX = x + NODE_WIDTH + H_GAP;

    // Layout branch children
    if (node.children.length > 0) {
      let branchOffset = y + height + V_GAP;
      const numBranches = node.children.length;

      for (let branchIndex = 0; branchIndex < numBranches; branchIndex++) {
        const branch = node.children[branchIndex];
        const branchColor = getBranchColor(branch.name);

        // Layout branch nodes
        let branchX = x + NODE_WIDTH + H_GAP;
        let prevNodeId = node.id;
        let isFirstInBranch = true;

        for (const childNode of branch.children) {
          const childHeight = calculateNodeHeight(
            childNode.inputs,
            childNode.opcode,
          );

          layoutNodes.push({
            node: childNode,
            x: branchX,
            y: branchOffset,
            width: NODE_WIDTH,
            height: childHeight,
          });
          nodePositions.set(childNode.id, {
            x: branchX,
            y: branchOffset,
            height: childHeight,
          });
          updateBounds(branchX, branchOffset, NODE_WIDTH, childHeight);

          // Connection - use port names instead of coordinates
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
          branchX += NODE_WIDTH + H_GAP;

          // Recursively layout nested branches
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
        const childHeight = calculateNodeHeight(
          childNode.inputs,
          childNode.opcode,
        );

        layoutNodes.push({
          node: childNode,
          x: branchX,
          y: branchY,
          width: NODE_WIDTH,
          height: childHeight,
        });
        nodePositions.set(childNode.id, {
          x: branchX,
          y: branchY,
          height: childHeight,
        });
        updateBounds(branchX, branchY, NODE_WIDTH, childHeight);

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
        branchX += NODE_WIDTH + H_GAP;
      }

      maxX = Math.max(maxX, branchX);
      branchY += NODE_HEIGHT + V_GAP;
    }

    return maxX;
  }

  // Include start node in bounds
  updateBounds(startNodeX, startNodeY, START_NODE_WIDTH, START_NODE_HEIGHT);

  // Layout all nodes in the workflow (starting after the start node)
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
        color: "#22C55E", // Green color for start connection
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

  // Handle empty workflow (just start node)
  if (workflow.children.length === 0) {
    minX = Math.min(minX, startNodeX);
    minY = Math.min(minY, startNodeY);
    maxX = Math.max(maxX, startNodeX + START_NODE_WIDTH + 20);
    maxY = Math.max(maxY, startNodeY + START_NODE_HEIGHT);
  }

  // Layout orphan nodes in a separate row below the main workflow
  const orphans = workflow.orphans || [];
  if (orphans.length > 0) {
    const orphanY = maxY + WORKFLOW_GAP;
    let orphanX = startNodeX;

    for (const orphan of orphans) {
      // Use layoutNode to properly handle branches and connections
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
          color: "#6B7280", // Gray color for orphan chains
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
      // Update bounds
      updateBounds(
        layoutNode.x,
        layoutNode.y,
        layoutNode.width,
        layoutNode.height,
      );
    }
  }

  // Note: Connection coordinates are now read from slot registry (updated via useEffect in nodes)
  // so no need to recalculate them here

  return {
    nodes: layoutNodes,
    connections,
    bounds: { minX, minY, maxX, maxY },
    startNode,
  };
}

function getBranchColor(name: string): string {
  // Handle CATCH1, CATCH2, etc.
  if (name.startsWith("CATCH")) {
    return "#F87171"; // Red
  }
  switch (name) {
    case "THEN":
      return "#34D399"; // Green
    case "ELSE":
      return "#F87171"; // Red
    case "BODY":
      return "#22D3EE"; // Cyan
    case "TRY":
      return "#3B82F6"; // Blue
    case "FINALLY":
      return "#FACC15"; // Yellow
    default:
      return "#9C27B0"; // Purple
  }
}
