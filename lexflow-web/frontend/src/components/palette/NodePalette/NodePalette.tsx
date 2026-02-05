import { useState, useMemo, useRef } from "react"
import { useWorkflowStore, useUiStore } from "@/store"
import type { OpcodeInterface } from "@/api/types"
import { getCallableWorkflows } from "@/utils/workflowUtils"
import { getCategories } from "@/services/grammar"
import { cn } from "@/lib/cn"
import {
  paletteVariants,
  headerVariants,
  headerTitleVariants,
  closeBtnVariants,
  searchVariants,
  searchInputVariants,
  contentVariants,
  searchResultsVariants,
  noResultsVariants,
  categoryVariants,
  categoryHeaderVariants,
  categoryIconVariants,
  categoryLabelVariants,
  categoryCountVariants,
  expandIconVariants,
  categoryItemsVariants,
  opcodeItemVariants,
  opcodeHeaderVariants,
  opcodeNameVariants,
  opcodeRawVariants,
  opcodeDetailsVariants,
  opcodeDescVariants,
  opcodeParamsVariants,
  paramsLabelVariants,
  paramVariants,
  paramTypeVariants,
  variableItemVariants,
  variableNameVariants,
  variableValueVariants,
  variableWorkflowVariants,
  emptyVariablesVariants,
  workflowItemVariants,
  workflowHeaderVariants,
  workflowNameVariants,
  workflowParamsVariants,
  workflowDetailsVariants,
  workflowParamListVariants,
  workflowParamVariants,
  workflowNoParamsVariants,
  goToDefinitionBtnVariants,
  footerVariants,
  hintVariants,
} from "./styles"
import type { NodePaletteProps } from "./types"

