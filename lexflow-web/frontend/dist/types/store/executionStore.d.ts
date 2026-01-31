export interface PendingPrompt {
    type: "input" | "select" | "confirm" | "button";
    prompt: string;
    options?: string[];
    message?: string;
    label?: string;
}
export interface RenderedContent {
    type: "html" | "markdown" | "table" | "image";
    content: string | Record<string, unknown>[] | {
        src: string;
        alt: string;
    };
}
export interface AlertItem {
    id: string;
    message: string;
    variant: "info" | "success" | "warning" | "error";
}
export interface ProgressState {
    value: number;
    max: number;
    label: string;
}
interface ExecutionState {
    isExecuting: boolean;
    executionOutput: string;
    executionResult: unknown;
    executionError: string | null;
    workflowInputs: Record<string, unknown>;
    pendingPrompt: PendingPrompt | null;
    renderedContent: RenderedContent[];
    alerts: AlertItem[];
    progress: ProgressState | null;
    setIsExecuting: (isExecuting: boolean) => void;
    setExecutionOutput: (output: string) => void;
    appendExecutionOutput: (chunk: string) => void;
    setExecutionResult: (result: unknown) => void;
    setExecutionError: (error: string | null) => void;
    clearExecution: () => void;
    setWorkflowInput: (key: string, value: unknown) => void;
    clearWorkflowInputs: () => void;
    setPendingPrompt: (prompt: PendingPrompt | null) => void;
    addRenderedContent: (content: RenderedContent) => void;
    clearRenderedContent: () => void;
    addAlert: (alert: Omit<AlertItem, "id">) => void;
    removeAlert: (id: string) => void;
    setProgress: (progress: ProgressState | null) => void;
}
export declare const useExecutionStore: import("zustand").UseBoundStore<import("zustand").StoreApi<ExecutionState>>;
export {};
