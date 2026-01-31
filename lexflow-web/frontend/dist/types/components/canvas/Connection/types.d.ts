export interface ConnectionProps {
    fromNodeId: string;
    toNodeId: string;
    fromPort?: "input" | "output" | string;
    toPort?: "input" | "output";
    x1?: number;
    y1?: number;
    x2?: number;
    y2?: number;
    color?: string;
    label?: string;
    isDotted?: boolean;
    isSelected?: boolean;
    onSelect?: () => void;
    onDelete?: () => void;
}
