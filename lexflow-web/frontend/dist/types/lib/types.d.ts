import type { BackendProvider } from "../providers/types";
import type { OpcodeInterface } from "../api/types";
export type { EditorMetadata } from "../services/metadata";
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
export interface LexFlowEditorProps {
    initialSource?: string;
    executionUrl?: string;
    websocketUrl?: string;
    backendProvider?: BackendProvider;
    theme?: ThemeOption;
    lite?: boolean;
    showCodeEditor?: boolean;
    showPalette?: boolean;
    showExecutionPanel?: boolean;
    showNodeEditor?: boolean;
    onSourceChange?: (source: string) => void;
    onExecute?: (result: ExecuteResult) => void;
    onError?: (error: string) => void;
    onReady?: () => void;
    onSave?: (source: string, metadata: import("../services/metadata").EditorMetadata) => void | Promise<void>;
    showSaveButton?: boolean;
    saveButtonLabel?: string;
    showExamples?: boolean;
    opcodesUrl?: string;
    opcodeAdapter?: (rawData: unknown) => OpcodeInterface[];
    executeOverride?: (source: string, inputs?: Record<string, unknown>) => Promise<ExecuteResult>;
    className?: string;
    style?: React.CSSProperties;
    instanceId?: string;
}
export interface ExecuteResult {
    success: boolean;
    output?: string;
    result?: unknown;
    error?: string;
    metrics?: Record<string, unknown>;
}
export interface MountOptions extends Omit<LexFlowEditorProps, "className" | "style"> {
    container?: HTMLElement | string;
}
export interface EditorInstance {
    getSource(): string;
    setSource(source: string): void;
    execute(inputs?: Record<string, unknown>): Promise<ExecuteResult>;
    setTheme(theme: ThemeOption): void;
    getTheme(): ThemePreset;
    toggleCodeEditor(): void;
    togglePalette(): void;
    toggleExecutionPanel(): void;
    destroy(): void;
}
export type { BackendProvider, BackendConfig } from "../providers/types";
