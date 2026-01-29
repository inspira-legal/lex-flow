import { useRef, useEffect, type ReactElement } from "react";
import { useWorkflowStore, useUiStore } from "../../store";
import type { SelectedReporter, NodeSlotPositions } from "../../store/uiStore";
import type {
  TreeNode,
  FormattedValue,
  NodeType,
  OpcodeParameter,
  BranchNode,
} from "../../api/types";
import { InputSlot } from "./InputSlot";
import { NODE_WIDTH } from "../../utils/wireUtils";
import { getInputDisplayName } from "../../utils/workflowUtils";
import {
  calculateReporterTotalHeight,
  formatValueShort,
} from "../../services/layout/LayoutService";
import { getBranchColor, getBranchSlots as getGrammarBranchSlots } from "../../services/grammar";
import { useNodePorts } from "../../hooks";
import styles from "./WorkflowNode.module.css";


// Get available branch slots for a control flow opcode
function getBranchSlots(
  opcode: string,
  children: BranchNode[],
): Array<{ name: string; connected: boolean }> {
  const connectedNames = children.map((c) => c.name);
  return getGrammarBranchSlots(opcode, connectedNames);
}

interface WorkflowNodeProps {
  node: TreeNode;
  x: number;
  y: number;
  isOrphan?: boolean;
  zoom?: number;
  onDrag?: (dx: number, dy: number) => void;
}

import { getNodeColor, getReporterColor as getGrammarReporterColor } from "../../services/grammar";

const NODE_ICONS: Record<string, string> = {
  control_flow: "⟳",
  data: "📦",
  io: "📤",
  operator: "⚡",
  workflow_op: "🔗",
  opcode: "⚙",
};

