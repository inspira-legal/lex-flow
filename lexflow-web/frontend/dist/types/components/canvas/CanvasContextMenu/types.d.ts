export interface CanvasContextMenuProps {
    x: number;
    y: number;
    workflowName?: string;
    onCreateWorkflow: () => void;
    onDeleteWorkflow?: (name: string) => void;
    onClose: () => void;
}
