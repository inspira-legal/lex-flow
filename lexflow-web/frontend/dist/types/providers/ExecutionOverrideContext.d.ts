import { type ReactNode } from "react";
import type { ExecuteResult } from "../lib/types";
export type ExecuteOverride = (source: string, inputs?: Record<string, unknown>) => Promise<ExecuteResult>;
interface ExecutionOverrideWrapperProps {
    override?: ExecuteOverride;
    children: ReactNode;
}
export declare function ExecutionOverrideWrapper({ override, children, }: ExecutionOverrideWrapperProps): import("react/jsx-runtime").JSX.Element;
export declare function useExecutionOverride(): ExecuteOverride | null;
export {};
