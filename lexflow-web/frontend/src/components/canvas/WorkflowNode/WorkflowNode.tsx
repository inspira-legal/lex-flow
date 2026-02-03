import { useRef, useEffect, useState, memo } from "react"
import { useWorkflowStore, useUiStore, useSelectionStore } from "@/store"
import type { NodeSlotPositions } from "@/store/uiStore"
import type { SelectedReporter } from "@/store/selectionStore"
import type { FormattedValue, BranchNode, OpcodeInterface } from "@/api/types"
import { InputSlot } from "../InputSlot"
import {
  getBranchColor,
  getBranchSlots as getGrammarBranchSlots,
  getCategoryIcon,
  getNodeColor,
} from "@/services/grammar"
import { useNodePorts } from "@/hooks"
import {
  getReporterColor as getGrammarReporterColor,
} from "@/services/grammar"
import {
  NODE_WIDTH,
  NODE_HEIGHT,
  NODE_EXPANDED_INPUT_HEIGHT,
  NODE_TYPE_ICONS,
  getCardStyle,
  getColorBarStyle,
  getIconContainerStyle,
  iconStyle,
  nameStyle,
  idStyle,
  getPortStyle,
  getStatusDotStyle,
  orphanBadgeStyle,
  orphanBadgeRectStyle,
  orphanBadgeTextStyle,
  nodeDragHandleStyle,
  getBranchPortStyle,
  branchLabelStyle,
  getReporterBadgeStyle,
  reporterBadgeTextStyle,
  getAddButtonStyle,
  addButtonTextStyle,
} from "./styles"
import type { WorkflowNodeProps } from "./types"

// Get available branch slots for a control flow opcode
function getBranchSlots(
  opcode: string,
  children: BranchNode[]
): Array<{ name: string; connected: boolean }> {
  const connectedNames = children
    .filter((c) => c.children.length > 0)
    .map((c) => c.name)
  const allBranchNames = children.map((c) => c.name)

  const slots = getGrammarBranchSlots(opcode, connectedNames)

  for (const branchName of allBranchNames) {
    if (!slots.find((s) => s.name === branchName)) {
      slots.push({ name: branchName, connected: connectedNames.includes(branchName) })
    }
  }

  return slots
}

// Get icon for node
function getNodeIcon(opcode: string, nodeType: string): string {
  const grammarIcon = getCategoryIcon(opcode)
  if (grammarIcon && grammarIcon !== "⚙") {
    return grammarIcon
  }
  return NODE_TYPE_ICONS[nodeType] || NODE_TYPE_ICONS.opcode
}

