import { useState } from "react";
import { useWorkflowStore, useSelectionStore } from "../../store";
import type { WorkflowNode } from "../../api/types";
import styles from "./NodeEditorPanel.module.css";

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
  } = useWorkflowStore();
  const { selectStartNode } = useSelectionStore();

  // Find the workflow
  const workflow = tree?.workflows.find((w) => w.name === workflowName) as
    | WorkflowNode
    | undefined;

  const [newVarName, setNewVarName] = useState("");
  const [newVarValue, setNewVarValue] = useState("");
  const [editingVar, setEditingVar] = useState<string | null>(null);
  const [editVarName, setEditVarName] = useState("");
  const [editVarValue, setEditVarValue] = useState("");

  const [newInput, setNewInput] = useState("");
  const [newOutput, setNewOutput] = useState("");

  if (!workflow) {
    return (
      <div className={styles.panel}>
        <div className={styles.header}>
          <span className={styles.title}>Start Node</span>
          <button className={styles.closeBtn} onClick={onClose}>
            ✕
          </button>
        </div>
        <div className={styles.empty}>
          <p>Workflow not found</p>
        </div>
      </div>
    );
  }

  const handleClose = () => {
    selectStartNode(null);
    onClose();
  };

  // Variable operations
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
    if (confirm(`Delete variable "$${name}"?`)) {
      deleteVariable(workflowName, name);
    }
  };

  // Interface operations
  const handleAddInput = () => {
    if (!newInput.trim()) return;
    const newInputs = [...workflow.interface.inputs, newInput.trim()];
    if (
      updateWorkflowInterface(
        workflowName,
        newInputs,
        workflow.interface.outputs,
      )
    ) {
      setNewInput("");
    }
  };

  const handleRemoveInput = (input: string) => {
    const newInputs = workflow.interface.inputs.filter((i) => i !== input);
    updateWorkflowInterface(
      workflowName,
      newInputs,
      workflow.interface.outputs,
    );
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
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.title}>Start Node</span>
        <button className={styles.closeBtn} onClick={handleClose}>
          ✕
        </button>
      </div>

      <div className={styles.content}>
        {/* Workflow info */}
        <div className={styles.nodeInfo}>
          <div
            className={styles.colorBar}
            style={{ backgroundColor: "#22C55E" }}
          />
          <div className={styles.nodeDetails}>
            <span className={styles.nodeType}>Workflow</span>
            <h3 className={styles.nodeName}>{workflowName}</h3>
          </div>
        </div>

        {/* Interface Inputs */}
        <div className={styles.section}>
          <h4>Interface Inputs</h4>
          {workflow.interface.inputs.length === 0 ? (
            <p className={styles.noInputs}>No inputs defined</p>
          ) : (
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "6px",
                marginBottom: "10px",
              }}
            >
              {workflow.interface.inputs.map((input) => (
                <span
                  key={input}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                    padding: "4px 8px",
                    background: "var(--bg-secondary)",
                    borderRadius: "4px",
                    fontSize: "0.85rem",
                    color: "var(--color-cyan)",
                  }}
                >
                  {input}
                  <button
                    onClick={() => handleRemoveInput(input)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--text-muted)",
                      cursor: "pointer",
                      padding: "0 2px",
                      fontSize: "0.8rem",
                    }}
                    title="Remove input"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          )}
          <div style={{ display: "flex", gap: "6px" }}>
            <input
              type="text"
              className={styles.input}
              placeholder="New input name"
              value={newInput}
              onChange={(e) => setNewInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddInput()}
              style={{ flex: 1 }}
            />
            <button
              className={styles.actionBtn}
              onClick={handleAddInput}
              style={{ flex: "none", width: "auto" }}
            >
              Add
            </button>
          </div>
        </div>

        {/* Interface Outputs */}
        <div className={styles.section}>
          <h4>Interface Outputs</h4>
          {workflow.interface.outputs.length === 0 ? (
            <p className={styles.noInputs}>No outputs defined</p>
          ) : (
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "6px",
                marginBottom: "10px",
              }}
            >
              {workflow.interface.outputs.map((output) => (
                <span
                  key={output}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "4px",
                    padding: "4px 8px",
                    background: "var(--bg-secondary)",
                    borderRadius: "4px",
                    fontSize: "0.85rem",
                    color: "var(--color-magenta)",
                  }}
                >
                  {output}
                  <button
                    onClick={() => handleRemoveOutput(output)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--text-muted)",
                      cursor: "pointer",
                      padding: "0 2px",
                      fontSize: "0.8rem",
                    }}
                    title="Remove output"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          )}
          <div style={{ display: "flex", gap: "6px" }}>
            <input
              type="text"
              className={styles.input}
              placeholder="New output name"
              value={newOutput}
              onChange={(e) => setNewOutput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddOutput()}
              style={{ flex: 1 }}
            />
            <button
              className={styles.actionBtn}
              onClick={handleAddOutput}
              style={{ flex: "none", width: "auto" }}
            >
              Add
            </button>
          </div>
        </div>

        {/* Variables */}
        <div className={styles.section}>
          <h4>Variables</h4>
          {varEntries.length === 0 ? (
            <p className={styles.noInputs}>No variables defined</p>
          ) : (
            <div style={{ marginBottom: "10px" }}>
              {varEntries.map(([name, value]) => (
                <div key={name} style={{ marginBottom: "8px" }}>
                  {editingVar === name ? (
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "6px",
                      }}
                    >
                      <input
                        type="text"
                        className={styles.editInput}
                        placeholder="Variable name"
                        value={editVarName}
                        onChange={(e) => setEditVarName(e.target.value)}
                      />
                      <input
                        type="text"
                        className={styles.editInput}
                        placeholder="Default value"
                        value={editVarValue}
                        onChange={(e) => setEditVarValue(e.target.value)}
                        onKeyDown={(e) =>
                          e.key === "Enter" && handleSaveEditVar()
                        }
                      />
                      <div style={{ display: "flex", gap: "6px" }}>
                        <button
                          className={styles.actionBtn}
                          onClick={handleSaveEditVar}
                          style={{ flex: 1 }}
                        >
                          Save
                        </button>
                        <button
                          className={styles.actionBtn}
                          onClick={handleCancelEditVar}
                          style={{ flex: 1 }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div
                      className={`${styles.inputPreview} ${styles.editable}`}
                      onClick={() => handleStartEditVar(name, value)}
                      style={{ cursor: "pointer" }}
                    >
                      <span
                        style={{
                          color: "#4ADE80",
                          fontFamily: "'JetBrains Mono', monospace",
                          fontWeight: 500,
                        }}
                      >
                        ${name}
                      </span>
                      <span style={{ color: "var(--text-muted)" }}>=</span>
                      <span className={styles.valueContent}>
                        {formatValue(value)}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteVar(name);
                        }}
                        style={{
                          background: "none",
                          border: "none",
                          color: "var(--color-red)",
                          cursor: "pointer",
                          padding: "0 4px",
                          marginLeft: "auto",
                          fontSize: "0.8rem",
                        }}
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
          <div style={{ display: "flex", gap: "6px", flexDirection: "column" }}>
            <div style={{ display: "flex", gap: "6px" }}>
              <input
                type="text"
                className={styles.input}
                placeholder="Variable name"
                value={newVarName}
                onChange={(e) => setNewVarName(e.target.value)}
                style={{ flex: 1 }}
              />
              <input
                type="text"
                className={styles.input}
                placeholder="Default value"
                value={newVarValue}
                onChange={(e) => setNewVarValue(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddVariable()}
                style={{ flex: 1 }}
              />
            </div>
            <button className={styles.actionBtn} onClick={handleAddVariable}>
              Add Variable
            </button>
          </div>
        </div>
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

  // Try to parse as JSON (for numbers, arrays, objects)
  try {
    return JSON.parse(str);
  } catch {
    // Return as string if not valid JSON
    return str;
  }
}
