import type { ReactNode } from "react";
export interface MainLayoutProps {
    canvas: ReactNode;
    editor?: ReactNode;
    executionPanel?: ReactNode;
    nodeEditor?: ReactNode;
    palette?: ReactNode;
    className?: string;
}
