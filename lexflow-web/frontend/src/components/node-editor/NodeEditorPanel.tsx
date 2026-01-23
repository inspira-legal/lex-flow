import { useState } from "react";
import { useWorkflowStore, useUiStore } from "../../store";
import type { SelectedReporter } from "../../store/uiStore";
import type { TreeNode, FormattedValue, NodeType } from "../../api/types";
import { StartNodeEditorPanel } from "./StartNodeEditorPanel";
import styles from "./NodeEditorPanel.module.css";

const NODE_TYPE_LABELS: Record<NodeType | string, string> = {
  control_flow: "Control Flow",
  data: "Data",
  io: "I/O",
  operator: "Operator",
  workflow_op: "Workflow",
  opcode: "Opcode",
};

const NODE_COLORS: Record<NodeType | string, string> = {
  control_flow: "#FF9500",
  data: "#4CAF50",
  io: "#22D3EE",
  operator: "#9C27B0",
  workflow_op: "#E91E63",
  opcode: "#64748B",
};

const REPORTER_COLORS: Record<string, string> = {
  data: "#4CAF50",
  operator: "#9C27B0",
  io: "#22D3EE",
  workflow: "#E91E63",
  default: "#64748B",
};

export function NodeEditorPanel() {
  const {
    tree,
    selectedNodeId,
    selectNode,
    source,
    opcodes,
    deleteNode,
    duplicateNode,
    updateNodeInput,
    updateReporterInput,
    deleteReporter,
  } = useWorkflowStore();
  const {
    closeNodeEditor,
    selectedReporter,
    selectReporter,
    selectedStartNode,
    selectStartNode,
  } = useUiStore();
  const [copied, setCopied] = useState(false);

  // Show start node editor if a start node is selected
  if (selectedStartNode) {
    return (
      <StartNodeEditorPanel
        workflowName={selectedStartNode}
        onClose={() => {
          selectStartNode(null);
          closeNodeEditor();
        }}
      />
    );
  }

  // Find the selected node in the tree
  const selectedNode = selectedNodeId ? findNode(tree, selectedNodeId) : null;

  // Find opcode info for node or reporter
  const opcodeInfo = selectedReporter
    ? opcodes.find((op) => op.name === selectedReporter.opcode)
    : selectedNode
      ? opcodes.find((op) => op.name === selectedNode.opcode)
      : null;

  const handleClose = () => {
    closeNodeEditor();
    selectNode(null);
    selectReporter(null);
  };

  const handleCopyId = () => {
    if (selectedNodeId) {
      navigator.clipboard.writeText(selectedNodeId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleCopyPath = () => {
    if (selectedReporter) {
      const path = `${selectedReporter.parentNodeId}.${selectedReporter.inputPath.join(".")}`;
      navigator.clipboard.writeText(path);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleFindInSource = () => {
    if (selectedNodeId) {
      // Find the line number in the source
      const lines = source.split("\n");
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes(selectedNodeId + ":")) {
          // Dispatch a custom event that the editor can listen to
          window.dispatchEvent(
            new CustomEvent("lexflow:goto-line", { detail: { line: i + 1 } }),
          );
          break;
        }
      }
    }
  };

  const handleDelete = () => {
    if (selectedNodeId && selectedNodeId !== "start") {
      if (
        confirm(
          `Delete node "${selectedNodeId}"? This action can be undone with Ctrl+Z.`,
        )
      ) {
        deleteNode(selectedNodeId);
        closeNodeEditor();
      }
    }
  };

  const handleDuplicate = () => {
    if (selectedNodeId && selectedNodeId !== "start") {
      duplicateNode(selectedNodeId);
    }
  };

  const handleBackToNode = () => {
    selectReporter(null);
  };

  const handleUpdateReporterInput = (inputKey: string, newValue: string) => {
    if (selectedReporter && selectedReporter.reporterNodeId) {
      const success = updateReporterInput(
        selectedReporter.reporterNodeId,
        inputKey,
        newValue,
      );
      if (success) {
        // Update the selected reporter state with the new value
        const updatedInputs = { ...selectedReporter.inputs };
        // Parse the new value to create the appropriate FormattedValue
        if (newValue.startsWith("$")) {
          updatedInputs[inputKey] = {
            type: "variable",
            name: newValue.slice(1),
          };
        } else {
          try {
            const parsed = JSON.parse(newValue);
            updatedInputs[inputKey] = { type: "literal", value: parsed };
          } catch {
            updatedInputs[inputKey] = { type: "literal", value: newValue };
          }
        }
        selectReporter({ ...selectedReporter, inputs: updatedInputs });
      }
    } else {
      console.warn("Cannot update reporter: no reporter node ID available");
    }
  };

  const handleDeleteReporter = () => {
    if (selectedReporter) {
      if (
        confirm(
          `Delete this reporter? It will be replaced with null. This action can be undone with Ctrl+Z.`,
        )
      ) {
        deleteReporter(
          selectedReporter.parentNodeId,
          selectedReporter.inputPath,
        );
        selectReporter(null);
      }
    }
  };

  const handleFindReporterInSource = () => {
    if (selectedReporter) {
      const lines = source.split("\n");

      // If we have the reporter node ID, find its definition directly
      if (selectedReporter.reporterNodeId) {
        for (let i = 0; i < lines.length; i++) {
          // Look for the node definition line (e.g., "  reporter_id:")
          if (
            lines[i].match(
              new RegExp(`^\\s+${selectedReporter.reporterNodeId}:\\s*$`),
            )
          ) {
            window.dispatchEvent(
              new CustomEvent("lexflow:goto-line", { detail: { line: i + 1 } }),
            );
            return;
          }
        }
      }

      // Fallback: find in parent node's inputs
      const pathKey =
        selectedReporter.inputPath[selectedReporter.inputPath.length - 1];
      let inParentNode = false;
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line.includes(selectedReporter.parentNodeId + ":")) {
          inParentNode = true;
        }
        if (inParentNode && line.includes(pathKey + ":")) {
          window.dispatchEvent(
            new CustomEvent("lexflow:goto-line", { detail: { line: i + 1 } }),
          );
          break;
        }
      }
    }
  };

  // Show reporter panel if a reporter is selected
  if (selectedReporter) {
    return (
      <ReporterPanel
        reporter={selectedReporter}
        parentNode={selectedNode}
        opcodeInfo={opcodeInfo}
        copied={copied}
        onCopyPath={handleCopyPath}
        onBackToNode={handleBackToNode}
        onClose={handleClose}
        onUpdateInput={handleUpdateReporterInput}
        onDelete={handleDeleteReporter}
        onFindInSource={handleFindReporterInSource}
      />
    );
  }

  if (!selectedNode) {
    return (
      <div className={styles.panel}>
        <div className={styles.header}>
          <span className={styles.title}>Node Editor</span>
          <button className={styles.closeBtn} onClick={handleClose}>
            ✕
          </button>
        </div>
        <div className={styles.empty}>
          <p>Select a node to edit</p>
        </div>
      </div>
    );
  }

  const color = NODE_COLORS[selectedNode.type] || NODE_COLORS.opcode;
  const typeLabel = NODE_TYPE_LABELS[selectedNode.type] || "Node";

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.title}>Node Editor</span>
        <button className={styles.closeBtn} onClick={handleClose}>
          ✕
        </button>
      </div>

      <div className={styles.content}>
        {/* Node info */}
        <div className={styles.nodeInfo}>
          <div className={styles.colorBar} style={{ backgroundColor: color }} />
          <div className={styles.nodeDetails}>
            <span className={styles.nodeType}>{typeLabel}</span>
            <h3 className={styles.nodeName}>
              {formatOpcodeName(selectedNode.opcode)}
            </h3>
            <button
              className={styles.nodeIdBtn}
              onClick={handleCopyId}
              title="Copy node ID"
            >
              {copied ? "✓ Copied!" : `ID: ${selectedNode.id}`}
            </button>
          </div>
        </div>

        {/* Opcode description */}
        {opcodeInfo?.description && (
          <div className={styles.description}>{opcodeInfo.description}</div>
        )}

        {/* Opcode */}
        <div className={styles.field}>
          <label>Opcode</label>
          <input
            type="text"
            value={selectedNode.opcode}
            readOnly
            className={styles.input}
          />
        </div>

        {/* Inputs */}
        <div className={styles.section}>
          <h4>Inputs</h4>
          {Object.entries(selectedNode.inputs).length === 0 ? (
            <p className={styles.noInputs}>No inputs</p>
          ) : (
            Object.entries(selectedNode.inputs).map(([key, value]) => (
              <InputField
                key={key}
                name={key}
                value={value}
                paramInfo={opcodeInfo?.parameters.find(
                  (p) => p.name.toUpperCase() === key,
                )}
                onUpdate={(inputKey, newValue) =>
                  updateNodeInput(selectedNodeId!, inputKey, newValue)
                }
              />
            ))
          )}
        </div>

        {/* Expected parameters (from opcode definition) */}
        {opcodeInfo && opcodeInfo.parameters.length > 0 && (
          <div className={styles.section}>
            <h4>Parameters</h4>
            <div className={styles.paramList}>
              {opcodeInfo.parameters.map((param) => (
                <div key={param.name} className={styles.paramItem}>
                  <span className={styles.paramName}>
                    {param.name}
                    {!param.required && (
                      <span className={styles.optional}>?</span>
                    )}
                  </span>
                  <span className={styles.paramType}>{param.type}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Branches */}
        {selectedNode.children.length > 0 && (
          <div className={styles.section}>
            <h4>Branches</h4>
            {selectedNode.children.map((branch, i) => (
              <div key={i} className={styles.branch}>
                <span className={styles.branchName}>{branch.name}</span>
                <span className={styles.branchCount}>
                  {branch.children.length} node(s)
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className={styles.actions}>
        <button className={styles.actionBtn} onClick={handleFindInSource}>
          Find in Source
        </button>
        <button
          className={styles.actionBtn}
          onClick={handleDuplicate}
          disabled={selectedNodeId === "start"}
          title={
            selectedNodeId === "start"
              ? "Cannot duplicate start node"
              : "Duplicate node (Ctrl+D)"
          }
        >
          Duplicate
        </button>
        <button
          className={styles.actionBtnDanger}
          onClick={handleDelete}
          disabled={selectedNodeId === "start"}
          title={
            selectedNodeId === "start"
              ? "Cannot delete start node"
              : "Delete node (Del)"
          }
        >
          Delete
        </button>
      </div>
    </div>
  );
}

// Reporter Panel Component
interface ReporterPanelProps {
  reporter: SelectedReporter;
  parentNode: TreeNode | null;
  opcodeInfo:
    | {
        name: string;
        description?: string;
        parameters: Array<{ name: string; type: string; required: boolean }>;
      }
    | null
    | undefined;
  copied: boolean;
  onCopyPath: () => void;
  onBackToNode: () => void;
  onClose: () => void;
  onUpdateInput: (inputKey: string, newValue: string) => void;
  onDelete: () => void;
  onFindInSource: () => void;
}

function ReporterPanel({
  reporter,
  parentNode,
  opcodeInfo,
  copied,
  onCopyPath,
  onBackToNode,
  onClose,
  onUpdateInput,
  onDelete,
  onFindInSource,
}: ReporterPanelProps) {
  const color = getReporterColor(reporter.opcode);
  const typeLabel = getReporterTypeLabel(reporter.opcode);

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.title}>Reporter Editor</span>
        <button className={styles.closeBtn} onClick={onClose}>
          ✕
        </button>
      </div>

      <div className={styles.content}>
        {/* Back button */}
        {parentNode && (
          <button className={styles.backBtn} onClick={onBackToNode}>
            ← Back to {parentNode.id}
          </button>
        )}

        {/* Reporter info */}
        <div className={styles.nodeInfo}>
          <div className={styles.colorBar} style={{ backgroundColor: color }} />
          <div className={styles.nodeDetails}>
            <span className={styles.nodeType}>{typeLabel}</span>
            <h3 className={styles.nodeName}>
              {formatOpcodeName(reporter.opcode)}
            </h3>
            <button
              className={styles.nodeIdBtn}
              onClick={onCopyPath}
              title="Copy reporter path"
            >
              {copied ? "✓ Copied!" : `Path: ${reporter.inputPath.join(".")}`}
            </button>
          </div>
        </div>

        {/* Opcode description */}
        {opcodeInfo?.description && (
          <div className={styles.description}>{opcodeInfo.description}</div>
        )}

        {/* Parent info */}
        <div className={styles.field}>
          <label>Parent Node</label>
          <input
            type="text"
            value={reporter.parentNodeId}
            readOnly
            className={styles.input}
          />
        </div>

        {/* Opcode */}
        <div className={styles.field}>
          <label>Opcode</label>
          <input
            type="text"
            value={reporter.opcode}
            readOnly
            className={styles.input}
          />
        </div>

        {/* Inputs */}
        <div className={styles.section}>
          <h4>Inputs</h4>
          {Object.entries(reporter.inputs).length === 0 ? (
            <p className={styles.noInputs}>No inputs</p>
          ) : (
            Object.entries(reporter.inputs).map(([key, value]) => (
              <InputField
                key={key}
                name={key}
                value={value}
                paramInfo={opcodeInfo?.parameters.find(
                  (p) => p.name.toUpperCase() === key,
                )}
                onUpdate={onUpdateInput}
              />
            ))
          )}
        </div>

        {/* Expected parameters (from opcode definition) */}
        {opcodeInfo && opcodeInfo.parameters.length > 0 && (
          <div className={styles.section}>
            <h4>Parameters</h4>
            <div className={styles.paramList}>
              {opcodeInfo.parameters.map((param) => (
                <div key={param.name} className={styles.paramItem}>
                  <span className={styles.paramName}>
                    {param.name}
                    {!param.required && (
                      <span className={styles.optional}>?</span>
                    )}
                  </span>
                  <span className={styles.paramType}>{param.type}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className={styles.actions}>
        <button className={styles.actionBtn} onClick={onFindInSource}>
          Find in Source
        </button>
        <button
          className={styles.actionBtnDanger}
          onClick={onDelete}
          title="Delete reporter (replace with null)"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

interface InputFieldProps {
  name: string;
  value: FormattedValue;
  paramInfo?: { name: string; type: string; required: boolean };
  onUpdate?: (inputKey: string, newValue: string) => void;
}

function InputField({ name, value, paramInfo, onUpdate }: InputFieldProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState("");

  const displayValue = formatValue(value);

  const getEditableValue = (val: FormattedValue): string => {
    switch (val.type) {
      case "literal":
        if (typeof val.value === "string") return val.value;
        return JSON.stringify(val.value);
      case "variable":
        return `$${val.name}`;
      default:
        return displayValue;
    }
  };

  const handleStartEdit = () => {
    // Only allow editing literals and variables
    if (value.type === "literal" || value.type === "variable") {
      setEditValue(getEditableValue(value));
      setIsEditing(true);
    }
  };

  const handleSave = () => {
    if (onUpdate && editValue !== getEditableValue(value)) {
      onUpdate(name, editValue);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSave();
    } else if (e.key === "Escape") {
      setIsEditing(false);
    }
  };

  const isEditable = value.type === "literal" || value.type === "variable";

  return (
    <div className={styles.field}>
      <label>
        {name}
        {paramInfo && (
          <span className={styles.inputType}>{paramInfo.type}</span>
        )}
      </label>
      {isEditing ? (
        <input
          type="text"
          className={styles.editInput}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={handleSave}
          onKeyDown={handleKeyDown}
          autoFocus
        />
      ) : (
        <div
          className={`${styles.inputPreview} ${isEditable ? styles.editable : ""}`}
          onClick={handleStartEdit}
          title={isEditable ? "Click to edit" : undefined}
        >
          <span className={styles.valueType}>{value.type}</span>
          <span className={styles.valueContent}>{displayValue}</span>
          {isEditable && <span className={styles.editHint}>Click to edit</span>}
        </div>
      )}
    </div>
  );
}

function formatValue(value: FormattedValue): string {
  switch (value.type) {
    case "literal":
      if (typeof value.value === "string") return `"${value.value}"`;
      if (typeof value.value === "object" && value.value !== null) {
        return JSON.stringify(value.value, null, 2);
      }
      return String(value.value);
    case "variable":
      return `$${value.name}`;
    case "reporter":
      return `${formatOpcodeName(value.opcode || "")}(...)`;
    case "workflow_call":
      return `→ ${value.name}`;
    case "branch":
      return `→ ${value.target}`;
    case "dict":
      return JSON.stringify(value.value, null, 2);
    case "truncated":
      return value.display || "...";
    default:
      return "?";
  }
}

function formatOpcodeName(opcode: string): string {
  return opcode
    .replace(/^(control_|data_|io_|operator_|workflow_)/, "")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getReporterColor(opcode: string): string {
  if (opcode.startsWith("data_")) return REPORTER_COLORS.data;
  if (opcode.startsWith("operator_")) return REPORTER_COLORS.operator;
  if (opcode.startsWith("io_")) return REPORTER_COLORS.io;
  if (opcode.startsWith("workflow_")) return REPORTER_COLORS.workflow;
  return REPORTER_COLORS.default;
}

function getReporterTypeLabel(opcode: string): string {
  if (opcode.startsWith("data_")) return "Data Reporter";
  if (opcode.startsWith("operator_")) return "Operator Reporter";
  if (opcode.startsWith("io_")) return "I/O Reporter";
  if (opcode.startsWith("workflow_")) return "Workflow Reporter";
  return "Reporter";
}

function findNode(tree: any, nodeId: string): TreeNode | null {
  if (!tree) return null;

  function searchNodes(nodes: TreeNode[]): TreeNode | null {
    for (const node of nodes) {
      if (node.id === nodeId) return node;
      if (node.children) {
        for (const branch of node.children) {
          const found = searchNodes(branch.children);
          if (found) return found;
        }
      }
    }
    return null;
  }

  for (const workflow of tree.workflows || []) {
    const found = searchNodes(workflow.children || []);
    if (found) return found;

    // Search orphans
    const orphanFound = searchNodes(workflow.orphans || []);
    if (orphanFound) return orphanFound;
  }

  return null;
}