export function NodePalette({ className }: NodePaletteProps) {
  const { opcodes, tree } = useWorkflowStore()
  const { togglePalette, setDraggingVariable, setDraggingWorkflowCall } =
    useUiStore()
  const [search, setSearch] = useState("")
  const [expandedCategory, setExpandedCategory] = useState<string | null>(
    "variables"
  )

  const CATEGORIES = getCategories()

  const callableWorkflows = useMemo(
    () => getCallableWorkflows(tree),
    [tree]
  )

  const allVariables = useMemo(() => {
    if (!tree) return []
    const vars: Array<{ name: string; value: unknown; workflowName: string }> =
      []
    for (const workflow of tree.workflows) {
      for (const [name, value] of Object.entries(workflow.variables)) {
        vars.push({ name, value, workflowName: workflow.name })
      }
    }
    return vars
  }, [tree])

  const grouped = useMemo(() => {
    const groups: Record<string, OpcodeInterface[]> = {}
    for (const cat of CATEGORIES) {
      groups[cat.id] = []
    }
    groups["other"] = []

    for (const opcode of opcodes) {
      // Use explicit category from API if available
      if (opcode.category && groups[opcode.category]) {
        groups[opcode.category].push(opcode)
      } else {
        groups["other"].push(opcode)
      }
    }

    return groups
  }, [opcodes, CATEGORIES])

  const filteredOpcodes = useMemo(() => {
    if (!search) return null
    const lower = search.toLowerCase()
    return opcodes.filter(
      (op) =>
        op.name.toLowerCase().includes(lower) ||
        (op.description?.toLowerCase().includes(lower) ?? false)
    )
  }, [opcodes, search])

  return (
    <div className={cn(paletteVariants(), className)}>
      <div className={headerVariants()}>
        <h2 className={headerTitleVariants()}>Node Palette</h2>
        <button className={closeBtnVariants()} onClick={togglePalette}>
          ✕
        </button>
      </div>

      <div className={searchVariants()}>
        <input
          type="text"
          placeholder="Search nodes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className={searchInputVariants()}
        />
      </div>

      <div className={contentVariants()}>
        {filteredOpcodes ? (
          <div className={searchResultsVariants()}>
            {filteredOpcodes.length === 0 ? (
              <p className={noResultsVariants()}>No nodes found</p>
            ) : (
              filteredOpcodes.map((opcode) => (
                <OpcodeItem key={opcode.name} opcode={opcode} />
              ))
            )}
          </div>
        ) : (
          <>
            <div className={categoryVariants()}>
              <button
                className={categoryHeaderVariants()}
                onClick={() =>
                  setExpandedCategory(
                    expandedCategory === "variables" ? null : "variables"
                  )
                }
                style={{ "--cat-color": "#22C55E" } as React.CSSProperties}
              >
                <span className={categoryIconVariants()}>$</span>
                <span className={categoryLabelVariants()}>Variables</span>
                <span className={categoryCountVariants()}>
                  {allVariables.length}
                </span>
                <span className={expandIconVariants()}>
                  {expandedCategory === "variables" ? "▼" : "▶"}
                </span>
              </button>

              {expandedCategory === "variables" && (
                <div className={categoryItemsVariants()}>
                  {allVariables.length === 0 ? (
                    <div className={emptyVariablesVariants()}>
                      No variables defined. Add variables in the Start Node
                      editor.
                    </div>
                  ) : (
                    allVariables.map((v) => (
                      <VariableItem
                        key={`${v.workflowName}-${v.name}`}
                        name={v.name}
                        value={v.value}
                        workflowName={v.workflowName}
                        onDragStart={setDraggingVariable}
                        onDragEnd={() => setDraggingVariable(null)}
                      />
                    ))
                  )}
                </div>
              )}
            </div>

            {callableWorkflows.length > 0 && (
              <div className={categoryVariants()}>
                <button
                  className={categoryHeaderVariants()}
                  onClick={() =>
                    setExpandedCategory(
                      expandedCategory === "workflows" ? null : "workflows"
                    )
                  }
                  style={{ "--cat-color": "#E91E63" } as React.CSSProperties}
                >
                  <span className={categoryIconVariants()}>fn</span>
                  <span className={categoryLabelVariants()}>Workflows</span>
                  <span className={categoryCountVariants()}>
                    {callableWorkflows.length}
                  </span>
                  <span className={expandIconVariants()}>
                    {expandedCategory === "workflows" ? "▼" : "▶"}
                  </span>
                </button>

                {expandedCategory === "workflows" && (
                  <div className={categoryItemsVariants()}>
                    {callableWorkflows.map((wf) => (
                      <WorkflowCallItem
                        key={wf.name}
                        name={wf.name}
                        params={wf.params}
                        onDragStart={setDraggingWorkflowCall}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {CATEGORIES.map((cat) => (
              <div key={cat.id} className={categoryVariants()}>
                <button
                  className={categoryHeaderVariants()}
                  onClick={() =>
                    setExpandedCategory(
                      expandedCategory === cat.id ? null : cat.id
                    )
                  }
                  style={{ "--cat-color": cat.color } as React.CSSProperties}
                >
                  <span className={categoryIconVariants()}>{cat.icon}</span>
                  <span className={categoryLabelVariants()}>{cat.label}</span>
                  <span className={categoryCountVariants()}>
                    {grouped[cat.id].length}
                  </span>
                  <span className={expandIconVariants()}>
                    {expandedCategory === cat.id ? "▼" : "▶"}
                  </span>
                </button>

                {expandedCategory === cat.id && (
                  <div className={categoryItemsVariants()}>
                    {grouped[cat.id].map((opcode) => (
                      <OpcodeItem key={opcode.name} opcode={opcode} />
                    ))}
                  </div>
                )}
              </div>
            ))}

            {grouped["other"].length > 0 && (
              <div className={categoryVariants()}>
                <button
                  className={categoryHeaderVariants()}
                  onClick={() =>
                    setExpandedCategory(
                      expandedCategory === "other" ? null : "other"
                    )
                  }
                  style={{ "--cat-color": "#64748B" } as React.CSSProperties}
                >
                  <span className={categoryIconVariants()}>⚙</span>
                  <span className={categoryLabelVariants()}>Other</span>
                  <span className={categoryCountVariants()}>
                    {grouped["other"].length}
                  </span>
                  <span className={expandIconVariants()}>
                    {expandedCategory === "other" ? "▼" : "▶"}
                  </span>
                </button>

                {expandedCategory === "other" && (
                  <div className={categoryItemsVariants()}>
                    {grouped["other"].map((opcode) => (
                      <OpcodeItem key={opcode.name} opcode={opcode} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      <div className={footerVariants()}>
        <p className={hintVariants()}>
          Click to view details • Drag to canvas to add node
        </p>
      </div>
    </div>
  )
}

function OpcodeItem({ opcode }: { opcode: OpcodeInterface }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const { setDraggingOpcode, togglePalette } = useUiStore()
  const isDraggingRef = useRef(false)
  const startPosRef = useRef({ x: 0, y: 0 })

  const displayName = opcode.name
    .replace(
      /^(control_|data_|io_|operator_|list_|dict_|string_|math_|workflow_|async_|pubsub_)/,
      ""
    )
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ")

  const handleMouseDown = (e: React.MouseEvent) => {
    startPosRef.current = { x: e.clientX, y: e.clientY }
    isDraggingRef.current = false

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const dx = Math.abs(moveEvent.clientX - startPosRef.current.x)
      const dy = Math.abs(moveEvent.clientY - startPosRef.current.y)

      if (!isDraggingRef.current && (dx > 5 || dy > 5)) {
        isDraggingRef.current = true
        setDraggingOpcode(opcode)
        togglePalette()
      }
    }

    const handleMouseUp = () => {
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mouseup", handleMouseUp)
    }

    window.addEventListener("mousemove", handleMouseMove)
    window.addEventListener("mouseup", handleMouseUp)
  }

  return (
    <div className={opcodeItemVariants()}>
      <button
        className={opcodeHeaderVariants()}
        onMouseDown={handleMouseDown}
        onClick={() => {
          if (!isDraggingRef.current) {
            setIsExpanded(!isExpanded)
          }
        }}
      >
        <span className={opcodeNameVariants()}>{displayName}</span>
        <span className={opcodeRawVariants()}>{opcode.name}</span>
      </button>

      {isExpanded && (
        <div className={opcodeDetailsVariants()}>
          {opcode.description && (
            <p className={opcodeDescVariants()}>{opcode.description}</p>
          )}
          {opcode.parameters.length > 0 && (
            <div className={opcodeParamsVariants()}>
              <span className={paramsLabelVariants()}>Parameters:</span>
              {opcode.parameters.map((param) => (
                <span key={param.name} className={paramVariants()}>
                  {param.name}
                  {!param.required && "?"}
                  <span className={paramTypeVariants()}>: {param.type}</span>
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

interface VariableItemProps {
  name: string
  value: unknown
  workflowName: string
  onDragStart: (v: {
    name: string
    workflowName: string
    fromX: number
    fromY: number
    toX: number
    toY: number
  }) => void
  onDragEnd: () => void
}

function VariableItem({
  name,
  value,
  workflowName,
  onDragStart,
  onDragEnd,
}: VariableItemProps) {
  const { togglePalette } = useUiStore()
  const isDraggingRef = useRef(false)
  const startPosRef = useRef({ x: 0, y: 0 })

  const displayValue = formatVariableValue(value)

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    startPosRef.current = { x: e.clientX, y: e.clientY }
    isDraggingRef.current = false

    const handleMouseMove = (moveEvent: MouseEvent) => {
      moveEvent.preventDefault()
      const dx = Math.abs(moveEvent.clientX - startPosRef.current.x)
      const dy = Math.abs(moveEvent.clientY - startPosRef.current.y)

      if (!isDraggingRef.current && (dx > 5 || dy > 5)) {
        isDraggingRef.current = true
        onDragStart({
          name,
          workflowName,
          fromX: 0,
          fromY: 0,
          toX: 0,
          toY: 0,
        })
        togglePalette()
      }
    }

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        onDragEnd()
      }
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mouseup", handleMouseUp)
    }

    window.addEventListener("mousemove", handleMouseMove)
    window.addEventListener("mouseup", handleMouseUp)
  }

  return (
    <div
      className={variableItemVariants()}
      onMouseDown={handleMouseDown}
    >
      <span className={variableNameVariants()}>${name}</span>
      <span className={variableValueVariants()}>{displayValue}</span>
      {workflowName !== "main" && (
        <span className={variableWorkflowVariants()}>({workflowName})</span>
      )}
    </div>
  )
}

function formatVariableValue(value: unknown): string {
  if (value === null) return "null"
  if (value === undefined) return "undefined"
  if (typeof value === "string") {
    if (value.length > 15) return `"${value.slice(0, 15)}..."`
    return `"${value}"`
  }
  if (typeof value === "object") {
    const str = JSON.stringify(value)
    if (str.length > 15) return str.slice(0, 15) + "..."
    return str
  }
  return String(value)
}

interface WorkflowCallItemProps {
  name: string
  params: string[]
  onDragStart: (wc: { workflowName: string; params: string[] }) => void
}

function WorkflowCallItem({
  name,
  params,
  onDragStart,
}: WorkflowCallItemProps) {
  const { togglePalette } = useUiStore()
  const [isExpanded, setIsExpanded] = useState(false)
  const isDraggingRef = useRef(false)
  const startPosRef = useRef({ x: 0, y: 0 })

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    startPosRef.current = { x: e.clientX, y: e.clientY }
    isDraggingRef.current = false

    const handleMouseMove = (moveEvent: MouseEvent) => {
      moveEvent.preventDefault()
      const dx = Math.abs(moveEvent.clientX - startPosRef.current.x)
      const dy = Math.abs(moveEvent.clientY - startPosRef.current.y)

      if (!isDraggingRef.current && (dx > 5 || dy > 5)) {
        isDraggingRef.current = true
        onDragStart({ workflowName: name, params })
        togglePalette()
      }
    }

    const handleMouseUp = () => {
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mouseup", handleMouseUp)
    }

    window.addEventListener("mousemove", handleMouseMove)
    window.addEventListener("mouseup", handleMouseUp)
  }

  const handleGoToDefinition = (e: React.MouseEvent) => {
    e.stopPropagation()
    window.dispatchEvent(
      new CustomEvent("lexflow:goto-workflow", { detail: { workflowName: name } })
    )
    togglePalette()
  }

  return (
    <div className={workflowItemVariants()}>
      <button
        className={workflowHeaderVariants()}
        onMouseDown={handleMouseDown}
        onClick={() => {
          if (!isDraggingRef.current) {
            setIsExpanded(!isExpanded)
          }
        }}
      >
        <span className={workflowNameVariants()}>{name}</span>
        <span className={workflowParamsVariants()}>
          {params.length === 0 ? "(no params)" : `(${params.length} params)`}
        </span>
      </button>

      {isExpanded && (
        <div className={workflowDetailsVariants()}>
          {params.length > 0 ? (
            <div className={workflowParamListVariants()}>
              <span className={paramsLabelVariants()}>Parameters:</span>
              {params.map((param, i) => (
                <span key={param} className={workflowParamVariants()}>
                  ARG{i + 1}: {param}
                </span>
              ))}
            </div>
          ) : (
            <p className={workflowNoParamsVariants()}>
              This workflow has no input parameters.
            </p>
          )}
          <button
            className={goToDefinitionBtnVariants()}
            onClick={handleGoToDefinition}
          >
            Go to Definition
          </button>
        </div>
      )}
    </div>
  )
}
