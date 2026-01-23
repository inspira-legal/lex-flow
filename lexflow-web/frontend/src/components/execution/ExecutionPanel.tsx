import { useRef, useEffect } from "react";
import { useWorkflowStore, useUiStore, useExecutionStore } from "../../store";
import { useWebSocketExecution } from "../../hooks";
import styles from "./ExecutionPanel.module.css";

export function ExecutionPanel() {
  const { source, tree } = useWorkflowStore();
  const {
    isExecuting,
    executionOutput,
    executionResult,
    executionError,
    workflowInputs,
  } = useExecutionStore();
  const { toggleExecutionPanel } = useUiStore();
  const { execute, cancel } = useWebSocketExecution();
  const outputRef = useRef<HTMLPreElement>(null);

  // Auto-scroll output to bottom
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [executionOutput]);

  const handleRun = () => {
    execute(source, workflowInputs);
  };

  const handleCancel = () => {
    cancel();
  };

  const inputs = tree?.interface?.inputs || [];

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.title}>Execution</span>
        <div className={styles.actions}>
          {isExecuting ? (
            <button className={styles.cancelBtn} onClick={handleCancel}>
              ■ Stop
            </button>
          ) : (
            <button className={styles.runBtn} onClick={handleRun}>
              ▶ Run
            </button>
          )}
          <button className={styles.iconBtn} onClick={toggleExecutionPanel}>
            ✕
          </button>
        </div>
      </div>

      <div className={styles.content}>
        {/* Inputs */}
        {inputs.length > 0 && (
          <div className={styles.inputs}>
            <span className={styles.label}>Inputs:</span>
            {inputs.map((input) => (
              <InputField key={input} name={input} />
            ))}
          </div>
        )}

        {/* Output */}
        <div className={styles.output}>
          {executionError ? (
            <div className={styles.error}>{executionError}</div>
          ) : (
            <>
              {executionOutput && (
                <pre ref={outputRef} className={styles.outputText}>
                  {executionOutput}
                  {isExecuting && <span className={styles.cursor}>▋</span>}
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
