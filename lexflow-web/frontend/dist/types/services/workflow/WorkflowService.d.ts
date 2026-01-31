import type { OpcodeInterface } from "../../api/types";
export interface NodeResult {
    source: string;
    nodeId: string | null;
}
export interface OperationResult {
    source: string;
    success: boolean;
}
export declare function formatYamlValue(value: unknown): string;
export declare function findNodeLineRange(source: string, nodeId: string, workflowName?: string): {
    startLine: number;
    endLine: number;
    indent: number;
} | null;
export declare function generateUniqueNodeId(source: string, prefix: string): string;
export declare function deleteNode(source: string, nodeId: string): OperationResult;
export declare function addNode(source: string, opcode: OpcodeInterface, workflowName?: string): NodeResult;
export declare function duplicateNode(source: string, nodeId: string): NodeResult;
export declare function updateNodeInput(source: string, nodeId: string, inputKey: string, newValue: string): OperationResult;
export declare function connectNodes(source: string, fromNodeId: string, toNodeId: string, workflowName?: string): OperationResult;
export declare function disconnectNode(source: string, nodeId: string, workflowName?: string): OperationResult;
export declare function connectBranch(source: string, fromNodeId: string, toNodeId: string, branchLabel: string): OperationResult;
export declare function disconnectConnection(source: string, fromNodeId: string, toNodeId: string, branchLabel?: string, workflowName?: string): OperationResult;
export declare function convertOrphanToReporter(source: string, orphanNodeId: string, targetNodeId: string, inputKey: string): OperationResult;
export declare function deleteReporter(source: string, parentNodeId: string, inputPath: string[]): OperationResult;
export declare function updateWorkflowInterface(source: string, workflowName: string, inputs: string[], outputs: string[]): OperationResult;
export declare function addVariable(source: string, workflowName: string, name: string, defaultValue: unknown): OperationResult;
export declare function updateVariable(source: string, workflowName: string, oldName: string, newName: string, newValue: unknown): OperationResult;
export declare function deleteVariable(source: string, workflowName: string, name: string): OperationResult;
export declare function addWorkflowCallNode(source: string, workflowName: string, params: string[], targetWorkflow?: string): NodeResult;
export declare function addDynamicBranch(source: string, nodeId: string, branchPrefix: string): OperationResult;
export declare function removeDynamicBranch(source: string, nodeId: string, branchName: string): OperationResult;
export declare function addDynamicInput(source: string, nodeId: string, inputPrefix: string): OperationResult;
export declare function removeDynamicInput(source: string, nodeId: string, inputName: string): OperationResult;
export declare function addWorkflow(source: string, name: string, inputs?: string[], outputs?: string[], variables?: Record<string, unknown>): OperationResult;
export declare function deleteWorkflow(source: string, name: string): OperationResult;
export declare const workflowService: {
    formatYamlValue: typeof formatYamlValue;
    findNodeLineRange: typeof findNodeLineRange;
    generateUniqueNodeId: typeof generateUniqueNodeId;
    deleteNode: typeof deleteNode;
    addNode: typeof addNode;
    addWorkflowCallNode: typeof addWorkflowCallNode;
    duplicateNode: typeof duplicateNode;
    updateNodeInput: typeof updateNodeInput;
    connectNodes: typeof connectNodes;
    disconnectNode: typeof disconnectNode;
    connectBranch: typeof connectBranch;
    disconnectConnection: typeof disconnectConnection;
    convertOrphanToReporter: typeof convertOrphanToReporter;
    deleteReporter: typeof deleteReporter;
    updateWorkflowInterface: typeof updateWorkflowInterface;
    addVariable: typeof addVariable;
    updateVariable: typeof updateVariable;
    deleteVariable: typeof deleteVariable;
    addDynamicBranch: typeof addDynamicBranch;
    removeDynamicBranch: typeof removeDynamicBranch;
    addDynamicInput: typeof addDynamicInput;
    removeDynamicInput: typeof removeDynamicInput;
    addWorkflow: typeof addWorkflow;
    deleteWorkflow: typeof deleteWorkflow;
};
