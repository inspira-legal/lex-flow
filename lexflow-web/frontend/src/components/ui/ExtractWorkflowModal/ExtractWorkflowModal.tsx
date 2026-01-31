import { useEffect, useRef, useState } from "react"
import { createPortal } from "react-dom"
import { cn } from "@/lib/cn"
import {
  overlayVariants,
  dialogVariants,
  headerVariants,
  titleVariants,
  bodyVariants,
  footerVariants,
  buttonBaseVariants,
  cancelButtonVariants,
  confirmButtonVariants,
  formFieldVariants,
  labelVariants,
  inputVariants,
  errorVariants,
  tagListVariants,
  tagVariants,
  tagRemoveVariants,
  addRowVariants,
  addButtonVariants,
  variableRowVariants,
  smallInputVariants,
  removeButtonVariants,
} from "../NewWorkflowModal/styles"
import { infoBoxVariants } from "./styles"
import type { ExtractWorkflowModalProps } from "./types"

export function ExtractWorkflowModal({
  isOpen,
  existingWorkflowNames,
  nodeIds,
  suggestedInputs,
  suggestedOutputs,
  onConfirm,
  onCancel,
}: ExtractWorkflowModalProps) {
  const nameInputRef = useRef<HTMLInputElement>(null)
  const [name, setName] = useState("")
  const [nameError, setNameError] = useState<string | null>(null)
  const [inputs, setInputs] = useState<string[]>([])
  const [newInput, setNewInput] = useState("")
  const [outputs, setOutputs] = useState<string[]>([])
  const [newOutput, setNewOutput] = useState("")
  const [variables, setVariables] = useState<Array<{ name: string; value: string }>>([])

  // Reset form when modal opens or suggestions change
  useEffect(() => {
    if (isOpen) {
      // Reset form state when opening modal - this is intentional to synchronize
      // with external state (suggestedInputs/Outputs from validation)
      /* eslint-disable react-hooks/set-state-in-effect */
      setName("")
      setNameError(null)
      setInputs(suggestedInputs)
      setNewInput("")
      setOutputs(suggestedOutputs)
      setNewOutput("")
      setVariables([])
      /* eslint-enable react-hooks/set-state-in-effect */
      setTimeout(() => {
        nameInputRef.current?.focus()
      }, 50)
    }
  }, [isOpen, suggestedInputs, suggestedOutputs])

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onCancel()
      }
    }

    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onCancel])

  const validateName = (value: string): string | null => {
    if (!value.trim()) {
      return "Workflow name is required"
    }
    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(value)) {
      return "Name must start with a letter or underscore and contain only letters, numbers, and underscores"
    }
    if (existingWorkflowNames.includes(value)) {
      return "A workflow with this name already exists"
    }
    return null
  }

  const handleNameChange = (value: string) => {
    setName(value)
    if (nameError) {
      setNameError(validateName(value))
    }
  }

  const handleNameBlur = () => {
    setNameError(validateName(name))
  }

  const addInput = () => {
    const trimmed = newInput.trim()
    if (trimmed && !inputs.includes(trimmed) && /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(trimmed)) {
      setInputs([...inputs, trimmed])
      setNewInput("")
    }
  }

  const removeInput = (input: string) => {
    setInputs(inputs.filter((i) => i !== input))
  }

  const addOutput = () => {
    const trimmed = newOutput.trim()
    if (trimmed && !outputs.includes(trimmed) && /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(trimmed)) {
      setOutputs([...outputs, trimmed])
      setNewOutput("")
    }
  }

  const removeOutput = (output: string) => {
    setOutputs(outputs.filter((o) => o !== output))
  }

  const addVariable = () => {
    setVariables([...variables, { name: "", value: "" }])
  }

  const updateVariable = (index: number, field: "name" | "value", value: string) => {
    const updated = [...variables]
    updated[index][field] = value
    setVariables(updated)
  }

  const removeVariable = (index: number) => {
    setVariables(variables.filter((_, i) => i !== index))
  }

  const handleSubmit = () => {
    const error = validateName(name)
    if (error) {
      setNameError(error)
      return
    }

    // Convert variables array to object with parsed values
    const varsObj: Record<string, unknown> = {}
    for (const v of variables) {
      if (v.name.trim() && /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(v.name.trim())) {
        let parsedValue: unknown = v.value
        try {
          parsedValue = JSON.parse(v.value)
        } catch {
          // Keep as string if not valid JSON
        }
        varsObj[v.name.trim()] = parsedValue
      }
    }

    onConfirm({
      name: name.trim(),
      inputs,
      outputs,
      variables: varsObj,
    })
  }

  if (!isOpen) return null

  return createPortal(
    <div
      className={cn(overlayVariants())}
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="extract-workflow-dialog-title"
    >
      <div
        className={cn(dialogVariants())}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={cn(headerVariants())}>
          <h2 id="extract-workflow-dialog-title" className={cn(titleVariants())}>
            Extract to Workflow
          </h2>
        </div>

        <div className={cn(bodyVariants())}>
          {/* Info box showing what will be extracted */}
          <div className={cn(infoBoxVariants())}>
            <strong>{nodeIds.length} nodes</strong> will be extracted into a new workflow.
            The selected nodes will be replaced with a workflow_call node.
          </div>

          {/* Workflow Name */}
          <div className={cn(formFieldVariants())}>
            <label className={cn(labelVariants())}>
              Workflow Name <span className="text-accent-red">*</span>
            </label>
            <input
              ref={nameInputRef}
              type="text"
              className={cn(inputVariants())}
              placeholder="my_workflow"
              value={name}
              onChange={(e) => handleNameChange(e.target.value)}
              onBlur={handleNameBlur}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSubmit()
                }
              }}
            />
            {nameError && <p className={cn(errorVariants())}>{nameError}</p>}
          </div>

          {/* Interface Inputs */}
          <div className={cn(formFieldVariants())}>
            <label className={cn(labelVariants())}>
              Interface Inputs
              {suggestedInputs.length > 0 && (
                <span className="text-text-muted text-xs ml-2">(auto-detected)</span>
              )}
            </label>
            {inputs.length > 0 && (
              <div className={cn(tagListVariants())}>
                {inputs.map((input) => (
                  <span key={input} className={cn(tagVariants())}>
                    {input}
                    <button
                      className={cn(tagRemoveVariants())}
                      onClick={() => removeInput(input)}
                      aria-label={`Remove ${input}`}
                    >
                      x
                    </button>
                  </span>
                ))}
              </div>
            )}
            <div className={cn(addRowVariants())}>
              <input
                type="text"
                className={cn(inputVariants())}
                placeholder="input_name"
                value={newInput}
                onChange={(e) => setNewInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    addInput()
                  }
                }}
              />
              <button
                type="button"
                className={cn(addButtonVariants())}
                onClick={addInput}
              >
                Add
              </button>
            </div>
          </div>

          {/* Interface Outputs */}
          <div className={cn(formFieldVariants())}>
            <label className={cn(labelVariants())}>
              Interface Outputs
              {suggestedOutputs.length > 0 && (
                <span className="text-text-muted text-xs ml-2">(auto-detected)</span>
              )}
            </label>
            {outputs.length > 0 && (
              <div className={cn(tagListVariants())}>
                {outputs.map((output) => (
                  <span key={output} className={cn(tagVariants())}>
                    {output}
                    <button
                      className={cn(tagRemoveVariants())}
                      onClick={() => removeOutput(output)}
                      aria-label={`Remove ${output}`}
                    >
                      x
                    </button>
                  </span>
                ))}
              </div>
            )}
            <div className={cn(addRowVariants())}>
              <input
                type="text"
                className={cn(inputVariants())}
                placeholder="output_name"
                value={newOutput}
                onChange={(e) => setNewOutput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    addOutput()
                  }
                }}
              />
              <button
                type="button"
                className={cn(addButtonVariants())}
                onClick={addOutput}
              >
                Add
              </button>
            </div>
          </div>

          {/* Variables */}
          <div className={cn(formFieldVariants())}>
            <label className={cn(labelVariants())}>Variables</label>
            {variables.map((variable, index) => (
              <div key={index} className={cn(variableRowVariants())}>
                <input
                  type="text"
                  className={cn(smallInputVariants())}
                  placeholder="name"
                  value={variable.name}
                  onChange={(e) => updateVariable(index, "name", e.target.value)}
                />
                <span className="text-text-muted">=</span>
                <input
                  type="text"
                  className={cn(smallInputVariants())}
                  placeholder="value"
                  value={variable.value}
                  onChange={(e) => updateVariable(index, "value", e.target.value)}
                />
                <button
                  type="button"
                  className={cn(removeButtonVariants())}
                  onClick={() => removeVariable(index)}
                  aria-label="Remove variable"
                >
                  x
                </button>
              </div>
            ))}
            <button
              type="button"
              className={cn(addButtonVariants())}
              onClick={addVariable}
            >
              + Add Variable
            </button>
          </div>
        </div>

        <div className={cn(footerVariants())}>
          <button
            className={cn(buttonBaseVariants(), cancelButtonVariants())}
            onClick={onCancel}
          >
            Cancel
          </button>
          <button
            className={cn(buttonBaseVariants(), confirmButtonVariants())}
            onClick={handleSubmit}
          >
            Extract
          </button>
        </div>
      </div>
    </div>,
    document.body
  )
}
