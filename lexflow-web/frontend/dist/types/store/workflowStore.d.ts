import type { WorkflowTree, ExampleInfo, OpcodeInterface, DetailedInput } from "../api/types";
interface WorkflowState {
    source: string;
    setSource: (source: string, addToHistory?: boolean) => void;
    history: string[];
    historyIndex: number;
    canUndo: boolean;
    canRedo: boolean;
    undo: () => void;
    redo: () => void;
    tree: WorkflowTree | null;
    parseError: string | null;
    isParsing: boolean;
    setTree: (tree: WorkflowTree | null) => void;
    setParseError: (error: string | null) => void;
    setIsParsing: (isParsing: boolean) => void;
    deleteNode: (nodeId: string) => boolean;
    addNode: (opcode: OpcodeInterface, workflowName?: string) => string | null;
    addWorkflowCallNode: (workflowName: string, params: string[], targetWorkflow?: string) => string | null;
    duplicateNode: (nodeId: string) => string | null;
    updateNodeInput: (nodeId: string, inputKey: string, newValue: string) => boolean;
    connectNodes: (fromNodeId: string, toNodeId: string, workflowName?: string) => boolean;
    connectBranch: (fromNodeId: string, toNodeId: string, branchLabel: string) => boolean;
    disconnectNode: (nodeId: string, workflowName?: string) => boolean;
    disconnectConnection: (fromNodeId: string, toNodeId: string, branchLabel?: string, workflowName?: string) => boolean;
    convertOrphanToReporter: (orphanNodeId: string, targetNodeId: string, inputKey: string) => boolean;
    updateReporterInput: (reporterNodeId: string, inputKey: string, newValue: string) => boolean;
    deleteReporter: (parentNodeId: string, inputPath: string[]) => boolean;
    updateWorkflowInterface: (workflowName: string, inputs: DetailedInput[], outputs: string[]) => boolean;
    addVariable: (workflowName: string, name: string, defaultValue: unknown) => boolean;
    updateVariable: (workflowName: string, oldName: string, newName: string, newValue: unknown) => boolean;
    deleteVariable: (workflowName: string, name: string) => boolean;
    addDynamicBranch: (nodeId: string, branchPrefix: string) => boolean;
    removeDynamicBranch: (nodeId: string, branchName: string) => boolean;
    addDynamicInput: (nodeId: string, inputPrefix: string) => boolean;
    removeDynamicInput: (nodeId: string, inputName: string) => boolean;
    addWorkflow: (name: string, inputs?: DetailedInput[], outputs?: string[], variables?: Record<string, unknown>) => boolean;
    deleteWorkflow: (name: string) => boolean;
    extractToWorkflow: (nodeIds: string[], sourceWorkflowName: string, newWorkflowName: string, inputs: DetailedInput[], outputs: string[], variables: Record<string, unknown>) => {
        success: boolean;
        errors: string[];
    };
    examples: ExampleInfo[];
    setExamples: (examples: ExampleInfo[]) => void;
    opcodes: OpcodeInterface[];
    setOpcodes: (opcodes: OpcodeInterface[]) => void;
    isExecuting: boolean;
    executionOutput: string;
    executionResult: unknown;
    executionError: string | null;
    setIsExecuting: (isExecuting: boolean) => void;
    setExecutionOutput: (output: string) => void;
    appendExecutionOutput: (chunk: string) => void;
    setExecutionResult: (result: unknown) => void;
    setExecutionError: (error: string | null) => void;
    clearExecution: () => void;
    workflowInputs: Record<string, unknown>;
    setWorkflowInput: (key: string, value: unknown) => void;
    clearWorkflowInputs: () => void;
}
export declare const useWorkflowStore: import("zustand").UseBoundStore<Omit<import("zustand").StoreApi<WorkflowState>, "setState" | "persist"> & {
    setState(partial: WorkflowState | Partial<WorkflowState> | ((state: WorkflowState) => WorkflowState | Partial<WorkflowState>), replace?: false | undefined): unknown;
    setState(state: WorkflowState | ((state: WorkflowState) => WorkflowState), replace: true): unknown;
    persist: {
        setOptions: (options: Partial<import("zustand/middleware").PersistOptions<WorkflowState, {
            source: string;
        }, unknown>>) => void;
        clearStorage: () => void;
        rehydrate: () => Promise<void> | void;
        hasHydrated: () => boolean;
        onHydrate: (fn: (state: WorkflowState) => void) => () => void;
        onFinishHydration: (fn: (state: WorkflowState) => void) => () => void;
        getOptions: () => Partial<import("zustand/middleware").PersistOptions<WorkflowState, {
            source: string;
        }, unknown>>;
    };
}>;
export {};
