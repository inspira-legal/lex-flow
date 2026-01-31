import type { FormattedValue } from "../api/types";
export interface SelectedReporter {
    parentNodeId: string;
    inputPath: string[];
    reporterNodeId: string | undefined;
    opcode: string;
    inputs: Record<string, FormattedValue>;
}
export interface SelectedConnection {
    fromNodeId: string;
    toNodeId: string;
    label?: string;
}
interface SelectionState {
    selectedNodeId: string | null;
    selectNode: (id: string | null) => void;
    selectedNodeIds: string[];
    toggleNodeSelection: (id: string) => void;
    addToSelection: (id: string) => void;
    clearMultiSelection: () => void;
    selectedReporter: SelectedReporter | null;
    selectReporter: (reporter: SelectedReporter | null) => void;
    selectedConnection: SelectedConnection | null;
    selectConnection: (conn: SelectedConnection | null) => void;
    selectedStartNode: string | null;
    selectStartNode: (workflowName: string | null) => void;
    clearSelection: () => void;
}
export declare const useSelectionStore: import("zustand").UseBoundStore<import("zustand").StoreApi<SelectionState>>;
export {};
