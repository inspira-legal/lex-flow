import { useRef, useEffect, useState, useCallback } from "react";
import { useWorkflowStore, useUiStore, useExecutionStore } from "@/store";
import { useWebSocketExecution } from "@/hooks";
import { PromptOverlay } from "../PromptOverlay";
import { cn } from "@/lib/cn";
import {
  PlayIcon,
  StopIcon,
  StepForwardIcon,
  TrashIcon,
  CloseIcon,
} from "@/components/icons";
import type { RenderedContent, AlertItem } from "@/store/executionStore";
import type { DetailedInput } from "@/api/types";
import {
  panelVariants,
  resizeHandleVariants,
  headerVariants,
  titleGroupVariants,
  titleVariants,
  statusDotVariants,
  actionsVariants,
  separatorVariants,
  toggleBtnVariants,
  runBtnVariants,
  cancelBtnVariants,
  iconBtnVariants,
  closeBtnVariants,
  inputsRowVariants,
  labelVariants,
  inputFieldVariants,
  inputFieldLabelVariants,
  inputFieldInputVariants,
  progressContainerVariants,
  progressBarVariants,
  progressFillVariants,
  progressLabelVariants,
  panesVariants,
  paneVariants,
  paneHeaderVariants,
  paneContentVariants,
  paneResizerVariants,
  emptyStateVariants,
  placeholderVariants,
  outputTextVariants,
  errorVariants,
  resultVariants,
  resultLabelVariants,
  resultCodeVariants,
  cursorVariants,
  alertsContainerVariants,
  alertVariants,
  alertDismissVariants,
  htmlContentVariants,
  markdownContentVariants,
  tableContainerVariants,
  tableVariants,
  tableHeaderVariants,
  tableCellVariants,
  imageContainerVariants,
  imageVariants,
} from "./styles";
import type { ExecutionPanelProps } from "./types";

const MIN_HEIGHT = 100;
const MAX_HEIGHT = 600;
const DEFAULT_HEIGHT = 250;