// Format opcode name for display
function formatOpcodeName(opcode: string): string {
  return opcode
    .replace(/^(control_|data_|io_|operator_|workflow_)/, "")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

// Count total reporters in inputs (including nested)
function countReporters(inputs: Record<string, FormattedValue>): number {
  let count = 0
  for (const value of Object.values(inputs)) {
    if (value.type === "reporter" && value.opcode) {
      count += 1
      if (value.inputs) {
        count += countReporters(value.inputs)
      }
    }
  }
  return count
}

// Reporter nesting constants - reporters are full-sized nodes
const REPORTER_PADDING = 12 // Padding inside parent container
const REPORTER_GAP = 8 // Gap between siblings
const REPORTER_LABEL_HEIGHT = 16 // Height for input key label
const INPUT_SLOT_HEIGHT = 28 // Height for literal/variable input slots

// UI timing constants
const HIDE_ADD_BUTTON_DELAY_MS = 2000 // Delay before hiding the add button after mouse leave

// Calculate nested reporter dimensions recursively
// expandedReporters: Record of compositeId (workflowName::nodeId) -> boolean for expansion state
function calculateReporterDimensions(
  value: FormattedValue,
  showInputSlots: boolean,
  expandedReporters: Record<string, boolean>,
  workflowName: string
): { width: number; height: number } {
  if (value.type !== "reporter" || !value.opcode) {
    return { width: 0, height: 0 }
  }

  // Check if THIS reporter is expanded using composite ID
  const compositeId = `${workflowName}::${value.id || ""}`
  const isExpanded = expandedReporters[compositeId] ?? false

  // If collapsed, just return minimum node size
  if (!isExpanded && !showInputSlots) {
    return { width: NODE_WIDTH, height: NODE_HEIGHT }
  }

  // Separate nested reporters from regular inputs
  const nestedReporters: Array<{ key: string; value: FormattedValue }> = []
  let regularInputCount = 0

  if (value.inputs) {
    for (const [key, nestedValue] of Object.entries(value.inputs)) {
      if (nestedValue.type === "reporter" && nestedValue.opcode) {
        nestedReporters.push({ key, value: nestedValue })
      } else {
        regularInputCount++
      }
    }
  }

  // Base size is minimum node size
  let contentWidth = NODE_WIDTH
  let contentHeight = NODE_HEIGHT

  // Only show content if expanded OR in drag mode
  if (isExpanded || showInputSlots) {
    // Add height for nested reporters (they stack vertically inside)
    if (nestedReporters.length > 0) {
      let childrenHeight = 0
      let maxChildWidth = 0

      for (const nested of nestedReporters) {
        const childDims = calculateReporterDimensions(nested.value, showInputSlots, expandedReporters, workflowName)
        childrenHeight += REPORTER_LABEL_HEIGHT + childDims.height + REPORTER_GAP
        maxChildWidth = Math.max(maxChildWidth, childDims.width)
      }

      contentWidth = Math.max(contentWidth, maxChildWidth + REPORTER_PADDING * 2)
      contentHeight = NODE_HEIGHT + childrenHeight
    }

    // Add height for input slots
    if (regularInputCount > 0) {
      contentHeight += regularInputCount * INPUT_SLOT_HEIGHT + REPORTER_GAP
    }

    // Add bottom padding if there's content
    if (nestedReporters.length > 0 || regularInputCount > 0) {
      contentHeight += REPORTER_PADDING
    }
  }

  return { width: contentWidth, height: contentHeight }
}

// Calculate total dimensions for all reporter inputs on a node
function calculateAllReportersHeight(
  reporterInputs: Array<{ key: string; value: FormattedValue }>,
  showInputSlots: boolean,
  expandedReporters: Record<string, boolean>,
  workflowName: string
): number {
  let totalHeight = 0
  for (const { value } of reporterInputs) {
    const dims = calculateReporterDimensions(value, showInputSlots, expandedReporters, workflowName)
    totalHeight += REPORTER_LABEL_HEIGHT + dims.height + REPORTER_GAP
  }
  return totalHeight
}

function calculateAllReportersWidth(
  reporterInputs: Array<{ key: string; value: FormattedValue }>,
  showInputSlots: boolean,
  expandedReporters: Record<string, boolean>,
  workflowName: string
): number {
  let maxWidth = NODE_WIDTH
  for (const { value } of reporterInputs) {
    const dims = calculateReporterDimensions(value, showInputSlots, expandedReporters, workflowName)
    maxWidth = Math.max(maxWidth, dims.width)
  }
  return maxWidth
}

export const WorkflowNode = memo(function WorkflowNode({
  node,
  x,
  y,
  isOrphan,
  zoom = 1,
  onDrag,
  workflowName,
}: WorkflowNodeProps) {
  const { opcodes } = useWorkflowStore()
  const {
    openNodeEditor,
    nodeStatus,
    searchResults,
    draggingWire,
    draggingOrphan,
    setDraggingOrphan,
    draggingVariable,
    layoutMode,
    setIsDraggingNode,
    registerSlotPositions,
    unregisterSlotPositions,
    showContextMenu,
    expandedReporters,
    showAddNodeMenu,
  } = useUiStore()
  const {
    selectedNodeId,
    selectNode,
    selectedNodeIds,
    toggleNodeSelection,
    clearMultiSelection,
    selectedReporter,
    selectReporter,
  } = useSelectionStore()

  const [isHovered, setIsHovered] = useState(false)
  const [isAddButtonHovered, setIsAddButtonHovered] = useState(false)
  const [showAddButton, setShowAddButton] = useState(false)
  const addButtonTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Handle add button visibility with delay
  useEffect(() => {
    if (isHovered || isAddButtonHovered) {
      // Show immediately when hovering
      if (addButtonTimeoutRef.current) {
        clearTimeout(addButtonTimeoutRef.current)
        addButtonTimeoutRef.current = null
      }
      setShowAddButton(true)
    } else {
      // Hide after delay
      addButtonTimeoutRef.current = setTimeout(() => {
        setShowAddButton(false)
      }, HIDE_ADD_BUTTON_DELAY_MS)
    }

    return () => {
      if (addButtonTimeoutRef.current) {
        clearTimeout(addButtonTimeoutRef.current)
      }
    }
  }, [isHovered, isAddButtonHovered])

  // Composite ID for UI state that needs to be unique across workflows
  const compositeId = `${workflowName}::${node.id}`

  const showReporters = expandedReporters[compositeId] ?? false

  const opcodeInfo = opcodes.find((op) => op.name === node.opcode)
  const color = getNodeColor(node.type)
  const icon = getNodeIcon(node.opcode, node.type)
  // Selection uses composite ID to avoid cross-workflow selection issues
  const isSelected = selectedNodeId === compositeId && !selectedReporter
  const isMultiSelected = selectedNodeIds.includes(compositeId)
  const isSearchMatch = searchResults.includes(node.id) // Search still uses raw ID for YAML matching
  const status = nodeStatus[node.id] || "idle" // Status comes from execution engine, uses raw ID
  const displayName = formatOpcodeName(node.opcode)

  const justDraggedRef = useRef(false)

  // Separate reporter inputs from regular inputs
  const reporterInputs: Array<{ key: string; value: FormattedValue }> = []
  const regularInputs: Array<{ key: string; value: FormattedValue }> = []

  for (const [key, value] of Object.entries(node.inputs)) {
    if (value.type === "reporter" && value.opcode) {
      reporterInputs.push({ key, value })
    } else {
      regularInputs.push({ key, value })
    }
  }

  // Count reporters for badge (including nested)
  const reporterCount = countReporters(node.inputs)

  // Check if we should show expanded input slots
  // Compare with compositeId to handle same node IDs across workflows
  const showInputSlots = !!(
    draggingVariable || (draggingOrphan && draggingOrphan.nodeId !== compositeId)
  )

  // Get input keys for slot display (only regular inputs)
  const inputKeys = regularInputs.map(r => r.key).slice(0, 4)

  // Calculate dynamic dimensions
  const branchSlots = getBranchSlots(node.opcode, node.children)
  const branchSectionHeight = branchSlots.length > 0 ? 20 : 0
  const inputSlotsHeight = showInputSlots ? inputKeys.length * NODE_EXPANDED_INPUT_HEIGHT : 0

  // Show reporters section when expanded OR when in drag mode
  const showReporterSection = showReporters || showInputSlots
  const reporterSectionHeight = showReporterSection && reporterInputs.length > 0
    ? calculateAllReportersHeight(reporterInputs, showInputSlots, expandedReporters, workflowName)
    : 0

  // Calculate width - expands to fit reporters
  const reporterSectionWidth = showReporterSection && reporterInputs.length > 0
    ? calculateAllReportersWidth(reporterInputs, showInputSlots, expandedReporters, workflowName) + REPORTER_PADDING * 2
    : 0
  const totalWidth = Math.max(NODE_WIDTH, reporterSectionWidth)
  const totalHeight = NODE_HEIGHT + inputSlotsHeight + reporterSectionHeight + branchSectionHeight

  // slotId is the same as compositeId, used for slot registry
  const slotId = compositeId

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
  } = useNodePorts({ nodeId: node.id, slotId, x, y })

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (justDraggedRef.current) {
      justDraggedRef.current = false
      return
    }

    // Ctrl/Cmd+click for multi-selection (use compositeId for unique selection)
    if (e.ctrlKey || e.metaKey) {
      toggleNodeSelection(compositeId)
      selectReporter(null)
      return
    }

    // Normal click - clear multi-selection and select single node
    clearMultiSelection()
    selectNode(compositeId)
    selectReporter(null)
    openNodeEditor()
  }

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    // If this node is part of multi-selection, keep the selection
    // Otherwise, select just this node (clears multi-selection)
    if (!selectedNodeIds.includes(compositeId)) {
      clearMultiSelection()
      selectNode(compositeId)
    }

    // Context menu uses compositeId for UI state, but also needs raw nodeId for YAML operations
    showContextMenu({
      nodeId: compositeId,
      x: e.clientX,
      y: e.clientY,
      hasReporters: reporterCount > 0,
      reportersExpanded: showReporters,
      isOrphan: isOrphan ?? false,
    })
  }

  const handleOrphanDragStart = (e: React.MouseEvent) => {
    if (!isOrphan) return
    e.stopPropagation()
    e.preventDefault()

    // Start from the diamond badge position (top-right corner of node)
    // Badge is at x=totalWidth-28, width=28, so center is at totalWidth-14
    // Badge is at y=-8, height=16, so center is at y=0
    const badgeCenterX = x + totalWidth - 14
    const badgeCenterY = y

    setDraggingOrphan({
      nodeId: compositeId,  // Use compositeId for UI state
      opcode: node.opcode,
      returnType: opcodeInfo?.return_type,
      fromX: badgeCenterX,
      fromY: badgeCenterY,
      toX: badgeCenterX,
      toY: badgeCenterY,
    })
  }

  const handleNodeDragStart = (e: React.MouseEvent) => {
    if (layoutMode !== "free" || !onDrag) return
    e.stopPropagation()
    e.preventDefault()

    setIsDraggingNode(true)

    const startX = e.clientX
    const startY = e.clientY
    let hasMoved = false

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const dx = (moveEvent.clientX - startX) / zoom
      const dy = (moveEvent.clientY - startY) / zoom
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        hasMoved = true
        onDrag(dx, dy)
      }
    }

    const handleMouseUp = () => {
      setIsDraggingNode(false)
      if (hasMoved) {
        justDraggedRef.current = true
      }
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mouseup", handleMouseUp)
    }

    window.addEventListener("mousemove", handleMouseMove)
    window.addEventListener("mouseup", handleMouseUp)
  }

  const handleAddNodeClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    showAddNodeMenu(e.clientX, e.clientY, node.id, workflowName)
  }

  // Register slot positions using composite ID (workflowName::nodeId)
  useEffect(() => {
    const positions: NodeSlotPositions = {
      input: { x, y: y + NODE_HEIGHT / 2 },
      output: { x: x + totalWidth, y: y + NODE_HEIGHT / 2 },
      branches: {},
    }

    branchSlots.forEach((slot, index) => {
      const slotWidth = totalWidth / branchSlots.length
      positions.branches[slot.name] = {
        x: x + slotWidth * index + slotWidth / 2,
        y: y + totalHeight,
      }
    })

    registerSlotPositions(slotId, positions)
    return () => unregisterSlotPositions(slotId)
  }, [x, y, totalWidth, totalHeight, branchSlots.length, slotId, registerSlotPositions, unregisterSlotPositions])

  return (
    <g
      style={{ cursor: "pointer" }}
      transform={`translate(${x}, ${y})`}
      onClick={handleClick}
      onContextMenu={handleContextMenu}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Invisible hit area extending to add button - prevents hover flicker */}
      <rect
        x={0}
        y={0}
        width={totalWidth + 30}
        height={totalHeight}
        fill="transparent"
        style={{ pointerEvents: 'all' }}
      />
      {/* Main card */}
      <rect
        width={totalWidth}
        height={totalHeight}
        rx={8}
        style={getCardStyle(color, isSelected, isSearchMatch, isOrphan ?? false, isHovered, status, showInputSlots, isMultiSelected)}
      />

      {/* Color accent bar */}
      <rect
        x={0}
        y={0}
        width={3}
        height={totalHeight}
        rx={1.5}
        style={getColorBarStyle(color)}
      />

      {/* Icon circle - centered horizontally, near top */}
      <circle
        cx={NODE_WIDTH / 2}
        cy={22}
        r={14}
        style={getIconContainerStyle(color, isHovered)}
      />
      <text x={NODE_WIDTH / 2} y={22} style={iconStyle}>
        {icon}
      </text>

      {/* Node name - centered below icon */}
      <text x={NODE_WIDTH / 2} y={46} textAnchor="middle" style={nameStyle}>
        {displayName.length > 10 ? displayName.slice(0, 10) + "…" : displayName}
      </text>

      {/* Node ID (shown on hover or selection) */}
      {(isHovered || isSelected) && (
        <text x={NODE_WIDTH / 2} y={60} textAnchor="middle" style={idStyle}>
          {node.id.length > 12 ? node.id.slice(0, 12) + "…" : node.id}
        </text>
      )}

      {/* Input slots (shown during drag operations) */}
      {showInputSlots && inputKeys.map((key, i) => (
        <InputSlot
          key={key}
          nodeId={node.id}
          inputKey={key}
          value={node.inputs[key]}
          paramInfo={opcodeInfo?.parameters.find(p => p.name.toUpperCase() === key)}
          opcode={node.opcode}
          allInputs={node.inputs}
          x={REPORTER_PADDING}
          y={NODE_HEIGHT + i * NODE_EXPANDED_INPUT_HEIGHT}
          width={totalWidth - REPORTER_PADDING * 2}
        />
      ))}

      {/* Expanded reporter chain (shown when expanded or during drag operations) */}
      {showReporterSection && reporterInputs.length > 0 && (
        <ReporterChain
          reporterInputs={reporterInputs}
          parentNodeId={node.id}
          baseY={NODE_HEIGHT + inputSlotsHeight}
          selectedReporter={selectedReporter}
          selectReporter={selectReporter}
          openNodeEditor={openNodeEditor}
          showInputSlots={showInputSlots}
          opcodes={opcodes}
          expandedReporters={expandedReporters}
          showContextMenu={showContextMenu}
          workflowName={workflowName}
        />
      )}

      {/* Reporter count badge (shown when collapsed and not in drag mode) */}
      {reporterCount > 0 && !showReporterSection && (
        <g transform={`translate(${totalWidth - 18}, 4)`}>
          <rect
            x={0}
            y={0}
            width={14}
            height={14}
            rx={7}
            style={getReporterBadgeStyle(true, false)}
          />
          <text x={7} y={7} style={reporterBadgeTextStyle}>
            {reporterCount}
          </text>
        </g>
      )}

      {/* Connection ports */}
      {isValidDropTarget && (
        <circle
          cx={0}
          cy={NODE_HEIGHT / 2}
          r={16}
          fill="transparent"
          style={{ cursor: "pointer" }}
          onMouseUp={handleInputPortMouseUp}
        />
      )}
      {isValidOutputDropTarget && (
        <circle
          cx={totalWidth}
          cy={NODE_HEIGHT / 2}
          r={16}
          fill="transparent"
          style={{ cursor: "pointer" }}
          onMouseUp={handleOutputPortMouseUp}
        />
      )}

      {/* Input port */}
      <circle
        cx={0}
        cy={NODE_HEIGHT / 2}
        r={5}
        style={getPortStyle(isHovered, isInputPortHighlighted, !!draggingWire)}
        onMouseDown={handleInputPortMouseDown}
        onMouseUp={handleInputPortMouseUp}
      />

      {/* Output port */}
      <circle
        cx={totalWidth}
        cy={NODE_HEIGHT / 2}
        r={5}
        style={getPortStyle(isHovered, isOutputPortHighlighted, !!draggingWire)}
        onMouseDown={handleOutputPortMouseDown}
        onMouseUp={handleOutputPortMouseUp}
      />

      {/* Add node button - shown on hover, not on workflow_start nodes */}
      {showAddButton && node.opcode !== "workflow_start" && (
        <g
          className="add-node-button"
          onClick={handleAddNodeClick}
          onMouseEnter={() => setIsAddButtonHovered(true)}
          onMouseLeave={() => setIsAddButtonHovered(false)}
          style={{ cursor: 'pointer' }}
        >
          <circle
            cx={totalWidth + 16}
            cy={NODE_HEIGHT / 2}
            r={10}
            style={getAddButtonStyle(isAddButtonHovered)}
          />
          <text
            x={totalWidth + 16}
            y={NODE_HEIGHT / 2}
            style={addButtonTextStyle}
          >
            +
          </text>
        </g>
      )}

      {/* Branch ports */}
      {branchSlots.length > 0 && (
        <g>
          {branchSlots.map((slot, index) => {
            const slotWidth = totalWidth / branchSlots.length
            const portX = slotWidth * index + slotWidth / 2
            const portY = totalHeight
            const branchColor = getBranchColor(slot.name)

            return (
              <g key={slot.name}>
                <text
                  x={portX}
                  y={totalHeight - 8}
                  fill={branchColor}
                  style={branchLabelStyle}
                >
                  {slot.name}
                </text>
                <circle
                  cx={portX}
                  cy={portY}
                  r={4}
                  style={getBranchPortStyle(slot.connected, branchColor)}
                  onMouseDown={(e) => handleBranchPortMouseDown(e, slot.name, portX, portY)}
                />
              </g>
            )
          })}
        </g>
      )}

      {/* Status indicator */}
      {status !== "idle" && (
        <circle
          cx={totalWidth - 8}
          cy={12}
          r={4}
          style={getStatusDotStyle(status)}
        />
      )}

      {/* Orphan badge */}
      {isOrphan && (
        <g style={orphanBadgeStyle} onMouseDown={handleOrphanDragStart}>
          <rect
            x={totalWidth - 28}
            y={-8}
            width={28}
            height={16}
            rx={3}
            style={orphanBadgeRectStyle}
          />
          <text x={totalWidth - 14} y={0} style={orphanBadgeTextStyle}>
            ◇
          </text>
          <title>Drag to slot as reporter</title>
        </g>
      )}

      {/* Drag handle for free layout */}
      {layoutMode === "free" && onDrag && (
        <rect
          x={4}
          y={0}
          width={isOrphan ? totalWidth - 32 : totalWidth - 8}
          height={NODE_HEIGHT}
          style={nodeDragHandleStyle}
          onMouseDown={handleNodeDragStart}
        />
      )}
    </g>
  )
})

