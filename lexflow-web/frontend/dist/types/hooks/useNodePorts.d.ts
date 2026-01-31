interface UseNodePortsProps {
    nodeId: string;
    x: number;
    y: number;
}
interface UseNodePortsReturn {
    handleOutputPortMouseDown: (e: React.MouseEvent) => void;
    handleInputPortMouseDown: (e: React.MouseEvent) => void;
    handleOutputPortMouseUp: (e: React.MouseEvent) => void;
    handleInputPortMouseUp: (e: React.MouseEvent) => void;
    handleBranchPortMouseDown: (e: React.MouseEvent, branchName: string, portX: number, portY: number) => void;
    isInputPortHighlighted: boolean;
    isOutputPortHighlighted: boolean;
    isValidDropTarget: boolean;
    isValidOutputDropTarget: boolean;
}
export declare function useNodePorts({ nodeId, x, y, }: UseNodePortsProps): UseNodePortsReturn;
export {};
