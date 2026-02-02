import type { ParseResponse, ValidateResponse, ExecuteResponse, ExampleInfo, ExampleContent, OpcodeInterface } from "../api/types";
export interface BackendConfig {
    apiBaseUrl: string;
    wsUrl?: string;
    supportsExamples?: boolean;
    supportsWebSocket?: boolean;
    opcodesUrl?: string;
    opcodeAdapter?: (rawData: unknown) => OpcodeInterface[];
}
export interface BackendProvider {
    name: string;
    config: BackendConfig;
    listOpcodes(): Promise<OpcodeInterface[]>;
    executeWorkflow(source: string, inputs?: Record<string, unknown>, includeMetrics?: boolean): Promise<ExecuteResponse>;
    getWebSocketUrl(): string | null;
    parseWorkflow(source: string): Promise<ParseResponse>;
    validateWorkflow?(source: string): Promise<ValidateResponse>;
    listExamples?(): Promise<ExampleInfo[]>;
    getExample?(path: string): Promise<ExampleContent>;
}
export declare function supportsExamples(provider: BackendProvider): provider is BackendProvider & {
    listExamples: () => Promise<ExampleInfo[]>;
    getExample: (path: string) => Promise<ExampleContent>;
};
export declare function supportsValidation(provider: BackendProvider): provider is BackendProvider & {
    validateWorkflow: (source: string) => Promise<ValidateResponse>;
};
