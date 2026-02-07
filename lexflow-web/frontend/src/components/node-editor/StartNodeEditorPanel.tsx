import { useState } from "react";
import { useWorkflowStore, useSelectionStore, useUiStore } from "@/store";
import type { WorkflowNode, DetailedInput, InputType } from "@/api/types";
import { cn } from "@/lib/cn";
import {
  panelVariants,
  headerVariants,
  titleVariants,
  closeBtnVariants,
  contentVariants,
  emptyVariants,
  nodeInfoVariants,
  colorBarVariants,
  nodeDetailsVariants,
  nodeTypeVariants,
  nodeNameVariants,
  sectionVariants,
  sectionTitleVariants,
  noInputsVariants,
  inputVariants,
  inputPreviewVariants,
  valueContentVariants,
  editInputVariants,
  actionBtnVariants,
} from "./NodeEditorPanel/styles";

const INPUT_TYPES: InputType[] = [
  "string",
  "number",
  "boolean",
  "list",
  "dict",
  "any",
];

interface StartNodeEditorPanelProps {
  workflowName: string;
  onClose: () => void;
}

export function StartNodeEditorPanel({
  workflowName,
  onClose,
}: StartNodeEditorPanelProps) {
  const {
    tree,
    addVariable,
    updateVariable,
    deleteVariable,
    updateWorkflowInterface,
    deleteWorkflow,
  } = useWorkflowStore();
  const { selectStartNode } = useSelectionStore();

  const workflow = tree?.workflows.find((w) => w.name === workflowName) as
    | WorkflowNode
    | undefined;

  const [newVarName, setNewVarName] = useState("");
  const [newVarValue, setNewVarValue] = useState("");
  const [editingVar, setEditingVar] = useState<string | null>(null);
  const [editVarName, setEditVarName] = useState("");
  const [editVarValue, setEditVarValue] = useState("");

  // Input form state
  const [newInputName, setNewInputName] = useState("");
  const [newInputType, setNewInputType] = useState<InputType>("string");
  const [newInputRequired, setNewInputRequired] = useState(false);

  // Editing existing input
  const [editingInput, setEditingInput] = useState<string | null>(null);
  const [editInputName, setEditInputName] = useState("");
  const [editInputType, setEditInputType] = useState<InputType>("string");
  const [editInputRequired, setEditInputRequired] = useState(false);

  const [newOutput, setNewOutput] = useState("");

  if (!workflow) {
    return (
      <div className={panelVariants()}>
        <div className={headerVariants()}>
          <span className={titleVariants()}>Start Node</span>
          <button className={closeBtnVariants()} onClick={onClose}>
            ✕
          </button>
        </div>
        <div className={emptyVariants()}>
          <p>Workflow not found</p>
        </div>
      </div>
    );
  }

  const handleClose = () => {
    selectStartNode(null);
    onClose();
  };

  const handleAddVariable = () => {
    if (!newVarName.trim()) return;
    const value = parseValue(newVarValue);
    if (addVariable(workflowName, newVarName.trim(), value)) {
      setNewVarName("");
      setNewVarValue("");
    }
  };

  const handleStartEditVar = (name: string, value: unknown) => {
    setEditingVar(name);
    setEditVarName(name);
    setEditVarValue(formatValue(value));
  };

  const handleSaveEditVar = () => {
    if (!editingVar || !editVarName.trim()) return;
    const value = parseValue(editVarValue);
    if (updateVariable(workflowName, editingVar, editVarName.trim(), value)) {
      setEditingVar(null);
      setEditVarName("");
      setEditVarValue("");
    }
  };

  const handleCancelEditVar = () => {
    setEditingVar(null);
    setEditVarName("");
    setEditVarValue("");
  };

  const handleDeleteVar = (name: string) => {
    useUiStore.getState().showConfirmDialog({
      title: "Delete Variable",
      message: `Delete variable "$${name}"?`,
      confirmLabel: "Delete",
      variant: "danger",
      onConfirm: () => deleteVariable(workflowName, name),
    });
  };

  const handleDeleteWorkflow = () => {
    useUiStore.getState().showConfirmDialog({
      title: "Delete Workflow",
      message: `Are you sure you want to delete the workflow "${workflowName}"? This action cannot be undone.`,
      confirmLabel: "Delete",
      variant: "danger",
      onConfirm: () => {
        deleteWorkflow(workflowName);
        handleClose();
      },
    });
  };

  const handleAddInput = () => {
    const name = newInputName.trim();
    if (!name) return;
    if (workflow.interface.inputs.some((i) => i.name === name)) return;
    const newInputs: DetailedInput[] = [
      ...workflow.interface.inputs,
      { name, type: newInputType, required: newInputRequired },
    ];
    if (
      updateWorkflowInterface(
        workflowName,
        newInputs,
        workflow.interface.outputs,
      )
    ) {
      setNewInputName("");
      setNewInputType("string");
      setNewInputRequired(false);
    }
  };

  const handleRemoveInput = (inputName: string) => {
    const newInputs = workflow.interface.inputs.filter(
      (i) => i.name !== inputName,
    );
    updateWorkflowInterface(
      workflowName,
      newInputs,
      workflow.interface.outputs,
    );
  };

  const handleStartEditInput = (input: DetailedInput) => {
    setEditingInput(input.name);
    setEditInputName(input.name);
    setEditInputType(input.type);
    setEditInputRequired(input.required);
  };

  const handleSaveEditInput = () => {
    if (!editingInput || !editInputName.trim()) return;
    const newInputs = workflow.interface.inputs.map((i) =>
      i.name === editingInput
        ? {
            name: editInputName.trim(),
            type: editInputType,
            required: editInputRequired,
          }
        : i,
    );
    if (
      updateWorkflowInterface(
        workflowName,
        newInputs,
        workflow.interface.outputs,
      )
    ) {
      setEditingInput(null);
    }
  };

  const handleCancelEditInput = () => {
    setEditingInput(null);
  };

  const handleAddOutput = () => {
    if (!newOutput.trim()) return;
    const newOutputs = [...workflow.interface.outputs, newOutput.trim()];
    if (
      updateWorkflowInterface(
        workflowName,
        workflow.interface.inputs,
        newOutputs,
      )
    ) {
      setNewOutput("");
    }
  };

  const handleRemoveOutput = (output: string) => {
    const newOutputs = workflow.interface.outputs.filter((o) => o !== output);
    updateWorkflowInterface(
      workflowName,
      workflow.interface.inputs,
      newOutputs,
    );
  };

  const varEntries = Object.entries(workflow.variables);

  return (
    <div className={panelVariants()}>
      <div className={headerVariants()}>
        <span className={titleVariants()}>Start Node</span>
        <button className={closeBtnVariants()} onClick={handleClose}>
          ✕
        </button>
      </div>

      <div className={contentVariants()}>
        <div className={nodeInfoVariants()}>
          <div
            className={colorBarVariants()}
            style={{ backgroundColor: "#22C55E" }}
          />
          <div className={nodeDetailsVariants()}>
            <span className={nodeTypeVariants()}>Workflow</span>
            <h3 className={nodeNameVariants()}>{workflowName}</h3>
          </div>
        </div>

        <div className={sectionVariants()}>
          <h4 className={sectionTitleVariants()}>Interface Inputs</h4>
          {workflow.interface.inputs.length === 0 ? (
            <p className={noInputsVariants()}>No inputs defined</p>
          ) : (
            <div className="flex flex-col gap-1.5 mb-2.5">
              {workflow.interface.inputs.map((input) => (
                <div key={input.name}>
                  {editingInput === input.name ? (
                    <div className="flex flex-col gap-1.5">
                      <input
                        type="text"
                        className={editInputVariants()}
                        placeholder="Input name"
                        value={editInputName}
                        onChange={(e) => setEditInputName(e.target.value)}
                      />
                      <div className="flex gap-1.5 items-center">
                        <select
                          className={cn(editInputVariants(), "flex-1")}
                          value={editInputType}
                          onChange={(e) =>
                            setEditInputType(e.target.value as InputType)
                          }
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
                            checked={editInputRequired}
                            onChange={(e) =>
                              setEditInputRequired(e.target.checked)
                            }
                          />
                          Required
                        </label>
                      </div>
                      <div className="flex gap-1.5">
                        <button
                          className={cn(actionBtnVariants(), "flex-1")}
                          onClick={handleSaveEditInput}
                        >
                          Save
                        </button>
                        <button
                          className={cn(actionBtnVariants(), "flex-1")}
                          onClick={handleCancelEditInput}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div
                      className={cn(
                        inputPreviewVariants({ editable: true }),
                        "cursor-pointer",
                      )}
                      onClick={() => handleStartEditInput(input)}
                    >
                      <span className="text-accent-blue font-mono font-medium">
                        {input.name}
                      </span>
                      <span className="text-xs px-1 py-0.5 rounded bg-surface-3 text-text-muted">
                        {input.type}
                      </span>
                      {input.required && (
                        <span
                          className="text-accent-red text-xs"
                          title="Required"
                        >
                          *
                        </span>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveInput(input.name);
                        }}
                        className="bg-transparent border-none text-accent-red cursor-pointer px-1 ml-auto text-xs"
                        title="Remove input"
                      >
                        ✕
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          <div className="flex flex-col gap-1.5">
            <div className="flex gap-1.5">
              <input
                type="text"
                className={cn(inputVariants(), "flex-1")}
                placeholder="Input name"
                value={newInputName}
                onChange={(e) => setNewInputName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddInput()}
              />
              <select
                className={cn(inputVariants(), "w-20")}
                value={newInputType}
                onChange={(e) => setNewInputType(e.target.value as InputType)}
              >
                {INPUT_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-1.5 items-center">
              <label className="flex items-center gap-1 text-xs text-text-secondary">
                <input
                  type="checkbox"
                  checked={newInputRequired}
                  onChange={(e) => setNewInputRequired(e.target.checked)}
                />
                Required
              </label>
              <button
                className={cn(actionBtnVariants(), "flex-none w-auto ml-auto")}
                onClick={handleAddInput}
              >
                Add
              </button>
            </div>
          </div>
        </div>

        <div className={sectionVariants()}>
          <h4 className={sectionTitleVariants()}>Interface Outputs</h4>
          {workflow.interface.outputs.length === 0 ? (
            <p className={noInputsVariants()}>No outputs defined</p>
          ) : (
            <div className="flex flex-wrap gap-1.5 mb-2.5">
              {workflow.interface.outputs.map((output) => (
                <span
                  key={output}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-surface-2 rounded text-sm text-accent-violet"
                >
                  {output}
                  <button
                    onClick={() => handleRemoveOutput(output)}
                    className="bg-transparent border-none text-text-muted cursor-pointer p-0 text-xs hover:text-text-primary"
                    title="Remove output"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          )}
          <div className="flex gap-1.5">
            <input
              type="text"
              className={cn(inputVariants(), "flex-1")}
              placeholder="New output name"
              value={newOutput}
              onChange={(e) => setNewOutput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddOutput()}
            />
            <button
              className={cn(actionBtnVariants(), "flex-none w-auto")}
              onClick={handleAddOutput}
            >
              Add
            </button>
          </div>
        </div>

        <div className={sectionVariants()}>
          <h4 className={sectionTitleVariants()}>Variables</h4>
          {varEntries.length === 0 ? (
            <p className={noInputsVariants()}>No variables defined</p>
          ) : (
            <div className="mb-2.5">
              {varEntries.map(([name, value]) => (
                <div key={name} className="mb-2">
                  {editingVar === name ? (
                    <div className="flex flex-col gap-1.5">
                      <input
                        type="text"
                        className={editInputVariants()}
                        placeholder="Variable name"
                        value={editVarName}
                        onChange={(e) => setEditVarName(e.target.value)}
                      />
                      <input
                        type="text"
                        className={editInputVariants()}
                        placeholder="Default value"
                        value={editVarValue}
                        onChange={(e) => setEditVarValue(e.target.value)}
                        onKeyDown={(e) =>
                          e.key === "Enter" && handleSaveEditVar()
                        }
                      />
                      <div className="flex gap-1.5">
                        <button
                          className={cn(actionBtnVariants(), "flex-1")}
                          onClick={handleSaveEditVar}
                        >
                          Save
                        </button>
                        <button
                          className={cn(actionBtnVariants(), "flex-1")}
                          onClick={handleCancelEditVar}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div
                      className={cn(
                        inputPreviewVariants({ editable: true }),
                        "cursor-pointer",
                      )}
                      onClick={() => handleStartEditVar(name, value)}
                    >
                      <span className="text-accent-green font-mono font-medium">
                        ${name}
                      </span>
                      <span className="text-text-muted">=</span>
                      <span className={valueContentVariants()}>
                        {formatValue(value)}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteVar(name);
                        }}
                        className="bg-transparent border-none text-accent-red cursor-pointer px-1 ml-auto text-xs"
                        title="Delete variable"
                      >
                        ✕
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          <div className="flex flex-col gap-1.5">
            <div className="flex gap-1.5">
              <input
                type="text"
                className={cn(inputVariants(), "flex-1")}
                placeholder="Variable name"
                value={newVarName}
                onChange={(e) => setNewVarName(e.target.value)}
              />
              <input
                type="text"
                className={cn(inputVariants(), "flex-1")}
                placeholder="Default value"
                value={newVarValue}
                onChange={(e) => setNewVarValue(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddVariable()}
              />
            </div>
            <button className={actionBtnVariants()} onClick={handleAddVariable}>
              Add Variable
            </button>
          </div>
        </div>

        {/* Delete Workflow (only for non-main workflows) */}
        {workflowName !== "main" && (
          <div className={sectionVariants()}>
            <h4 className={sectionTitleVariants()}>Danger Zone</h4>
            <button
              className="w-full px-3 py-2 text-sm font-medium bg-accent-red/10 text-accent-red border border-accent-red/30 rounded hover:bg-accent-red/20 transition-colors"
              onClick={handleDeleteWorkflow}
            >
              Delete Workflow
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function formatValue(value: unknown): string {
  if (value === null) return "null";
  if (value === undefined) return "";
  if (typeof value === "string") return value;
  return JSON.stringify(value);
}

function parseValue(str: string): unknown {
  if (!str || str === "") return "";
  if (str === "null") return null;
  if (str === "true") return true;
  if (str === "false") return false;

  try {
    return JSON.parse(str);
  } catch {
    return str;
  }
}
