import type { LexFlowEditorProps, ExecuteResult, ThemeOption } from "../types";
export interface LexFlowEditorHandle {
    getSource(): string;
    setSource(source: string): void;
    execute(inputs?: Record<string, unknown>): Promise<ExecuteResult>;
    setTheme(theme: ThemeOption): void;
    toggleCodeEditor(): void;
    togglePalette(): void;
    toggleExecutionPanel(): void;
}
export declare const LexFlowEditor: import("react").ForwardRefExoticComponent<LexFlowEditorProps & import("react").RefAttributes<LexFlowEditorHandle>>;
export default LexFlowEditor;
