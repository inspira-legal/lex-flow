import { useUiStore, useWorkflowStore } from "@/store"
import { checkTypeCompatibility, getCompatibilityColor } from "@/utils/typeCompatibility"
import { getInputDisplayName } from "@/utils/workflowUtils"
import {
  inputSlotStyle,
  getSlotBgStyle,
  inputKeyStyle,
  inputValueStyle,
  typeHintStyle,
} from "./styles"
import type { InputSlotProps } from "./types"
import type { FormattedValue } from "@/api/types"

export function InputSlot({
  nodeId,
  inputKey,
  value,
  paramInfo,
  opcode,
  allInputs,
  x,
  y,
  width,
}: InputSlotProps) {
  const { draggingOrphan, setDraggingOrphan, draggingVariable, setDraggingVariable } =
    useUiStore()
  const { convertOrphanToReporter, updateNodeInput, tree } = useWorkflowStore()

  // Format the display value
  const displayValue = formatValueShort(value)

  // Get friendly display name for workflow_call inputs
  const displayKey = getInputDisplayName(inputKey, opcode, tree, allInputs)

  // Check if we're a valid drop target for either orphan or variable
  const isOrphanDropTarget = draggingOrphan !== null
  const isVariableDropTarget = draggingVariable !== null
  const isDropTarget = isOrphanDropTarget || isVariableDropTarget

  // Calculate type compatibility if dragging orphan (variables are untyped, so neutral)
  const compatibility = isOrphanDropTarget
    ? checkTypeCompatibility(draggingOrphan.returnType, paramInfo?.type)
    : isVariableDropTarget
      ? null // Neutral for variables (no type checking)
      : null

  const handleMouseUp = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (draggingOrphan) {
      // Type compatibility check (confirm dialog if incompatible)
      if (compatibility === false) {
        const orphanNodeId = draggingOrphan.nodeId
        useUiStore.getState().showConfirmDialog({
          title: "Type Mismatch",
          message: `The orphan node's return type may not be compatible with the input "${inputKey}". Continue anyway?`,
          confirmLabel: "Continue",
          variant: "default",
          onConfirm: () => {
            convertOrphanToReporter(orphanNodeId, nodeId, inputKey)
            setDraggingOrphan(null)
          },
          onCancel: () => {
            setDraggingOrphan(null)
          },
        })
        return
      }
      // Convert the orphan to a reporter for this input
      convertOrphanToReporter(draggingOrphan.nodeId, nodeId, inputKey)
      setDraggingOrphan(null)
    } else if (draggingVariable) {
      // Update the input to use the variable reference
      updateNodeInput(nodeId, inputKey, `$${draggingVariable.name}`)
      setDraggingVariable(null)
    }
  }

  const handleMouseEnter = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  // Use green color for variable drops
  const slotColor = isVariableDropTarget ? "#22C55E" : getCompatibilityColor(compatibility)

  const slotHeight = 20

  return (
    <g
      style={inputSlotStyle}
      transform={`translate(${x}, ${y})`}
      onMouseUp={handleMouseUp}
      onMouseEnter={handleMouseEnter}
    >
      {/* Background rect for drop target */}
      <rect
        x={0}
        y={0}
        width={width}
        height={slotHeight}
        rx={3}
        style={getSlotBgStyle(isDropTarget, compatibility, slotColor)}
      />

      {/* Key label */}
      <text x={6} y={13} style={inputKeyStyle}>
        {displayKey}:
      </text>

      {/* Value */}
      <text x={6 + (displayKey.length + 1) * 5} y={13} style={inputValueStyle}>
        {displayValue}
      </text>

      {/* Type hint when dragging */}
      {isDropTarget && paramInfo?.type && (
        <text x={width - 6} y={13} textAnchor="end" style={typeHintStyle}>
          {paramInfo.type}
        </text>
      )}
    </g>
  )
}

function formatValueShort(value: FormattedValue): string {
  switch (value.type) {
    case "literal": {
      const v = value.value
      if (typeof v === "string") {
        return `"${v.length > 10 ? v.slice(0, 10) + "..." : v}"`
      }
      if (typeof v === "object" && v !== null) {
        // Format arrays/objects compactly
        const json = JSON.stringify(v)
        return json.length > 20 ? json.slice(0, 17) + "..." : json
      }
      return String(v)
    }
    case "variable":
      return `$${value.name}`
    case "reporter":
      return `[reporter]`
    case "workflow_call":
      return `-> ${value.name}`
    default:
      return ""
  }
}
