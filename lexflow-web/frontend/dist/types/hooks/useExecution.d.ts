export declare function useExecution(): {
    isExecuting: boolean;
    setIsExecuting: (isExecuting: boolean) => void;
    output: string;
    setOutput: (output: string) => void;
    appendOutput: (chunk: string) => void;
    result: unknown;
    setResult: (result: unknown) => void;
    error: string | null;
    setError: (error: string | null) => void;
    clearExecution: () => void;
    workflowInputs: Record<string, unknown>;
    setWorkflowInput: (key: string, value: unknown) => void;
    clearWorkflowInputs: () => void;
};
