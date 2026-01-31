export interface ParseResult<T> {
    success: boolean;
    data?: T;
    error?: string;
}
export declare function parseWorkflowSource<T = unknown>(source: string): ParseResult<T>;
