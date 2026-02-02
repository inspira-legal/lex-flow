// Execution override context for bypassing normal WebSocket/REST execution

import { createContext, useContext, type ReactNode } from "react";
import type { ExecuteResult } from "../lib/types";

export type ExecuteOverride = (
  source: string,
  inputs?: Record<string, unknown>
) => Promise<ExecuteResult>;

const ExecutionOverrideContext = createContext<ExecuteOverride | null>(null);

interface ExecutionOverrideWrapperProps {
  override?: ExecuteOverride;
  children: ReactNode;
}

export function ExecutionOverrideWrapper({
  override,
  children,
}: ExecutionOverrideWrapperProps) {
  return (
    <ExecutionOverrideContext.Provider value={override ?? null}>
      {children}
    </ExecutionOverrideContext.Provider>
  );
}

export function useExecutionOverride(): ExecuteOverride | null {
  return useContext(ExecutionOverrideContext);
}
