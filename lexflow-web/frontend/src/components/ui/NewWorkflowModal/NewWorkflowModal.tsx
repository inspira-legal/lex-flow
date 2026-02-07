import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/cn";
import type { DetailedInput, InputType } from "@/api/types";
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
} from "./styles";
import type { NewWorkflowModalProps } from "./types";

const INPUT_TYPES: InputType[] = [
  "string",
  "number",
  "boolean",
  "list",
  "dict",
  "any",
];

export function NewWorkflowModal({
  isOpen,
  existingWorkflowNames,
  onConfirm,
  onCancel,
}: NewWorkflowModalProps) {
  const nameInputRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState("");
  const [nameError, setNameError] = useState<string | null>(null);
  const [inputs, setInputs] = useState<DetailedInput[]>([]);
  const [newInputName, setNewInputName] = useState("");
  const [newInputType, setNewInputType] = useState<InputType>("string");
  const [newInputRequired, setNewInputRequired] = useState(false);
  const [outputs, setOutputs] = useState<string[]>([]);
  const [newOutput, setNewOutput] = useState("");
  const [variables, setVariables] = useState<
    Array<{ name: string; value: string }>
  >([]);

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setName("");
      setNameError(null);
      setInputs([]);
      setNewInputName("");
      setNewInputType("string");
      setNewInputRequired(false);
      setOutputs([]);
      setNewOutput("");
      setVariables([]);
      // Focus name input with a small delay
      setTimeout(() => {
        nameInputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onCancel();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onCancel]);

  const validateName = (value: string): string | null => {
    if (!value.trim()) {
      return "Workflow name is required";
    }
    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(value)) {
      return "Name must start with a letter or underscore and contain only letters, numbers, and underscores";
    }
    if (existingWorkflowNames.includes(value)) {
      return "A workflow with this name already exists";
    }
    return null;
  };

  const handleNameChange = (value: string) => {
    setName(value);
    if (nameError) {
      setNameError(validateName(value));
    }
  };

  const handleNameBlur = () => {
    setNameError(validateName(name));
  };

  const addInput = () => {
    const trimmed = newInputName.trim();
    if (
      trimmed &&
      !inputs.some((i) => i.name === trimmed) &&
      /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(trimmed)
    ) {
      setInputs([
        ...inputs,
        { name: trimmed, type: newInputType, required: newInputRequired },
      ]);
      setNewInputName("");
      setNewInputType("string");
      setNewInputRequired(false);
    }
  };

  const removeInput = (inputName: string) => {
    setInputs(inputs.filter((i) => i.name !== inputName));
  };

  const addOutput = () => {
    const trimmed = newOutput.trim();
    if (
      trimmed &&
      !outputs.includes(trimmed) &&
      /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(trimmed)
    ) {
      setOutputs([...outputs, trimmed]);
      setNewOutput("");
    }
  };

  const removeOutput = (output: string) => {
    setOutputs(outputs.filter((o) => o !== output));
  };

  const addVariable = () => {
    setVariables([...variables, { name: "", value: "" }]);
  };

  const updateVariable = (
    index: number,
    field: "name" | "value",
    value: string,
  ) => {
    const updated = [...variables];
    updated[index][field] = value;
    setVariables(updated);
  };

  const removeVariable = (index: number) => {
    setVariables(variables.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    const error = validateName(name);
    if (error) {
      setNameError(error);
      return;
    }

    // Convert variables array to object with parsed values
    const varsObj: Record<string, unknown> = {};
    for (const v of variables) {
      if (v.name.trim() && /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(v.name.trim())) {
        let parsedValue: unknown = v.value;
        try {
          parsedValue = JSON.parse(v.value);
        } catch {
          // Keep as string if not valid JSON
        }
        varsObj[v.name.trim()] = parsedValue;
      }
    }

    onConfirm({
      name: name.trim(),
      inputs,
      outputs,
      variables: varsObj,
    });
  };

  if (!isOpen) return null;

  return createPortal(
    <div
      className={cn(overlayVariants())}
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="new-workflow-dialog-title"
    >
      <div
        className={cn(dialogVariants())}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={cn(headerVariants())}>
          <h2 id="new-workflow-dialog-title" className={cn(titleVariants())}>
            Create New Workflow
          </h2>
        </div>

        <div className={cn(bodyVariants())}>
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
                  handleSubmit();
                }
              }}
            />
            {nameError && <p className={cn(errorVariants())}>{nameError}</p>}
          </div>

          {/* Interface Inputs */}
          <div className={cn(formFieldVariants())}>
            <label className={cn(labelVariants())}>Interface Inputs</label>
            {inputs.length > 0 && (
              <div className={cn(tagListVariants())}>
                {inputs.map((input) => (
                  <span key={input.name} className={cn(tagVariants())}>
                    {input.name}
                    <span className="text-[10px] opacity-70 ml-0.5">
                      {input.type}
                    </span>
                    {input.required && (
                      <span className="text-accent-red text-[10px]">*</span>
                    )}
                    <button
                      className={cn(tagRemoveVariants())}
                      onClick={() => removeInput(input.name)}
                      aria-label={`Remove ${input.name}`}
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
                value={newInputName}
                onChange={(e) => setNewInputName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addInput();
                  }
                }}
              />
              <select
                className={cn(inputVariants(), "w-24")}
                value={newInputType}
                onChange={(e) => setNewInputType(e.target.value as InputType)}
              >
                {INPUT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
              <label className="flex items-center gap-1 text-xs text-text-secondary whitespace-nowrap">
                <input
                  type="checkbox"
                  checked={newInputRequired}
                  onChange={(e) => setNewInputRequired(e.target.checked)}
                />
                Req
              </label>
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
            <label className={cn(labelVariants())}>Interface Outputs</label>
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
                    e.preventDefault();
                    addOutput();
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
                  onChange={(e) =>
                    updateVariable(index, "name", e.target.value)
                  }
                />
                <span className="text-text-muted">=</span>
                <input
                  type="text"
                  className={cn(smallInputVariants())}
                  placeholder="value"
                  value={variable.value}
                  onChange={(e) =>
                    updateVariable(index, "value", e.target.value)
                  }
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
            Create
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
