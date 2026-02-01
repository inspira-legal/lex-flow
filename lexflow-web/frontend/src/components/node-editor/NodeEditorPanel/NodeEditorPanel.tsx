import { useState } from "react"
import { useWorkflowStore, useUiStore, useSelectionStore } from "@/store"
import type { SelectedReporter } from "@/store/selectionStore"
import type { TreeNode, FormattedValue, WorkflowTree } from "@/api/types"
import { getInputDisplayName } from "@/utils/workflowUtils"
import { toYamlNodeId } from "@/utils/wireUtils"
import { StartNodeEditorPanel } from "../StartNodeEditorPanel"
import {
  getNodeColor,
  getReporterColor as grammarGetReporterColor,
  NODE_TYPE_LABELS,
} from "@/constants"
import { getCategoryByOpcode, getConstruct } from "@/services/grammar"
import { cn } from "@/lib/cn"
import {
  panelVariants,
  headerVariants,
  titleVariants,
  closeBtnVariants,
  contentVariants,
  backBtnVariants,
  emptyVariants,
  nodeInfoVariants,
  colorBarVariants,
  nodeDetailsVariants,
  nodeTypeVariants,
  nodeNameVariants,
  nodeIdBtnVariants,
  descriptionVariants,
  fieldVariants,
  fieldLabelVariants,
  inputTypeVariants,
  inputVariants,
  inputPreviewVariants,
  valueTypeVariants,
  valueContentVariants,
  editHintVariants,
  editInputVariants,
  sectionVariants,
  sectionTitleVariants,
  noInputsVariants,
  branchVariants,
  branchNameVariants,
  branchCountVariants,
  removeBranchBtnVariants,
  addBranchBtnVariants,
  dynamicInputVariants,
  dynamicInputNameVariants,
  paramListVariants,
  paramItemVariants,
  paramNameVariants,
  optionalVariants,
  paramTypeVariants,
  actionsVariants,
  actionBtnVariants,
  actionBtnDangerVariants,
  goToDefinitionBtnVariants,
} from "./styles"
import type { NodeEditorPanelProps } from "./types"