export function WorkflowNode({
  node,
  x,
  y,
  isOrphan,
  zoom = 1,
  onDrag,
}: WorkflowNodeProps) {
  const { selectedNodeId, selectNode, opcodes, tree } = useWorkflowStore();
  const {
    openNodeEditor,
    nodeStatus,
    searchResults,
    selectReporter,
    selectedReporter,
    draggingWire,
    draggingOrphan,
    setDraggingOrphan,
    draggingVariable,
    layoutMode,
    setIsDraggingNode,
    registerSlotPositions,
    unregisterSlotPositions,
  } = useUiStore();

  // Get opcode info for this node
  const opcodeInfo = opcodes.find((op) => op.name === node.opcode);

  // Get parameter info map for quick lookup
  const paramInfoMap: Record<string, OpcodeParameter | undefined> = {};
  if (opcodeInfo) {
    for (const param of opcodeInfo.parameters) {
      paramInfoMap[param.name.toUpperCase()] = param;
    }
  }

  const color = getNodeColor(node.type);
  const icon = NODE_ICONS[node.type] || NODE_ICONS.opcode;
  const isSelected = selectedNodeId === node.id && !selectedReporter;
  const isSearchMatch = searchResults.includes(node.id);
  const status = nodeStatus[node.id] || "idle";

  // Track if we just dragged to prevent opening editor after drag
  const justDraggedRef = useRef(false);

  // Use node ports hook for wire connection handling
  const {
    handleOutputPortMouseDown,
    handleInputPortMouseDown,
    handleOutputPortMouseUp,
    handleInputPortMouseUp,
    handleBranchPortMouseDown,
    isInputPortHighlighted,
    isOutputPortHighlighted,
    isValidDropTarget,
    isValidOutputDropTarget,
  } = useNodePorts({ nodeId: node.id, x, y });

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (justDraggedRef.current) {
      justDraggedRef.current = false;
      return;
    }
    selectNode(node.id);
    selectReporter(null);
    openNodeEditor();
  };

  // Handle orphan drag start (for orphan-to-reporter conversion)
  const handleOrphanDragStart = (e: React.MouseEvent) => {
    if (!isOrphan) return;
    e.stopPropagation();
    e.preventDefault();

    const centerX = x + 90; // Center of node (width=180)
    const centerY = y + 30; // Approximate center

    setDraggingOrphan({
      nodeId: node.id,
      opcode: node.opcode,
      returnType: opcodeInfo?.return_type,
      fromX: centerX,
      fromY: centerY,
      toX: centerX,
      toY: centerY,
    });
  };

  // Handle node drag in free layout mode
  const handleNodeDragStart = (e: React.MouseEvent) => {
    if (layoutMode !== "free" || !onDrag) return;
    e.stopPropagation();
    e.preventDefault();

    setIsDraggingNode(true);

    const startX = e.clientX;
    const startY = e.clientY;
    let hasMoved = false;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const dx = (moveEvent.clientX - startX) / zoom;
      const dy = (moveEvent.clientY - startY) / zoom;
      // Only consider it a drag if moved more than 3 pixels
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        hasMoved = true;
        onDrag(dx, dy);
      }
    };

    const handleMouseUp = () => {
      setIsDraggingNode(false);
      if (hasMoved) {
        justDraggedRef.current = true;
      }
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
  };

  // Determine if we show input slots (when orphan or variable is being dragged)
  // - Always show for variables (any node can receive a variable)
  // - For orphans, show unless dragging the SAME orphan onto itself
  const showInputSlots =
    draggingVariable || (draggingOrphan && draggingOrphan.nodeId !== node.id);

  // Extract display name from opcode
  const displayName = formatOpcodeName(node.opcode);

  // Separate reporter inputs from regular inputs
  const reporterInputs: Array<{ key: string; value: FormattedValue }> = [];
  const regularInputs: Array<{ key: string; value: FormattedValue }> = [];

  for (const [key, value] of Object.entries(node.inputs)) {
    if (value.type === "reporter" && value.opcode) {
      reporterInputs.push({ key, value });
    } else {
      regularInputs.push({ key, value });
    }
  }

  // Get preview of regular inputs with friendly display names
  const inputPreview = regularInputs
    .slice(0, 2)
    .map(({ key, value }) => {
      const formatted = formatValueShort(value);
      const displayKey = getInputDisplayName(key, node.opcode, tree, node.inputs);
      return formatted ? { key: displayKey, formatted } : null;
    })
    .filter(Boolean) as Array<{ key: string; formatted: string }>;

  // Calculate heights
  const baseHeight = 60 + inputPreview.length * 18;
  const reporterSectionHeight = reporterInputs.reduce((acc, { value }) => {
    return acc + calculateReporterTotalHeight(value) + 4;
  }, 0);
  // Add extra height for branch slots at bottom for control flow nodes
  const branchSlots = getBranchSlots(node.opcode, node.children);
  const branchSlotsHeight = branchSlots.length > 0 ? 28 : 0;
  const totalHeight = baseHeight + reporterSectionHeight + branchSlotsHeight;

  // Register slot positions for wire alignment
  useEffect(() => {
    const positions: NodeSlotPositions = {
      input: { x, y: y + 30 },
      output: { x: x + NODE_WIDTH, y: y + 30 },
      branches: {},
    };

    branchSlots.forEach((slot, index) => {
      const slotWidth = NODE_WIDTH / branchSlots.length;
      positions.branches[slot.name] = {
        x: x + slotWidth * index + slotWidth / 2,
        y: y + totalHeight,
      };
    });

    registerSlotPositions(node.id, positions);
    return () => unregisterSlotPositions(node.id);
  }, [
    x,
    y,
    totalHeight,
    branchSlots.length,
    node.id,
    registerSlotPositions,
    unregisterSlotPositions,
  ]);

  return (
    <g
      className={`${styles.nodeGroup} ${isSelected ? styles.selected : ""} ${isSearchMatch ? styles.searchMatch : ""} ${isOrphan ? styles.orphan : ""} ${styles[status]}`}
      transform={`translate(${x}, ${y})`}
      onClick={handleClick}
    >
      {/* Node card */}
      <rect
        className={styles.card}
        width={180}
        height={totalHeight}
        rx={8}
        style={{ "--node-color": color } as React.CSSProperties}
      />

      {/* Color bar on left */}
      <rect
        className={styles.colorBar}
        width={4}
        height={totalHeight}
        rx={2}
        fill={color}
      />

      {/* Icon */}
      <text className={styles.icon} x={16} y={24}>
        {icon}
      </text>

      {/* Node name */}
      <text className={styles.name} x={36} y={24}>
        {displayName}
      </text>

      {/* Node ID (dimmed) */}
      <text className={styles.id} x={36} y={40}>
        {node.id}
      </text>

      {/* Regular input preview / Input slots */}
      {showInputSlots
        ? // Show input slots when an orphan is being dragged (drop targets)
          regularInputs
            .slice(0, 3)
            .map(({ key }, i) => (
              <InputSlot
                key={key}
                nodeId={node.id}
                inputKey={key}
                value={regularInputs[i].value}
                paramInfo={paramInfoMap[key]}
                opcode={node.opcode}
                allInputs={node.inputs}
                x={8}
                y={52 + i * 18}
                width={164}
              />
            ))
        : // Show regular input preview
          inputPreview.map((input, i) => (
            <g key={input.key}>
              <text className={styles.inputKey} x={12} y={56 + i * 18}>
                {input.key}:
              </text>
              <text
                className={styles.input}
                x={12 + (input.key.length + 1) * 6}
                y={56 + i * 18}
              >
                {input.formatted}
              </text>
            </g>
          ))}

      {/* Nested reporter blocks */}
      {reporterInputs.length > 0 && (
        <g transform={`translate(8, ${baseHeight - 4})`}>
          {renderNestedReporters(
            reporterInputs,
            0,
            true,
            node.id,
            [],
            selectReporter,
            selectedReporter,
          )}
        </g>
      )}

      {/* Connection points */}
      {/* Larger invisible hit area for input port when wire is being dragged from output */}
      {isValidDropTarget && (
        <circle
          cx={0}
          cy={30}
          r={20}
          fill="transparent"
          style={{ cursor: "pointer" }}
          onMouseUp={handleInputPortMouseUp}
        />
      )}
      {/* Larger invisible hit area for output port when wire is being dragged from input */}
      {isValidOutputDropTarget && (
        <circle
          cx={NODE_WIDTH}
          cy={30}
          r={20}
          fill="transparent"
          style={{ cursor: "pointer" }}
          onMouseUp={handleOutputPortMouseUp}
        />
      )}
      <circle
        className={`${styles.inputPort} ${isInputPortHighlighted ? styles.nearbyTarget : ""}`}
        cx={0}
        cy={30}
        r={6}
        onMouseDown={handleInputPortMouseDown}
        onMouseUp={handleInputPortMouseUp}
        onMouseEnter={(e) => e.stopPropagation()}
        style={{ cursor: draggingWire ? "pointer" : "crosshair" }}
      />
      <circle
        className={`${styles.outputPort} ${isOutputPortHighlighted ? styles.nearbyTarget : ""}`}
        cx={NODE_WIDTH}
        cy={30}
        r={6}
        onMouseDown={handleOutputPortMouseDown}
        onMouseUp={handleOutputPortMouseUp}
        style={{ cursor: "crosshair" }}
      />

      {/* Branch output ports for control flow nodes - at bottom */}
      {branchSlots.length > 0 && (
        <g>
          {branchSlots.map((slot, index) => {
            // Spread ports horizontally along the bottom
            const slotWidth = NODE_WIDTH / branchSlots.length;
            const portX = slotWidth * index + slotWidth / 2;
            const portY = totalHeight;
            return (
              <g key={slot.name}>
                {/* Branch label above port */}
                <text
                  className={styles.branchLabel}
                  x={portX}
                  y={totalHeight - 10}
                  textAnchor="middle"
                  fill={getBranchColor(slot.name)}
                  fontSize={9}
                  fontWeight={500}
                >
                  {slot.name}
                </text>
                {/* Branch port */}
                <circle
                  className={styles.branchPort}
                  cx={portX}
                  cy={portY}
                  r={5}
                  fill={
                    slot.connected ? getBranchColor(slot.name) : "transparent"
                  }
                  stroke={getBranchColor(slot.name)}
                  strokeWidth={2}
                  onMouseDown={(e) =>
                    handleBranchPortMouseDown(e, slot.name, portX, portY)
                  }
                  style={{ cursor: "crosshair" }}
                />
              </g>
            );
          })}
        </g>
      )}

      {/* Status indicator */}
      {status !== "idle" && (
        <circle
          className={styles.statusDot}
          cx={170}
          cy={10}
          r={6}
          fill={
            status === "running"
              ? "#FACC15"
              : status === "success"
                ? "#34D399"
                : "#F87171"
          }
        />
      )}

      {/* Orphan indicator - click badge to start orphan-to-reporter drag */}
      {isOrphan && (
        <g
          className={styles.orphanBadge}
          onMouseDown={handleOrphanDragStart}
          style={{ cursor: "grab" }}
        >
          <rect x={148} y={-10} width={36} height={20} rx={4} />
          <text
            x={166}
            y={4}
            textAnchor="middle"
            className={styles.orphanBadgeText}
          >
            ◇
          </text>
          {/* Tooltip hint */}
          <title>Drag to slot as reporter</title>
        </g>
      )}

      {/* Node drag handle for free layout mode (all nodes including orphans) */}
      {layoutMode === "free" && onDrag && (
        <rect
          className={styles.nodeDragHandle}
          x={4}
          y={0}
          width={isOrphan ? 140 : 172}
          height={40}
          fill="transparent"
          onMouseDown={handleNodeDragStart}
        />
      )}
    </g>
  );
}

