import { useRef, useEffect, useState, memo } from "react"
import { useUiStore, useSelectionStore } from "@/store"
import type { NodeSlotPositions } from "@/store/uiStore"
import {
  START_NODE_WIDTH,
  START_NODE_HEIGHT,
  getCardStyle,
  colorBarStyle,
  flagIconStyle,
  nameStyle,
  interfaceLabelStyle,
  variableStyle,
  moreVarsStyle,
  getOutputPortStyle,
  dragHandleStyle,
} from "./styles"
import type { StartNodeProps } from "./types"

export const StartNode = memo(function StartNode({
  workflowName,
  workflowInterface,
  variables,
  x,
  y,
  zoom = 1,
  onDrag,
}: StartNodeProps) {
  const {
    openNodeEditor,
    layoutMode,
    setIsDraggingNode,
    registerSlotPositions,
    unregisterSlotPositions,
  } = useUiStore()
  const { selectedStartNode, selectStartNode, selectNode } = useSelectionStore()

  const [isHovered, setIsHovered] = useState(false)

  // Start node ID for the slot registry
  const startNodeId = `start-${workflowName}`

  const isSelected = selectedStartNode === workflowName
  const justDraggedRef = useRef(false)

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (justDraggedRef.current) {
      justDraggedRef.current = false
      return
    }
    selectNode(null) // Deselect any regular node
    selectStartNode(workflowName)
    openNodeEditor()
  }

  // Handle node drag in free layout mode
  const handleDragStart = (e: React.MouseEvent) => {
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

  // Format variables for display
  const varEntries = Object.entries(variables).slice(0, 3)
  const hasMoreVars = Object.keys(variables).length > 3

  // Format interface inputs/outputs
  const inputs = workflowInterface.inputs || []
  const outputs = workflowInterface.outputs || []

  // Calculate dynamic height based on content
  const baseHeight = 50 // Header + padding
  const interfaceHeight = inputs.length > 0 || outputs.length > 0 ? 18 : 0
  const variablesHeight = varEntries.length * 14 + (hasMoreVars ? 12 : 0)
  const totalHeight = Math.max(
    START_NODE_HEIGHT,
    baseHeight + interfaceHeight + variablesHeight + 10
  )

  // Register slot positions for wire alignment (start node only has output port)
  useEffect(() => {
    const positions: NodeSlotPositions = {
      input: { x, y: y + 30 }, // Not used but required by interface
      output: { x: x + START_NODE_WIDTH, y: y + 30 },
      branches: {},
    }

    registerSlotPositions(startNodeId, positions)
    return () => unregisterSlotPositions(startNodeId)
  }, [x, y, startNodeId, registerSlotPositions, unregisterSlotPositions])

  return (
    <g
      style={{ cursor: "pointer" }}
      transform={`translate(${x}, ${y})`}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Node card */}
      <rect
        width={START_NODE_WIDTH}
        height={totalHeight}
        rx={8}
        style={getCardStyle(isSelected, isHovered)}
      />

      {/* Green color bar on left */}
      <rect width={4} height={totalHeight} rx={2} style={colorBarStyle} />

      {/* Green flag icon */}
      <text x={16} y={24} style={flagIconStyle}>
        🚩
      </text>

      {/* Workflow name */}
      <text x={38} y={24} style={nameStyle}>
        {workflowName}
      </text>

      {/* Interface info */}
      {(inputs.length > 0 || outputs.length > 0) && (
        <g transform="translate(12, 38)">
          <text x={0} y={0} style={interfaceLabelStyle}>
            {inputs.length > 0 && `In: ${inputs.join(", ")}`}
            {inputs.length > 0 && outputs.length > 0 && " | "}
            {outputs.length > 0 && `Out: ${outputs.join(", ")}`}
          </text>
        </g>
      )}

      {/* Variables section */}
      {varEntries.length > 0 && (
        <g transform={`translate(12, ${baseHeight + interfaceHeight - 4})`}>
          {varEntries.map(([name, value], i) => (
            <text key={name} x={0} y={i * 14 + 10} style={variableStyle}>
              ${name} = {formatVariableValue(value)}
            </text>
          ))}
          {hasMoreVars && (
            <text x={0} y={varEntries.length * 14 + 10} style={moreVarsStyle}>
              +{Object.keys(variables).length - 3} more...
            </text>
          )}
        </g>
      )}

      {/* Output port (connects to first real node) */}
      <circle
        cx={START_NODE_WIDTH}
        cy={30}
        r={6}
        style={getOutputPortStyle(isHovered)}
      />

      {/* Drag handle for free layout mode */}
      {layoutMode === "free" && onDrag && (
        <rect
          x={4}
          y={0}
          width={START_NODE_WIDTH - 8}
          height={40}
          fill="transparent"
          style={dragHandleStyle}
          onMouseDown={handleDragStart}
        />
      )}
    </g>
  )
})

function formatVariableValue(value: unknown): string {
  if (value === null) return "null"
  if (value === undefined) return "undefined"
  if (typeof value === "string") {
    if (value.length > 12) return `"${value.slice(0, 12)}..."`
    return `"${value}"`
  }
  if (typeof value === "object") {
    return JSON.stringify(value).slice(0, 15) + "..."
  }
  return String(value)
}