export function ExecutionPanel({ className }: ExecutionPanelProps) {
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
    clearWorkflowInputs,
  } = useExecutionStore();
  const { toggleExecutionPanel } = useUiStore();
  const { execute, cancel, respondToPrompt } = useWebSocketExecution();
  const outputRef = useRef<HTMLPreElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  const [height, setHeight] = useState(DEFAULT_HEIGHT);
  const [isResizing, setIsResizing] = useState(false);
  const [showPreview, setShowPreview] = useState(true);
  const [showConsole, setShowConsole] = useState(true);

  // Get workflow inputs interface
  const inputs: DetailedInput[] = tree?.interface?.inputs || [];
  const inputsKey = JSON.stringify(inputs.map((i) => i.name));

  // Clear workflow inputs when interface changes (e.g., switching examples)
  useEffect(() => {
    clearWorkflowInputs();
  }, [inputsKey, clearWorkflowInputs]);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [executionOutput]);

  useEffect(() => {
    if (alerts.length > 0) {
      const timer = setTimeout(() => {
        removeAlert(alerts[0].id);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [alerts, removeAlert]);

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
    // Filter inputs to only include those defined in current workflow
    const validInputs: Record<string, unknown> = {};
    for (const input of inputs) {
      if (input.name in workflowInputs) {
        validInputs[input.name] = workflowInputs[input.name];
      }
    }
    execute(
      source,
      Object.keys(validInputs).length > 0 ? validInputs : undefined,
    );
  };

  const handleCancel = () => {
    cancel();
  };

  return (
    <div
      ref={panelRef}
      className={cn(panelVariants(), className)}
      style={{ height: `${height}px` }}
    >
      <div
        className={resizeHandleVariants({ isResizing })}
        onMouseDown={handleMouseDown}
      />

      <div className={headerVariants()}>
        <div className={titleGroupVariants()}>
          <span className={titleVariants()}>Execution</span>
          <span
            className={statusDotVariants({
              status: isExecuting
                ? "running"
                : executionError
                  ? "error"
                  : "idle",
            })}
          />
        </div>
        <div className={actionsVariants()}>
          <button
            className={toggleBtnVariants({ active: showPreview })}
            onClick={() => setShowPreview(!showPreview)}
            title="Toggle Preview"
          >
            Preview
          </button>
          <button
            className={toggleBtnVariants({ active: showConsole })}
            onClick={() => setShowConsole(!showConsole)}
            title="Toggle Console"
          >
            Console
          </button>
          <div className={separatorVariants()} />
          {isExecuting ? (
            <button className={cancelBtnVariants()} onClick={handleCancel}>
              <StopIcon />
              Stop
            </button>
          ) : (
            <button className={runBtnVariants()} onClick={handleRun}>
              <PlayIcon />
              Run
            </button>
          )}
          <button
            className={iconBtnVariants()}
            title="Step forward (coming soon)"
            disabled
          >
            <StepForwardIcon />
          </button>
          <button
            className={iconBtnVariants()}
            onClick={() => useExecutionStore.getState().clearExecution()}
            title="Clear output"
          >
            <TrashIcon />
          </button>
          <div className={separatorVariants()} />
          <button
            className={closeBtnVariants()}
            onClick={toggleExecutionPanel}
            title="Close panel"
          >
            <CloseIcon />
          </button>
        </div>
      </div>

      {inputs.length > 0 && (
        <div className={inputsRowVariants()}>
          <span className={labelVariants()}>Inputs:</span>
          {inputs.map((input) => (
            <TypedInputField key={input.name} input={input} />
          ))}
        </div>
      )}

      {progress && (
        <div className={progressContainerVariants()}>
          <div className={progressBarVariants()}>
            <div
              className={progressFillVariants()}
              style={{ width: `${(progress.value / progress.max) * 100}%` }}
            />
          </div>
          {progress.label && (
            <span className={progressLabelVariants()}>{progress.label}</span>
          )}
        </div>
      )}

      <div className={panesVariants()}>
        {showPreview && (
          <div className={paneVariants()}>
            <div className={paneHeaderVariants()}>
              <span>Preview</span>
            </div>
            <div className={paneContentVariants()}>
              {renderedContent.length > 0 ? (
                renderedContent.map((item, i) => (
                  <RenderItem key={i} item={item} />
                ))
              ) : (
                <div className={placeholderVariants()}>No preview content</div>
              )}
            </div>
          </div>
        )}

        {showPreview && showConsole && (
          <div className={paneResizerVariants()} />
        )}

        {showConsole && (
          <div className={paneVariants()}>
            <div className={paneHeaderVariants()}>
              <span>Console</span>
            </div>
            <div className={paneContentVariants()}>
              {executionError ? (
                <div className={errorVariants()}>{executionError}</div>
              ) : (
                <>
                  {executionOutput && (
                    <pre ref={outputRef} className={outputTextVariants()}>
                      {executionOutput}
                      {isExecuting && (
                        <span className={cursorVariants()}>|</span>
                      )}
                    </pre>
                  )}
                  {executionResult !== null && !isExecuting && (
                    <div className={resultVariants()}>
                      <span className={resultLabelVariants()}>Result:</span>
                      <code className={resultCodeVariants()}>
                        {JSON.stringify(executionResult, null, 2)}
                      </code>
                    </div>
                  )}
                  {!executionOutput && !executionResult && !isExecuting && (
                    <div className={placeholderVariants()}>
                      Click "Run" to execute the workflow
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {!showPreview && !showConsole && (
          <div className={emptyStateVariants()}>
            Toggle Preview or Console to view execution output
          </div>
        )}
      </div>

      {alerts.length > 0 && (
        <div className={alertsContainerVariants()}>
          {alerts.map((alert) => (
            <AlertBox
              key={alert.id}
              alert={alert}
              onDismiss={() => removeAlert(alert.id)}
            />
          ))}
        </div>
      )}

      {pendingPrompt && (
        <PromptOverlay prompt={pendingPrompt} onSubmit={respondToPrompt} />
      )}
    </div>
  );
}

function TypedInputField({ input }: { input: DetailedInput }) {
  const { workflowInputs, setWorkflowInput } = useExecutionStore();
  const value = workflowInputs[input.name] ?? "";

  const label = (
    <label className={inputFieldLabelVariants()}>
      {input.name}
      {input.required && <span className="text-accent-red">*</span>}:
    </label>
  );

  if (input.type === "boolean") {
    return (
      <div className={inputFieldVariants()}>
        {label}
        <select
          value={value === "" ? "" : String(value)}
          onChange={(e) => {
            const v = e.target.value;
            if (v === "") setWorkflowInput(input.name, "");
            else setWorkflowInput(input.name, v === "true");
          }}
          className={inputFieldInputVariants()}
        >
          <option value="">--</option>
          <option value="true">true</option>
          <option value="false">false</option>
        </select>
      </div>
    );
  }

  if (input.type === "number") {
    return (
      <div className={inputFieldVariants()}>
        {label}
        <input
          type="number"
          value={String(value)}
          onChange={(e) => {
            const raw = e.target.value;
            if (raw === "") {
              setWorkflowInput(input.name, "");
            } else {
              const num = Number(raw);
              setWorkflowInput(input.name, isNaN(num) ? raw : num);
            }
          }}
          placeholder={`Enter ${input.name}`}
          className={inputFieldInputVariants()}
        />
      </div>
    );
  }

  return (
    <div className={inputFieldVariants()}>
      {label}
      <input
        type="text"
        value={String(value)}
        onChange={(e) => {
          const raw = e.target.value;
          try {
            setWorkflowInput(input.name, JSON.parse(raw));
          } catch {
            setWorkflowInput(input.name, raw);
          }
        }}
        placeholder={`Enter ${input.name}`}
        className={inputFieldInputVariants()}
      />
    </div>
  );
}

function RenderItem({ item }: { item: RenderedContent }) {
  switch (item.type) {
    case "html":
      return (
        <div
          className={htmlContentVariants()}
          dangerouslySetInnerHTML={{ __html: item.content as string }}
        />
      );

    case "markdown":
      return (
        <div className={markdownContentVariants()}>
          <MarkdownRenderer content={item.content as string} />
        </div>
      );

    case "table":
      const data = item.content as Record<string, unknown>[];
      if (!data.length) return null;
      const headers = Object.keys(data[0]);
      return (
        <div className={tableContainerVariants()}>
          <table className={tableVariants()}>
            <thead>
              <tr>
                {headers.map((h) => (
                  <th key={h} className={tableHeaderVariants()}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i} className="hover:bg-surface-2">
                  {headers.map((h) => (
                    <td key={h} className={tableCellVariants()}>
                      {String(row[h] ?? "")}
                    </td>
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
        <div className={imageContainerVariants()}>
          <img src={img.src} alt={img.alt} className={imageVariants()} />
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
  return (
    <div className={alertVariants({ variant: alert.variant })}>
      <span>{alert.message}</span>
      <button className={alertDismissVariants()} onClick={onDismiss}>
        ✕
      </button>
    </div>
  );
}