// Render nested reporters recursively
function renderNestedReporters(
  inputs: Array<{ key: string; value: FormattedValue }>,
  depth: number = 0,
  showLabels: boolean = true,
  parentNodeId: string,
  parentPath: string[],
  selectReporter: (reporter: SelectedReporter | null) => void,
  selectedReporter: SelectedReporter | null,
): ReactElement {
  let yOffset = 0;

  return (
    <g>
      {inputs.map(({ key, value }, index) => {
        const reporterColor = getReporterColor(value.opcode || "");
        const reporterName = formatOpcodeName(value.opcode || "");
        const width = 164 - depth * 8;
        const currentPath = [...parentPath, key];

        // Check if this reporter is selected
        const isSelected =
          selectedReporter &&
          selectedReporter.parentNodeId === parentNodeId &&
          selectedReporter.inputPath.join(".") === currentPath.join(".");

        const handleReporterClick = (e: React.MouseEvent) => {
          e.stopPropagation();
          selectReporter({
            parentNodeId,
            inputPath: currentPath,
            reporterNodeId: value.id,
            opcode: value.opcode || "",
            inputs: value.inputs || {},
          });
        };

        // Separate reporter's inputs into reporters and regular values
        const nestedReporters: Array<{ key: string; value: FormattedValue }> =
          [];
        const regularInputs: Array<{ key: string; formatted: string }> = [];

        if (value.inputs) {
          for (const [nestedKey, nestedValue] of Object.entries(value.inputs)) {
            if (nestedValue.type === "reporter" && nestedValue.opcode) {
              nestedReporters.push({ key: nestedKey, value: nestedValue });
            } else {
              const formatted = formatValueShort(nestedValue);
              if (formatted) {
                regularInputs.push({ key: nestedKey, formatted });
              }
            }
          }
        }

        // Calculate heights
        const labelHeight = showLabels ? 14 : 0;
        const headerHeight = 22;
        const regularInputsHeight = regularInputs.length * 14;
        const nestedLabelHeight =
          nestedReporters.length > 0 ? nestedReporters.length * 14 : 0;
        const nestedReportersHeight = nestedReporters.reduce(
          (acc, { value: v }) => {
            return acc + calculateReporterTotalHeight(v) + 4;
          },
          0,
        );
        const totalPillHeight =
          headerHeight +
          regularInputsHeight +
          nestedLabelHeight +
          nestedReportersHeight +
          4;

        const currentY = yOffset;
        yOffset += labelHeight + totalPillHeight + 4;

        return (
          <g key={`${key}-${index}`} transform={`translate(0, ${currentY})`}>
            {/* Input slot label on parent level */}
            {showLabels && (
              <text className={styles.reporterLabel} x={0} y={10}>
                {key}
              </text>
            )}

            {/* Reporter pill */}
            <g
              transform={`translate(0, ${labelHeight})`}
              className={`${styles.reporterClickable} ${isSelected ? styles.reporterSelected : ""}`}
              onClick={handleReporterClick}
            >
              {/* Reporter pill background */}
              <rect
                className={styles.reporterPill}
                x={0}
                y={0}
                width={width}
                height={totalPillHeight}
                rx={11}
                style={
                  { "--reporter-color": reporterColor } as React.CSSProperties
                }
              />

              {/* Color dot */}
              <circle cx={10} cy={11} r={4} fill={reporterColor} />

              {/* Reporter name */}
              <text className={styles.reporterName} x={18} y={15}>
                {reporterName}
              </text>

              {/* Regular inputs (literals, variables) - split key/value */}
              {regularInputs.map((input, i) => (
                <g key={input.key}>
                  <text
                    className={styles.reporterInputKey}
                    x={18}
                    y={headerHeight + 10 + i * 14}
                  >
                    {input.key}:
                  </text>
                  <text
                    className={styles.reporterInputValue}
                    x={18 + (input.key.length + 1) * 5}
                    y={headerHeight + 10 + i * 14}
                  >
                    {input.formatted}
                  </text>
                </g>
              ))}

              {/* Nested reporter labels and reporters */}
              {nestedReporters.length > 0 && (
                <g
                  transform={`translate(6, ${headerHeight + regularInputsHeight})`}
                >
                  {renderNestedReporterWithLabels(
                    nestedReporters,
                    depth + 1,
                    parentNodeId,
                    currentPath,
                    selectReporter,
                    selectedReporter,
                  )}
                </g>
              )}
            </g>
          </g>
        );
      })}
    </g>
  );
}

