// Public TypeScript types for the embeddable LexFlow Editor library

import type { BackendProvider } from "../providers/types";

// Theme configuration
export type ThemePreset = "light" | "dark" | "system";

export interface ThemeColors {
  accent?: string;
  background?: string;
  surface?: string;
  text?: string;
  border?: string;
}

export interface ThemeConfig {
  preset?: ThemePreset;
  colors?: ThemeColors;
  cssVariables?: Record<string, string>;
}

export type ThemeOption = ThemePreset | ThemeConfig;

// Editor props for React component
export interface LexFlowEditorProps {
  // Content
  initialSource?: string;

  // Backend configuration
  executionUrl?: string;
  websocketUrl?: string;
  backendProvider?: BackendProvider;

  // Appearance
  theme?: ThemeOption;
  lite?: boolean; // No Monaco editor, use textarea fallback

  // Panel visibility
  showCodeEditor?: boolean;
  showPalette?: boolean;
  showExecutionPanel?: boolean;
  showNodeEditor?: boolean;

  // Callbacks
  onSourceChange?: (source: string) => void;
  onExecute?: (result: ExecuteResult) => void;
  onError?: (error: string) => void;
  onReady?: () => void;

  // Styling
  className?: string;
  style?: React.CSSProperties;

  // Instance ID (for multi-instance support)
  instanceId?: string;
}

// Execution result type
export interface ExecuteResult {
  success: boolean;
  output?: string;
  result?: unknown;
  error?: string;
  metrics?: Record<string, unknown>;
}

// Vanilla JS mount options
export interface MountOptions extends Omit<LexFlowEditorProps, "className" | "style"> {
  // Container element or selector
  container?: HTMLElement | string;
}

// Editor instance returned by mount()
export interface EditorInstance {
  // State
  getSource(): string;
  setSource(source: string): void;

  // Execution
  execute(inputs?: Record<string, unknown>): Promise<ExecuteResult>;

  // Theme
  setTheme(theme: ThemeOption): void;
  getTheme(): ThemePreset;

  // Panels
  toggleCodeEditor(): void;
  togglePalette(): void;
  toggleExecutionPanel(): void;

  // Lifecycle
  destroy(): void;
}

// Re-export BackendProvider for advanced users
export type { BackendProvider, BackendConfig } from "../providers/types";
