export interface WorkflowGroupProps {
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
    isMain?: boolean;
    zoom: number;
    onDrag?: (dx: number, dy: number) => void;
}
