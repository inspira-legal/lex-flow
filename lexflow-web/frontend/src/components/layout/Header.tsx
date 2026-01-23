import { useRef } from "react";
import { useWorkflowStore, useUiStore } from "../../store";
import { api } from "../../api";
import styles from "./Header.module.css";

const DEFAULT_WORKFLOW = `workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        next: hello
      hello:
        opcode: io_print
        inputs:
          MESSAGE: { literal: "Hello, LexFlow!" }
`;

export function Header() {
  const { source, setSource, undo, redo, canUndo, canRedo } =
    useWorkflowStore();
  const { togglePalette, toggleEditor, isEditorOpen } = useUiStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleNew = () => {
    if (source !== DEFAULT_WORKFLOW) {
      if (confirm("Create a new workflow? Unsaved changes will be lost.")) {
        setSource(DEFAULT_WORKFLOW);
      }
    }
  };

  const handleExport = () => {
    const blob = new Blob([source], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "workflow.yaml";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setSource(content);
    };
    reader.readAsText(file);

    // Reset input so same file can be selected again
    e.target.value = "";
  };

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <h1 className={styles.logo}>LexFlow</h1>
        <div className={styles.divider} />
        <button
          className={styles.iconBtn}
          onClick={handleNew}
          title="New Workflow"
        >
          <FileIcon />
        </button>
        <button
          className={styles.iconBtn}
          onClick={handleImport}
          title="Import Workflow"
        >
          <UploadIcon />
        </button>
        <button
          className={styles.iconBtn}
          onClick={handleExport}
          title="Export Workflow"
        >
          <DownloadIcon />
        </button>
        <div className={styles.divider} />
        <button
          className={styles.iconBtn}
          onClick={undo}
          disabled={!canUndo}
          title="Undo (Ctrl+Z)"
        >
          <UndoIcon />
        </button>
        <button
          className={styles.iconBtn}
          onClick={redo}
          disabled={!canRedo}
          title="Redo (Ctrl+Y)"
        >
          <RedoIcon />
        </button>
        <div className={styles.divider} />
        <button
          className={styles.iconBtn}
          onClick={togglePalette}
          title="Node Palette (Ctrl+P)"
        >
          <PlusIcon />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".yaml,.yml,.json"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
      </div>

      <div className={styles.center}>
        <ExamplesDropdown />
      </div>

      <div className={styles.right}>
        <button
          className={`${styles.iconBtn} ${isEditorOpen ? styles.active : ""}`}
          onClick={toggleEditor}
          title="Toggle Editor (Ctrl+B)"
        >
          <CodeIcon />
        </button>
      </div>
    </header>
  );
}

function ExamplesDropdown() {
  const { examples, setSource } = useWorkflowStore();

  const handleSelect = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const path = e.target.value;
    if (!path) return;
    try {
      const example = await api.getExample(path);
      setSource(example.content);
    } catch (err) {
      console.error("Failed to load example:", err);
    }
    // Reset select
    e.target.value = "";
  };

  const grouped = examples.reduce(
    (acc, ex) => {
      if (!acc[ex.category]) acc[ex.category] = [];
      acc[ex.category].push(ex);
      return acc;
    },
    {} as Record<string, typeof examples>,
  );

  return (
    <select className={styles.select} onChange={handleSelect} defaultValue="">
      <option value="">Load Example...</option>
      {Object.entries(grouped).map(([category, items]) => (
        <optgroup key={category} label={category}>
          {items.map((ex) => (
            <option key={ex.path} value={ex.path}>
              {ex.name}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );
}

function FileIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

function DownloadIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

function UndoIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M3 7v6h6" />
      <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
    </svg>
  );
}

function RedoIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M21 7v6h-6" />
      <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

function CodeIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M16 18l6-6-6-6M8 6l-6 6 6 6" />
    </svg>
  );
}