// Full-node reporter component - looks identical to root nodes
interface FullNodeReporterProps {
  inputKey: string
  value: FormattedValue
  parentNodeId: string
  x: number
  y: number
  selectedReporter: SelectedReporter | null
  selectReporter: (reporter: SelectedReporter | null) => void
  openNodeEditor: () => void
  showInputSlots: boolean
  opcodes: OpcodeInterface[]
  inputPath: string[]
  expandedReporters: Record<string, boolean>
  showContextMenu: (data: {
    nodeId: string
    x: number
    y: number
    hasReporters: boolean
    reportersExpanded: boolean
    isOrphan: boolean
  }) => void
  workflowName: string
}

function FullNodeReporter({
  inputKey,
  value,
  parentNodeId,
  x,
  y,
  selectedReporter,
  selectReporter,
  openNodeEditor,
  showInputSlots,
  opcodes,
  inputPath,
  expandedReporters,
  showContextMenu,
  workflowName,
}: FullNodeReporterProps) {
  const reporterColor = getGrammarReporterColor(value.opcode || "")
  const reporterName = formatOpcodeName(value.opcode || "")
  const icon = getCategoryIcon(value.opcode || "") || "⚙"
  const currentPath = [...inputPath, inputKey]
  const reporterOpcodeInfo = opcodes.find((op) => op.name === value.opcode)
  const reporterId = value.id || ""

  // Check if THIS reporter is expanded using composite ID
  const compositeReporterId = `${workflowName}::${reporterId}`
  const isExpanded = expandedReporters[compositeReporterId] ?? false

  const isSelected =
    selectedReporter &&
    selectedReporter.parentNodeId === parentNodeId &&
    selectedReporter.inputPath.join(".") === currentPath.join(".")

  // Separate nested reporters from regular inputs
  const nestedReporters: Array<{ key: string; value: FormattedValue }> = []
  const regularInputs: Array<{ key: string; value: FormattedValue }> = []
  if (value.inputs) {
    for (const [nestedKey, nestedValue] of Object.entries(value.inputs)) {
      if (nestedValue.type === "reporter" && nestedValue.opcode) {
        nestedReporters.push({ key: nestedKey, value: nestedValue })
      } else {
        regularInputs.push({ key: nestedKey, value: nestedValue })
      }
    }
  }

  // Count nested reporters for badge
  const reporterCount = countReporters(value.inputs || {})

  // Should show content (expanded or in drag mode)
  const shouldShowContent = isExpanded || showInputSlots

  // Calculate dimensions
  const dims = calculateReporterDimensions(value, showInputSlots, expandedReporters, workflowName)
  const nodeWidth = dims.width
  const nodeHeight = dims.height

  // Pre-calculate all Y positions for nested reporters (only if showing content)
  const nestedPositions: Array<{ key: string; value: FormattedValue; y: number; height: number }> = []
  let currentY = NODE_HEIGHT
  if (shouldShowContent) {
    for (const nested of nestedReporters) {
      const nestedDims = calculateReporterDimensions(nested.value, showInputSlots, expandedReporters, workflowName)
      nestedPositions.push({ key: nested.key, value: nested.value, y: currentY, height: nestedDims.height })
      currentY += REPORTER_LABEL_HEIGHT + nestedDims.height + REPORTER_GAP
    }
  }

  // Calculate Y position where input slots start
  const inputSlotsStartY = currentY

  // Context menu handler
  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    selectReporter({
      parentNodeId,
      inputPath: currentPath,
      reporterNodeId: value.id,
      opcode: value.opcode || "",
      inputs: value.inputs || {},
    })
    showContextMenu({
      nodeId: reporterId,
      x: e.clientX,
      y: e.clientY,
      hasReporters: reporterCount > 0,
      reportersExpanded: isExpanded,
      isOrphan: false,
    })
  }

  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Main reporter card - same style as root nodes */}
      <rect
        x={0}
        y={0}
        width={nodeWidth}
        height={nodeHeight}
        rx={8}
        fill="var(--color-surface-1)"
        stroke={isSelected ? "var(--color-accent-blue)" : reporterColor}
        strokeWidth={isSelected ? 2 : 1.5}
        style={{ cursor: "pointer" }}
        onClick={(e) => {
          e.stopPropagation()
          selectReporter({
            parentNodeId,
            inputPath: currentPath,
            reporterNodeId: value.id,
            opcode: value.opcode || "",
            inputs: value.inputs || {},
          })
          openNodeEditor()
        }}
        onContextMenu={handleContextMenu}
      />

      {/* Color accent bar */}
      <rect
        x={0}
        y={0}
        width={4}
        height={nodeHeight}
        rx={2}
        fill={reporterColor}
        style={{ pointerEvents: "none" }}
      />

      {/* Icon circle - centered horizontally in the header area */}
      <circle
        cx={NODE_WIDTH / 2}
        cy={22}
        r={14}
        fill={`${reporterColor}30`}
        style={{ pointerEvents: "none" }}
      />
      <text
        x={NODE_WIDTH / 2}
        y={22}
        textAnchor="middle"
        dominantBaseline="central"
        style={{ fontSize: "14px", fill: "var(--color-text-primary)", pointerEvents: "none" }}
      >
        {icon}
      </text>

      {/* Reporter name - centered below icon */}
      <text
        x={NODE_WIDTH / 2}
        y={46}
        textAnchor="middle"
        style={{ fontSize: "11px", fontWeight: 600, fill: "var(--color-text-primary)", pointerEvents: "none" }}
      >
        {reporterName.length > 10 ? reporterName.slice(0, 10) + "…" : reporterName}
      </text>

      {/* Reporter count badge (shown when collapsed) */}
      {reporterCount > 0 && !shouldShowContent && (
        <g transform={`translate(${NODE_WIDTH - 18}, 4)`}>
          <rect
            x={0}
            y={0}
            width={14}
            height={14}
            rx={7}
            style={getReporterBadgeStyle(true, false)}
          />
          <text x={7} y={7} style={reporterBadgeTextStyle}>
            {reporterCount}
          </text>
        </g>
      )}

      {/* Nested reporters (full nodes inside) - only when expanded or dragging */}
      {shouldShowContent && nestedPositions.map((nested) => (
        <g key={nested.key}>
          {/* Input key label */}
          <text
            x={REPORTER_PADDING}
            y={nested.y + 10}
            style={{ fontSize: "10px", fontWeight: 500, fill: "var(--color-text-muted)" }}
          >
            {nested.key}
          </text>

          {/* Nested reporter as full node */}
          <FullNodeReporter
            inputKey={nested.key}
            value={nested.value}
            parentNodeId={parentNodeId}
            x={REPORTER_PADDING}
            y={nested.y + REPORTER_LABEL_HEIGHT}
            selectedReporter={selectedReporter}
            selectReporter={selectReporter}
            openNodeEditor={openNodeEditor}
            showInputSlots={showInputSlots}
            opcodes={opcodes}
            inputPath={currentPath}
            expandedReporters={expandedReporters}
            showContextMenu={showContextMenu}
            workflowName={workflowName}
          />
        </g>
      ))}

      {/* Input slots for literals/variables - only when expanded or dragging */}
      {shouldShowContent && regularInputs.map((input, i) => (
        <g key={input.key} transform={`translate(${REPORTER_PADDING}, ${inputSlotsStartY + i * INPUT_SLOT_HEIGHT})`}>
          {/* Input key label */}
          <text
            x={0}
            y={10}
            style={{ fontSize: "10px", fontWeight: 500, fill: "var(--color-text-muted)" }}
          >
            {input.key}
          </text>

          {/* Input slot pill */}
          <InputSlot
            nodeId={value.id || parentNodeId}
            inputKey={input.key}
            value={input.value}
            paramInfo={reporterOpcodeInfo?.parameters.find(p => p.name.toUpperCase() === input.key)}
            opcode={value.opcode || ""}
            allInputs={value.inputs || {}}
            x={0}
            y={12}
            width={nodeWidth - REPORTER_PADDING * 2}
          />
        </g>
      ))}
    </g>
  )
}

