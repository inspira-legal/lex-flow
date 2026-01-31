import type { OpcodeInterface } from "../api/types";
export declare function useNodeOperations(): {
    addNode: (opcode: OpcodeInterface, workflowName?: string) => string | null;
    deleteNode: (nodeId: string) => boolean;
    duplicateNode: (nodeId: string) => string | null;
    updateNodeInput: (nodeId: string, inputKey: string, newValue: string) => boolean;
    connectNodes: (fromNodeId: string, toNodeId: string) => boolean;
    disconnectNode: (nodeId: string) => boolean;
    connectBranch: (fromNodeId: string, toNodeId: string, branchLabel: string) => boolean;
    disconnectConnection: (fromNodeId: string, toNodeId: string, branchLabel?: string) => boolean;
    convertOrphanToReporter: (orphanNodeId: string, targetNodeId: string, inputKey: string) => boolean;
    deleteReporter: (parentNodeId: string, inputPath: string[]) => boolean;
};
