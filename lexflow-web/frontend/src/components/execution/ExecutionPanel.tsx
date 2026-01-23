import { useRef, useEffect, useState, useCallback } from "react";
import { useWorkflowStore, useUiStore, useExecutionStore } from "../../store";
import { useWebSocketExecution } from "../../hooks";
import { PromptOverlay } from "./PromptOverlay";
import type { RenderedContent, AlertItem } from "../../store/executionStore";
import styles from "./ExecutionPanel.module.css";

const MIN_HEIGHT = 100;
const MAX_HEIGHT = 600;
const DEFAULT_HEIGHT = 250;

export function ExecutionPanel() {
  const { source, tree } = useWorkflowStore();
  const {
    isExecuting,
    executionOutput,
    executionResult,
    executionError,
    workflowInputs,
    pendingPrompt,
    renderedContent,
    alerts,
    progress,
    removeAlert,
  } = useExecutionStore();
  const { toggleExecutionPanel } = useUiStore();
  const { execute, cancel, respondToPrompt } = useWebSocketExecution();
  const outputRef = useRef<HTMLPreElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  // Resize state
  const [height, setHeight] = useState(DEFAULT_HEIGHT);
  const [isResizing, setIsResizing] = useState(false);

  // Pane visibility state
  const [showPreview, setShowPreview] = useState(true);
  const [showConsole, setShowConsole] = useState(true);

  // Auto-scroll output to bottom
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [executionOutput]);

  // Auto-dismiss alerts after 5 seconds
  useEffect(() => {
    if (alerts.length > 0) {
      const timer = setTimeout(() => {
        removeAlert(alerts[0].id);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [alerts, removeAlert]);

  // Resize handlers
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!panelRef.current) return;
      const container = panelRef.current.parentElement;
      if (!container) return;

      const containerRect = container.getBoundingClientRect();
      const newHeight = containerRect.bottom - e.clientY;
      setHeight(Math.min(MAX_HEIGHT, Math.max(MIN_HEIGHT, newHeight)));
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing]);

  const handleRun = () => {
    execute(source, workflowInputs);
  };

  const handleCancel = () => {
    cancel();
  };

  const inputs = tree?.interface?.inputs || [];

  return (
    <div
      ref={panelRef}
      className={styles.panel}
      style={{ height: `${height}px` }}
    >
      {/* Resize handle */}
      <div
        className={`${styles.resizeHandle} ${isResizing ? styles.resizing : ""}`}
        onMouseDown={handleMouseDown}
      />

      <div className={styles.header}>
        <span className={styles.title}>Execution</span>
        <div className={styles.actions}>
          {/* Pane toggles */}
          <button
            className={`${styles.toggleBtn} ${showPreview ? styles.active : ""}`}
            onClick={() => setShowPreview(!showPreview)}
            title="Toggle Preview"
          >
            Preview
          </button>
          <button
            className={`${styles.toggleBtn} ${showConsole ? styles.active : ""}`}
            onClick={() => setShowConsole(!showConsole)}
            title="Toggle Console"
          >
            Console
          </button>
          <div className={styles.separator} />
          {isExecuting ? (
            <button className={styles.cancelBtn} onClick={handleCancel}>
              Stop
            </button>
          ) : (
            <button className={styles.runBtn} onClick={handleRun}>
              Run
            </button>
          )}
          <button className={styles.iconBtn} onClick={toggleExecutionPanel}>
            ✕
          </button>
        </div>
      </div>

      {/* Inputs row */}
      {inputs.length > 0 && (
        <div className={styles.inputsRow}>
          <span className={styles.label}>Inputs:</span>
          {inputs.map((input) => (
            <InputField key={input} name={input} />
          ))}
        </div>
      )}

      {/* Progress bar */}
      {progress && (
        <div className={styles.progressContainer}>
          <div className={styles.progressBar}>
            <div
              className={styles.progressFill}
              style={{ width: `${(progress.value / progress.max) * 100}%` }}
            />
          </div>
          {progress.label && (
            <span className={styles.progressLabel}>{progress.label}</span>
          )}
        </div>
      )}

      {/* Split panes */}
      <div className={styles.panes}>
        {/* Preview pane */}
        {showPreview && (
          <div className={styles.previewPane}>
            <div className={styles.paneHeader}>
              <span>Preview</span>
            </div>
            <div className={styles.paneContent}>
              {renderedContent.length > 0 ? (
                renderedContent.map((item, i) => (
                  <RenderItem key={i} item={item} />
                ))
              ) : (
                <div className={styles.placeholder}>
                  No preview content
                </div>
              )}
            </div>
          </div>
        )}

        {/* Resizer between panes */}
        {showPreview && showConsole && <div className={styles.paneResizer} />}

        {/* Console pane */}
        {showConsole && (
          <div className={styles.consolePane}>
            <div className={styles.paneHeader}>
              <span>Console</span>
            </div>
            <div className={styles.paneContent}>
              {executionError ? (
                <div className={styles.error}>{executionError}</div>
              ) : (
                <>
                  {executionOutput && (
                    <pre ref={outputRef} className={styles.outputText}>
                      {executionOutput}
                      {isExecuting && <span className={styles.cursor}>|</span>}
                    </pre>
                  )}
                  {executionResult !== null && !isExecuting && (
                    <div className={styles.result}>
                      <span className={styles.resultLabel}>Result:</span>
                      <code>{JSON.stringify(executionResult, null, 2)}</code>
                    </div>
                  )}
                  {!executionOutput && !executionResult && !isExecuting && (
                    <div className={styles.placeholder}>
                      Click "Run" to execute the workflow
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {/* Empty state when both panes hidden */}
        {!showPreview && !showConsole && (
          <div className={styles.emptyState}>
            Toggle Preview or Console to view execution output
          </div>
        )}
      </div>

      {/* Alerts - outside content div to avoid overflow:hidden clipping */}
      {alerts.length > 0 && (
        <div className={styles.alertsContainer}>
          {alerts.map((alert) => (
            <AlertBox
              key={alert.id}
              alert={alert}
              onDismiss={() => removeAlert(alert.id)}
            />
          ))}
        </div>
      )}

      {/* Prompt overlay */}
      {pendingPrompt && (
        <PromptOverlay prompt={pendingPrompt} onSubmit={respondToPrompt} />
      )}
    </div>
  );
}

function InputField({ name }: { name: string }) {
  const { workflowInputs, setWorkflowInput } = useExecutionStore();
  const value = workflowInputs[name] ?? "";

  return (
    <div className={styles.inputField}>
      <label>{name}:</label>
      <input
        type="text"
        value={String(value)}
        onChange={(e) => {
          // Try to parse as JSON, fall back to string
          const raw = e.target.value;
          try {
            setWorkflowInput(name, JSON.parse(raw));
          } catch {
            setWorkflowInput(name, raw);
          }
        }}
        placeholder={`Enter ${name}`}
      />
    </div>
  );
}

function RenderItem({ item }: { item: RenderedContent }) {
  switch (item.type) {
    case "html":
      return (
        <div
          className={styles.htmlContent}
          dangerouslySetInnerHTML={{ __html: item.content as string }}
        />
      );

    case "markdown":
      return (
        <div className={styles.markdownContent}>
          <MarkdownRenderer content={item.content as string} />
        </div>
      );

    case "table":
      const data = item.content as Record<string, unknown>[];
      if (!data.length) return null;
      const headers = Object.keys(data[0]);
      return (
        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                {headers.map((h) => (
                  <th key={h}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i}>
                  {headers.map((h) => (
                    <td key={h}>{String(row[h] ?? "")}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );

    case "image":
      const img = item.content as { src: string; alt: string };
      return (
        <div className={styles.imageContainer}>
          <img src={img.src} alt={img.alt} className={styles.image} />
        </div>
      );

    default:
      return null;
  }
}

function MarkdownRenderer({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("### ")) {
      elements.push(<h3 key={i}>{line.slice(4)}</h3>);
    } else if (line.startsWith("## ")) {
      elements.push(<h2 key={i}>{line.slice(3)}</h2>);
    } else if (line.startsWith("# ")) {
      elements.push(<h1 key={i}>{line.slice(2)}</h1>);
    } else if (line.trim()) {
      const processed = line
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/`(.+?)`/g, "<code>$1</code>");
      elements.push(
        <p key={i} dangerouslySetInnerHTML={{ __html: processed }} />,
      );
    } else {
      elements.push(<br key={i} />);
    }
  }

  return <>{elements}</>;
}

function AlertBox({
  alert,
  onDismiss,
}: {
  alert: AlertItem;
  onDismiss: () => void;
}) {
  const variantClass = styles[`alert${capitalize(alert.variant)}`] || "";

  return (
    <div className={`${styles.alert} ${variantClass}`}>
      <span>{alert.message}</span>
      <button className={styles.alertDismiss} onClick={onDismiss}>
        X
      </button>
    </div>
  );
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