export function NodeEditorPanel({ className }: NodeEditorPanelProps) {
  const {
    tree,
    source,
    opcodes,
    deleteNode,
    duplicateNode,
    updateNodeInput,
    updateReporterInput,
    deleteReporter,
    addDynamicBranch,
    removeDynamicBranch,
    addDynamicInput,
    removeDynamicInput,
  } = useWorkflowStore()
  const { closeNodeEditor } = useUiStore()
  const {
    selectedNodeId,
    selectedReporter,
    selectReporter,
    selectedStartNode,
    selectStartNode,
    clearSelection,
  } = useSelectionStore()
  const [copied, setCopied] = useState(false)

  if (selectedStartNode) {
    return (
      <StartNodeEditorPanel
        workflowName={selectedStartNode}
        onClose={() => {
          selectStartNode(null)
          closeNodeEditor()
        }}
      />
    )
  }

  // Extract raw node ID from composite ID (workflowName::nodeId -> nodeId)
  const rawNodeId = selectedNodeId ? toYamlNodeId(selectedNodeId) : null
  const selectedNode = rawNodeId ? findNode(tree, rawNodeId) : null

  const opcodeInfo = selectedReporter
    ? opcodes.find((op) => op.name === selectedReporter.opcode)
    : selectedNode
      ? opcodes.find((op) => op.name === selectedNode.opcode)
      : null

  const handleClose = () => {
    closeNodeEditor()
    clearSelection()
  }

  const handleCopyId = () => {
    if (rawNodeId) {
      navigator.clipboard.writeText(rawNodeId)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleCopyPath = () => {
    if (selectedReporter) {
      const path = `${selectedReporter.parentNodeId}.${selectedReporter.inputPath.join(".")}`
      navigator.clipboard.writeText(path)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleFindInSource = () => {
    if (rawNodeId) {
      const lines = source.split("\n")
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes(rawNodeId + ":")) {
          window.dispatchEvent(
            new CustomEvent("lexflow:goto-line", { detail: { line: i + 1 } })
          )
          break
        }
      }
    }
  }

  const handleGoToWorkflowDefinition = () => {
    if (selectedNode?.opcode === "workflow_call") {
      const workflowInput = selectedNode.inputs["WORKFLOW"]
      if (workflowInput && workflowInput.type === "literal") {
        const targetName = workflowInput.value as string
        if (targetName) {
          window.dispatchEvent(
            new CustomEvent("lexflow:goto-workflow", {
              detail: { workflowName: targetName },
            })
          )
          closeNodeEditor()
        }
      }
    }
  }

  const handleDelete = () => {
    if (rawNodeId && rawNodeId !== "start") {
      useUiStore.getState().showConfirmDialog({
        title: "Delete Node",
        message: `Delete node "${rawNodeId}"? This action can be undone with Ctrl+Z.`,
        confirmLabel: "Delete",
        variant: "danger",
        onConfirm: () => {
          deleteNode(rawNodeId)
          closeNodeEditor()
        },
      })
    }
  }

  const handleDuplicate = () => {
    if (rawNodeId && rawNodeId !== "start") {
      duplicateNode(rawNodeId)
    }
  }

  const handleBackToNode = () => {
    selectReporter(null)
  }

  const handleUpdateReporterInput = (inputKey: string, newValue: string) => {
    if (selectedReporter && selectedReporter.reporterNodeId) {
      const success = updateReporterInput(
        selectedReporter.reporterNodeId,
        inputKey,
        newValue
      )
      if (success) {
        const updatedInputs = { ...selectedReporter.inputs }
        if (newValue.startsWith("$")) {
          updatedInputs[inputKey] = {
            type: "variable",
            name: newValue.slice(1),
          }
        } else {
          try {
            const parsed = JSON.parse(newValue)
            updatedInputs[inputKey] = { type: "literal", value: parsed }
          } catch {
            updatedInputs[inputKey] = { type: "literal", value: newValue }
          }
        }
        selectReporter({ ...selectedReporter, inputs: updatedInputs })
      }
    }
  }

  const handleDeleteReporter = () => {
    if (selectedReporter) {
      useUiStore.getState().showConfirmDialog({
        title: "Detach Reporter",
        message: "Detach this reporter from its slot? The slot will be set to null. This action can be undone with Ctrl+Z.",
        confirmLabel: "Detach",
        variant: "danger",
        onConfirm: () => {
          deleteReporter(
            selectedReporter.parentNodeId,
            selectedReporter.inputPath
          )
          selectReporter(null)
        },
      })
    }
  }

  const handleFindReporterInSource = () => {
    if (selectedReporter) {
      const lines = source.split("\n")

      if (selectedReporter.reporterNodeId) {
        for (let i = 0; i < lines.length; i++) {
          if (
            lines[i].match(
              new RegExp(`^\\s+${selectedReporter.reporterNodeId}:\\s*$`)
            )
          ) {
            window.dispatchEvent(
              new CustomEvent("lexflow:goto-line", { detail: { line: i + 1 } })
            )
            return
          }
        }
      }

      const pathKey =
        selectedReporter.inputPath[selectedReporter.inputPath.length - 1]
      let inParentNode = false
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        if (line.includes(selectedReporter.parentNodeId + ":")) {
          inParentNode = true
        }
        if (inParentNode && line.includes(pathKey + ":")) {
          window.dispatchEvent(
            new CustomEvent("lexflow:goto-line", { detail: { line: i + 1 } })
          )
          break
        }
      }
    }
  }

  const handleAddDynamicBranch = (branchPrefix: string) => {
    if (rawNodeId) {
      addDynamicBranch(rawNodeId, branchPrefix)
    }
  }

  const handleRemoveDynamicBranch = (branchName: string) => {
    if (rawNodeId) {
      removeDynamicBranch(rawNodeId, branchName)
    }
  }

  const handleAddDynamicInput = (inputPrefix: string) => {
    if (rawNodeId) {
      addDynamicInput(rawNodeId, inputPrefix)
    }
  }

  const handleRemoveDynamicInput = (inputName: string) => {
    if (rawNodeId) {
      removeDynamicInput(rawNodeId, inputName)
    }
  }

  // Handler for "Go to Definition" on reporter workflow calls
  const handleReporterGoToDefinition = () => {
    if (selectedReporter && selectedReporter.opcode === "workflow_call") {
      const workflowInput = selectedReporter.inputs["WORKFLOW"]
      if (workflowInput && workflowInput.type === "literal" && typeof workflowInput.value === "string") {
        const targetName = workflowInput.value
        window.dispatchEvent(
          new CustomEvent("lexflow:goto-workflow", {
            detail: { workflowName: targetName },
          })
        )
        closeNodeEditor()
      }
    }
  }

  // Handlers for dynamic inputs on reporters
  const handleReporterAddDynamicInput = (inputPrefix: string) => {
    if (selectedReporter?.reporterNodeId) {
      addDynamicInput(selectedReporter.reporterNodeId, inputPrefix)
    }
  }

  const handleReporterRemoveDynamicInput = (inputName: string) => {
    if (selectedReporter?.reporterNodeId) {
      removeDynamicInput(selectedReporter.reporterNodeId, inputName)
    }
  }

  if (selectedReporter) {
    return (
      <ReporterPanel
        reporter={selectedReporter}
        parentNode={selectedNode}
        opcodeInfo={opcodeInfo}
        tree={tree}
        copied={copied}
        onCopyPath={handleCopyPath}
        onBackToNode={handleBackToNode}
        onClose={handleClose}
        onUpdateInput={handleUpdateReporterInput}
        onDetach={handleDeleteReporter}
        onFindInSource={handleFindReporterInSource}
        onGoToDefinition={selectedReporter.opcode === "workflow_call" ? handleReporterGoToDefinition : undefined}
        onAddDynamicInput={selectedReporter.reporterNodeId ? handleReporterAddDynamicInput : undefined}
        onRemoveDynamicInput={selectedReporter.reporterNodeId ? handleReporterRemoveDynamicInput : undefined}
        className={className}
      />
    )
  }

  if (!selectedNode) {
    return (
      <div className={cn(panelVariants(), className)}>
        <div className={headerVariants()}>
          <span className={titleVariants()}>Node Editor</span>
          <button className={closeBtnVariants()} onClick={handleClose}>
            ✕
          </button>
        </div>
        <div className={emptyVariants()}>
          <p>Select a node to edit</p>
        </div>
      </div>
    )
  }

  const color = getNodeColor(selectedNode.type)
  const typeLabel = NODE_TYPE_LABELS[selectedNode.type] || "Node"

  return (
    <div className={cn(panelVariants(), className)}>
      <div className={headerVariants()}>
        <span className={titleVariants()}>Node Editor</span>
        <button className={closeBtnVariants()} onClick={handleClose}>
          ✕
        </button>
      </div>

      <div className={contentVariants()}>
        <div className={nodeInfoVariants()}>
          <div className={colorBarVariants()} style={{ backgroundColor: color }} />
          <div className={nodeDetailsVariants()}>
            <span className={nodeTypeVariants()}>{typeLabel}</span>
            <h3 className={nodeNameVariants()}>
              {formatOpcodeName(selectedNode.opcode)}
            </h3>
            <button
              className={nodeIdBtnVariants()}
              onClick={handleCopyId}
              title="Copy node ID"
            >
              {copied ? "✓ Copied!" : `ID: ${selectedNode.id}`}
            </button>
          </div>
        </div>

        {opcodeInfo?.description && (
          <div className={descriptionVariants()}>{opcodeInfo.description}</div>
        )}

        <div className={fieldVariants()}>
          <label className={fieldLabelVariants()}>Opcode</label>
          <input
            type="text"
            value={selectedNode.opcode}
            readOnly
            className={inputVariants()}
          />
        </div>

        <div className={sectionVariants()}>
          <h4 className={sectionTitleVariants()}>Inputs</h4>
          {Object.entries(selectedNode.inputs).length === 0 ? (
            <p className={noInputsVariants()}>No inputs</p>
          ) : (
            Object.entries(selectedNode.inputs).map(([key, value]) => (
              <InputField
                key={key}
                name={getInputDisplayName(key, selectedNode.opcode, tree, selectedNode.inputs)}
                originalKey={key}
                value={value}
                paramInfo={opcodeInfo?.parameters.find(
                  (p) => p.name.toUpperCase() === key
                )}
                onUpdate={(inputKey, newValue) =>
                  updateNodeInput(rawNodeId!, inputKey, newValue)
                }
              />
            ))
          )}
        </div>

        {selectedNode.opcode === "workflow_call" && (
          <div className={sectionVariants()}>
            <button
              className={goToDefinitionBtnVariants()}
              onClick={handleGoToWorkflowDefinition}
              title="Navigate canvas to the workflow definition"
            >
              Go to Definition
            </button>
          </div>
        )}

        {opcodeInfo && opcodeInfo.parameters.length > 0 && (
          <div className={sectionVariants()}>
            <h4 className={sectionTitleVariants()}>Parameters</h4>
            <div className={paramListVariants()}>
              {opcodeInfo.parameters.map((param) => (
                <div key={param.name} className={paramItemVariants()}>
                  <span className={paramNameVariants()}>
                    {param.name}
                    {!param.required && (
                      <span className={optionalVariants()}>?</span>
                    )}
                  </span>
                  <span className={paramTypeVariants()}>{param.type}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {(() => {
          const construct = getConstruct(selectedNode.opcode)
          const hasDynamicBranches = construct?.dynamic_branches
          const hasDynamicInputs = construct?.dynamic_inputs
          const hasBranches = construct?.branches && construct.branches.length > 0

          let dynamicBranchPrefix: string | null = null
          if (hasDynamicBranches && construct?.branches) {
            for (const branch of construct.branches) {
              const match = branch.name.match(/^([A-Z]+)\d+$/)
              if (match) {
                dynamicBranchPrefix = match[1]
                break
              }
            }
          }

          const existingDynamicBranches = selectedNode.children
            .filter((b) => dynamicBranchPrefix && b.name.startsWith(dynamicBranchPrefix))
            .map((b) => b.name)

          const existingDynamicInputs = Object.keys(selectedNode.inputs)
            .filter((k) => /^ARG\d+$/.test(k))
            .sort((a, b) => {
              const numA = parseInt(a.replace("ARG", ""))
              const numB = parseInt(b.replace("ARG", ""))
              return numA - numB
            })

          const showBranchesSection = selectedNode.children.length > 0 || hasDynamicBranches

          return (
            <>
              {showBranchesSection && hasBranches && (
                <div className={sectionVariants()}>
                  <h4 className={sectionTitleVariants()}>Branches</h4>
                  {selectedNode.children.length === 0 && hasDynamicBranches ? (
                    <p className={noInputsVariants()}>No branches connected</p>
                  ) : (
                    selectedNode.children.map((branch, i) => {
                      const isDynamic = dynamicBranchPrefix && branch.name.startsWith(dynamicBranchPrefix)
                      const canRemove = isDynamic && existingDynamicBranches.length > 1
                      return (
                        <div key={i} className={branchVariants()}>
                          <span className={branchNameVariants()}>{branch.name}</span>
                          <span className={branchCountVariants()}>
                            {branch.children.length} node(s)
                          </span>
                          {canRemove && (
                            <button
                              className={removeBranchBtnVariants()}
                              onClick={() => handleRemoveDynamicBranch(branch.name)}
                              title={`Remove ${branch.name}`}
                            >
                              ×
                            </button>
                          )}
                        </div>
                      )
                    })
                  )}
                  {hasDynamicBranches && dynamicBranchPrefix && (
                    <button
                      className={addBranchBtnVariants()}
                      onClick={() => handleAddDynamicBranch(dynamicBranchPrefix!)}
                    >
                      + Add {dynamicBranchPrefix === "CATCH" ? "Catch Handler" : "Branch"}
                    </button>
                  )}
                </div>
              )}

              {hasDynamicInputs && selectedNode.opcode === "workflow_call" && (
                <div className={sectionVariants()}>
                  <h4 className={sectionTitleVariants()}>Arguments</h4>
                  {existingDynamicInputs.length === 0 ? (
                    <p className={noInputsVariants()}>No arguments</p>
                  ) : (
                    existingDynamicInputs.map((inputName) => (
                      <div key={inputName} className={dynamicInputVariants()}>
                        <span className={dynamicInputNameVariants()}>{inputName}</span>
                        <button
                          className={removeBranchBtnVariants()}
                          onClick={() => handleRemoveDynamicInput(inputName)}
                          title={`Remove ${inputName}`}
                        >
                          ×
                        </button>
                      </div>
                    ))
                  )}
                  <button
                    className={addBranchBtnVariants()}
                    onClick={() => handleAddDynamicInput("ARG")}
                  >
                    + Add Argument
                  </button>
                </div>
              )}
            </>
          )
        })()}
      </div>

      <div className={actionsVariants()}>
        <button className={actionBtnVariants()} onClick={handleFindInSource}>
          Find in Source
        </button>
        <button
          className={actionBtnVariants()}
          onClick={handleDuplicate}
          disabled={rawNodeId === "start"}
          title={
            rawNodeId === "start"
              ? "Cannot duplicate start node"
              : "Duplicate node (Ctrl+D)"
          }
        >
          Duplicate
        </button>
        <button
          className={actionBtnDangerVariants()}
          onClick={handleDelete}
          disabled={rawNodeId === "start"}
          title={
            rawNodeId === "start"
              ? "Cannot delete start node"
              : "Delete node (Del)"
          }
        >
          Delete
        </button>
      </div>
    </div>
  )
}

interface ReporterPanelProps {
  reporter: SelectedReporter
  parentNode: TreeNode | null
  opcodeInfo:
    | {
        name: string
        description?: string
        parameters: Array<{ name: string; type: string; required: boolean }>
      }
    | null
    | undefined
  tree: WorkflowTree | null
  copied: boolean
  onCopyPath: () => void
  onBackToNode: () => void
  onClose: () => void
  onUpdateInput: (inputKey: string, newValue: string) => void
  onDetach: () => void
  onFindInSource: () => void
  onGoToDefinition?: () => void
  onAddDynamicInput?: (prefix: string) => void
  onRemoveDynamicInput?: (inputName: string) => void
  className?: string
}

function ReporterPanel({
  reporter,
  parentNode,
  opcodeInfo,
  tree,
  copied,
  onCopyPath,
  onBackToNode,
  onClose,
  onUpdateInput,
  onDetach,
  onFindInSource,
  onGoToDefinition,
  onAddDynamicInput,
  onRemoveDynamicInput,
  className,
}: ReporterPanelProps) {
  const color = getReporterColor(reporter.opcode)
  const typeLabel = getReporterTypeLabel(reporter.opcode)
  const isWorkflowCall = reporter.opcode === "workflow_call"

  // Get existing dynamic inputs (ARG1, ARG2, etc.)
  const existingDynamicInputs = Object.keys(reporter.inputs)
    .filter((k) => /^ARG\d+$/.test(k))
    .sort((a, b) => {
      const numA = parseInt(a.replace("ARG", ""))
      const numB = parseInt(b.replace("ARG", ""))
      return numA - numB
    })

  // Check if this opcode has dynamic inputs
  const construct = getConstruct(reporter.opcode)
  const hasDynamicInputs = construct?.dynamic_inputs

  return (
    <div className={cn(panelVariants(), className)}>
      <div className={headerVariants()}>
        <span className={titleVariants()}>Node Editor</span>
        <button className={closeBtnVariants()} onClick={onClose}>
          ✕
        </button>
      </div>

      <div className={contentVariants()}>
        {parentNode && (
          <button className={backBtnVariants()} onClick={onBackToNode}>
            ← Back to {parentNode.id}
          </button>
        )}

        <div className={nodeInfoVariants()}>
          <div className={colorBarVariants()} style={{ backgroundColor: color }} />
          <div className={nodeDetailsVariants()}>
            <span className={nodeTypeVariants()}>{typeLabel}</span>
            <h3 className={nodeNameVariants()}>
              {formatOpcodeName(reporter.opcode)}
            </h3>
            <button
              className={nodeIdBtnVariants()}
              onClick={onCopyPath}
              title="Copy reporter ID"
            >
              {copied ? "✓ Copied!" : `ID: ${reporter.reporterNodeId || reporter.inputPath.join(".")}`}
            </button>
          </div>
        </div>

        {opcodeInfo?.description && (
          <div className={descriptionVariants()}>{opcodeInfo.description}</div>
        )}

        <div className={fieldVariants()}>
          <label className={fieldLabelVariants()}>Opcode</label>
          <input
            type="text"
            value={reporter.opcode}
            readOnly
            className={inputVariants()}
          />
        </div>

        <div className={sectionVariants()}>
          <h4 className={sectionTitleVariants()}>Inputs</h4>
          {Object.entries(reporter.inputs).length === 0 ? (
            <p className={noInputsVariants()}>No inputs</p>
          ) : (
            Object.entries(reporter.inputs).map(([key, value]) => (
              <InputField
                key={key}
                name={getInputDisplayName(key, reporter.opcode, tree, reporter.inputs)}
                originalKey={key}
                value={value}
                paramInfo={opcodeInfo?.parameters.find(
                  (p) => p.name.toUpperCase() === key
                )}
                onUpdate={onUpdateInput}
              />
            ))
          )}
        </div>

        {isWorkflowCall && onGoToDefinition && (
          <div className={sectionVariants()}>
            <button
              className={goToDefinitionBtnVariants()}
              onClick={onGoToDefinition}
              title="Navigate canvas to the workflow definition"
            >
              Go to Definition
            </button>
          </div>
        )}

        {opcodeInfo && opcodeInfo.parameters.length > 0 && (
          <div className={sectionVariants()}>
            <h4 className={sectionTitleVariants()}>Parameters</h4>
            <div className={paramListVariants()}>
              {opcodeInfo.parameters.map((param) => (
                <div key={param.name} className={paramItemVariants()}>
                  <span className={paramNameVariants()}>
                    {param.name}
                    {!param.required && (
                      <span className={optionalVariants()}>?</span>
                    )}
                  </span>
                  <span className={paramTypeVariants()}>{param.type}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {hasDynamicInputs && isWorkflowCall && onAddDynamicInput && onRemoveDynamicInput && (
          <div className={sectionVariants()}>
            <h4 className={sectionTitleVariants()}>Arguments</h4>
            {existingDynamicInputs.length === 0 ? (
              <p className={noInputsVariants()}>No arguments</p>
            ) : (
              existingDynamicInputs.map((inputName) => (
                <div key={inputName} className={dynamicInputVariants()}>
                  <span className={dynamicInputNameVariants()}>
                    {getInputDisplayName(inputName, reporter.opcode, tree, reporter.inputs)}
                  </span>
                  <button
                    className={removeBranchBtnVariants()}
                    onClick={() => onRemoveDynamicInput(inputName)}
                    title={`Remove ${inputName}`}
                  >
                    ×
                  </button>
                </div>
              ))
            )}
            <button
              className={addBranchBtnVariants()}
              onClick={() => onAddDynamicInput("ARG")}
            >
              + Add Argument
            </button>
          </div>
        )}
      </div>

      <div className={actionsVariants()}>
        <button className={actionBtnVariants()} onClick={onFindInSource}>
          Find in Source
        </button>
        <button
          className={actionBtnDangerVariants()}
          onClick={onDetach}
          title="Detach reporter from slot (replace with null)"
        >
          Detach
        </button>
      </div>
    </div>
  )
}

interface InputFieldProps {
  name: string
  originalKey?: string
  value: FormattedValue
  paramInfo?: { name: string; type: string; required: boolean }
  onUpdate?: (inputKey: string, newValue: string) => void
}

function InputField({ name, originalKey, value, paramInfo, onUpdate }: InputFieldProps) {
  const keyForUpdate = originalKey || name
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState("")

  const displayValue = formatValue(value)

  const getEditableValue = (val: FormattedValue): string => {
    switch (val.type) {
      case "literal":
        if (typeof val.value === "string") return val.value
        return JSON.stringify(val.value)
      case "variable":
        return `$${val.name}`
      default:
        return displayValue
    }
  }

  const handleStartEdit = () => {
    if (value.type === "literal" || value.type === "variable") {
      setEditValue(getEditableValue(value))
      setIsEditing(true)
    }
  }

  const handleSave = () => {
    if (onUpdate && editValue !== getEditableValue(value)) {
      onUpdate(keyForUpdate, editValue)
    }
    setIsEditing(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSave()
    } else if (e.key === "Escape") {
      setIsEditing(false)
    }
  }

  const isEditable = value.type === "literal" || value.type === "variable"

  return (
    <div className={fieldVariants()}>
      <label className={fieldLabelVariants()}>
        {name}
        {paramInfo && (
          <span className={inputTypeVariants()}>{paramInfo.type}</span>
        )}
      </label>
      {isEditing ? (
        <input
          type="text"
          className={editInputVariants()}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={handleSave}
          onKeyDown={handleKeyDown}
          autoFocus
        />
      ) : (
        <div
          className={cn(inputPreviewVariants({ editable: isEditable }), "group")}
          onClick={handleStartEdit}
          title={isEditable ? "Click to edit" : undefined}
        >
          <span className={valueTypeVariants()}>{value.type}</span>
          <span className={valueContentVariants()}>{displayValue}</span>
          {isEditable && <span className={editHintVariants()}>Click to edit</span>}
        </div>
      )}
    </div>
  )
}

function formatValue(value: FormattedValue): string {
  switch (value.type) {
    case "literal":
      if (typeof value.value === "string") return `"${value.value}"`
      if (typeof value.value === "object" && value.value !== null) {
        return JSON.stringify(value.value, null, 2)
      }
      return String(value.value)
    case "variable":
      return `$${value.name}`
    case "reporter":
      return `${formatOpcodeName(value.opcode || "")}(...)`
    case "workflow_call":
      return `→ ${value.name}`
    case "branch":
      return `→ ${value.target}`
    case "dict":
      return JSON.stringify(value.value, null, 2)
    case "truncated":
      return value.display || "..."
    default:
      return "?"
  }
}

function formatOpcodeName(opcode: string): string {
  return opcode
    .replace(/^(control_|data_|io_|operator_|workflow_)/, "")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

function getReporterColor(opcode: string): string {
  return grammarGetReporterColor(opcode)
}

function getReporterTypeLabel(opcode: string): string {
  const category = getCategoryByOpcode(opcode)
  if (category) {
    return `${category.label} Reporter`
  }
  return "Reporter"
}

function findNode(tree: any, nodeId: string): TreeNode | null {
  if (!tree) return null

  function searchNodes(nodes: TreeNode[]): TreeNode | null {
    for (const node of nodes) {
      if (node.id === nodeId) return node
      if (node.children) {
        for (const branch of node.children) {
          const found = searchNodes(branch.children)
          if (found) return found
        }
      }
    }
    return null
  }

  for (const workflow of tree.workflows || []) {
    const found = searchNodes(workflow.children || [])
    if (found) return found

    const orphanFound = searchNodes(workflow.orphans || [])
    if (orphanFound) return orphanFound
  }

  return null
}
