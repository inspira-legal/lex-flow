export declare function useWorkflowState(): {
    source: string;
    setSource: (source: string, addToHistory?: boolean) => void;
    tree: import("../api").WorkflowTree | null;
    setTree: (tree: import("../api").WorkflowTree | null) => void;
    parseError: string | null;
    setParseError: (error: string | null) => void;
    isParsing: boolean;
    setIsParsing: (isParsing: boolean) => void;
    canUndo: boolean;
    canRedo: boolean;
    undo: () => void;
    redo: () => void;
    opcodes: import("../lib").OpcodeInterface[];
    setOpcodes: (opcodes: import("../lib").OpcodeInterface[]) => void;
    examples: import("../api").ExampleInfo[];
    setExamples: (examples: import("../api").ExampleInfo[]) => void;
};