// Render nested reporters with their labels inside parent pill
function renderNestedReporterWithLabels(
  inputs: Array<{ key: string; value: FormattedValue }>,
  depth: number,
  parentNodeId: string,
  parentPath: string[],
  selectReporter: (reporter: SelectedReporter | null) => void,
  selectedReporter: SelectedReporter | null,
): ReactElement {
  let yOffset = 0;

  return (
    <g>
      {inputs.map(({ key, value }, index) => {
        const reporterColor = getReporterColor(value.opcode || "");
        const reporterName = formatOpcodeName(value.opcode || "");
        const width = 164 - depth * 8 - 6;
        const currentPath = [...parentPath, key];

        // Check if this reporter is selected
        const isSelected =
          selectedReporter &&
          selectedReporter.parentNodeId === parentNodeId &&
          selectedReporter.inputPath.join(".") === currentPath.join(".");

        const handleReporterClick = (e: React.MouseEvent) => {
          e.stopPropagation();
          selectReporter({
            parentNodeId,
            inputPath: currentPath,
            reporterNodeId: value.id,
            opcode: value.opcode || "",
            inputs: value.inputs || {},
          });
        };

        // Get nested content
        const nestedReporters: Array<{ key: string; value: FormattedValue }> =
          [];
        const regularInputs: Array<{ key: string; formatted: string }> = [];

        if (value.inputs) {
          for (const [nestedKey, nestedValue] of Object.entries(value.inputs)) {
            if (nestedValue.type === "reporter" && nestedValue.opcode) {
              nestedReporters.push({ key: nestedKey, value: nestedValue });
            } else {
              const formatted = formatValueShort(nestedValue);
              if (formatted) {
                regularInputs.push({ key: nestedKey, formatted });
              }
            }
          }
        }

        const labelHeight = 14;
        const headerHeight = 22;
        const regularInputsHeight = regularInputs.length * 14;
        const nestedLabelHeight =
          nestedReporters.length > 0 ? nestedReporters.length * 14 : 0;
        const nestedReportersHeight = nestedReporters.reduce(
          (acc, { value: v }) => {
            return acc + calculateReporterTotalHeight(v) + 4;
          },
          0,
        );
        const pillHeight =
          headerHeight +
          regularInputsHeight +
          nestedLabelHeight +
          nestedReportersHeight +
          4;

        const currentY = yOffset;
        yOffset += labelHeight + pillHeight + 4;

        return (
          <g key={`${key}-${index}`} transform={`translate(0, ${currentY})`}>
            {/* Label */}
            <text className={styles.reporterNestedLabel} x={0} y={10}>
              {key}
            </text>

            {/* Nested pill */}
            <g
              transform={`translate(0, ${labelHeight})`}
              className={`${styles.reporterClickable} ${isSelected ? styles.reporterSelected : ""}`}
              onClick={handleReporterClick}
            >
              <rect
                className={styles.reporterPill}
                x={0}
                y={0}
                width={width}
                height={pillHeight}
                rx={11}
                style={
                  { "--reporter-color": reporterColor } as React.CSSProperties
                }
              />

              <circle cx={10} cy={11} r={4} fill={reporterColor} />

              <text className={styles.reporterName} x={18} y={15}>
                {reporterName}
              </text>

              {regularInputs.map((input, i) => (
                <g key={input.key}>
                  <text
                    className={styles.reporterInputKey}
                    x={18}
                    y={headerHeight + 10 + i * 14}
                  >
                    {input.key}:
                  </text>
                  <text
                    className={styles.reporterInputValue}
                    x={18 + (input.key.length + 1) * 5}
                    y={headerHeight + 10 + i * 14}
                  >
                    {input.formatted}
                  </text>
                </g>
              ))}

              {nestedReporters.length > 0 && (
                <g
                  transform={`translate(6, ${headerHeight + regularInputsHeight})`}
                >
                  {renderNestedReporterWithLabels(
                    nestedReporters,
                    depth + 1,
                    parentNodeId,
                    currentPath,
                    selectReporter,
                    selectedReporter,
                  )}
                </g>
              )}
            </g>
          </g>
        );
      })}
    </g>
  );
}

function getReporterColor(opcode: string): string {
  return getGrammarReporterColor(opcode);
}

function formatOpcodeName(opcode: string): string {
  return opcode
    .replace(/^(control_|data_|io_|operator_|workflow_)/, "")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
