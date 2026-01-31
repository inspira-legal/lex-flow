export declare function useWebSocketExecution(): {
    execute: (workflow: string, inputs?: Record<string, unknown>, includeMetrics?: boolean) => Promise<void>;
    cancel: () => void;
    respondToPrompt: (value: unknown) => void;
};