// Top-level reporter chain (renders all reporter inputs as full nodes)
interface ReporterChainProps {
  reporterInputs: Array<{ key: string; value: FormattedValue }>
  parentNodeId: string
  baseY: number
  selectedReporter: SelectedReporter | null
  selectReporter: (reporter: SelectedReporter | null) => void
  openNodeEditor: () => void
  showInputSlots: boolean
  opcodes: OpcodeInterface[]
  expandedReporters: Record<string, boolean>
  showContextMenu: (data: {
    nodeId: string
    x: number
    y: number
    hasReporters: boolean
    reportersExpanded: boolean
    isOrphan: boolean
  }) => void
  workflowName: string
}

function ReporterChain({
  reporterInputs,
  parentNodeId,
  baseY,
  selectedReporter,
  selectReporter,
  openNodeEditor,
  showInputSlots,
  opcodes,
  expandedReporters,
  showContextMenu,
  workflowName,
}: ReporterChainProps) {
  // Pre-calculate all Y positions
  const positions: Array<{ key: string; value: FormattedValue; y: number }> = []
  let yOffset = 0
  for (const { key, value } of reporterInputs) {
    positions.push({ key, value, y: yOffset })
    const dims = calculateReporterDimensions(value, showInputSlots, expandedReporters, workflowName)
    yOffset += REPORTER_LABEL_HEIGHT + dims.height + REPORTER_GAP
  }

  return (
    <g transform={`translate(${REPORTER_PADDING}, ${baseY})`}>
      {positions.map(({ key, value, y: currentY }) => (
        <g key={key}>
          {/* Input key label above reporter */}
          <text
            x={0}
            y={currentY + 10}
            style={{ fontSize: "10px", fontWeight: 500, fill: "var(--color-text-muted)" }}
          >
            {key}
          </text>

          {/* Full node reporter */}
          <FullNodeReporter
            inputKey={key}
            value={value}
            parentNodeId={parentNodeId}
            x={0}
            y={currentY + REPORTER_LABEL_HEIGHT}
            selectedReporter={selectedReporter}
            selectReporter={selectReporter}
            openNodeEditor={openNodeEditor}
            showInputSlots={showInputSlots}
            opcodes={opcodes}
            inputPath={[]}
            expandedReporters={expandedReporters}
            showContextMenu={showContextMenu}
            workflowName={workflowName}
          />
        </g>
      ))}
    </g>
  )
}
