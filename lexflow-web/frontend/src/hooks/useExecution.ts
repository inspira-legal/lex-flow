// useExecution - Abstraction hook for execution state

import { useExecutionStore } from "../store";

export function useExecution() {
  const isExecuting = useExecutionStore((state) => state.isExecuting);
  const setIsExecuting = useExecutionStore((state) => state.setIsExecuting);
  const executionOutput = useExecutionStore((state) => state.executionOutput);
  const setExecutionOutput = useExecutionStore(
    (state) => state.setExecutionOutput,
  );
  const appendExecutionOutput = useExecutionStore(
    (state) => state.appendExecutionOutput,
  );
  const executionResult = useExecutionStore((state) => state.executionResult);
  const setExecutionResult = useExecutionStore(
    (state) => state.setExecutionResult,
  );
  const executionError = useExecutionStore((state) => state.executionError);
  const setExecutionError = useExecutionStore(
    (state) => state.setExecutionError,
  );
  const clearExecution = useExecutionStore((state) => state.clearExecution);
  const workflowInputs = useExecutionStore((state) => state.workflowInputs);
  const setWorkflowInput = useExecutionStore((state) => state.setWorkflowInput);
  const clearWorkflowInputs = useExecutionStore(
    (state) => state.clearWorkflowInputs,
  );

  return {
    // Status
    isExecuting,
    setIsExecuting,

    // Output
    output: executionOutput,
    setOutput: setExecutionOutput,
    appendOutput: appendExecutionOutput,

    // Result
    result: executionResult,
    setResult: setExecutionResult,

    // Error
    error: executionError,
    setError: setExecutionError,

    // Clear
    clearExecution,

    // Inputs
    workflowInputs,
    setWorkflowInput,
    clearWorkflowInputs,
  };
}
