import type { MountOptions, EditorInstance } from "./types";
import "../styles/variables.css";
import "../styles/index.css";
/**
 * Mount a LexFlow Editor instance to a DOM element.
 *
 * @param container - DOM element or CSS selector string
 * @param options - Editor configuration options
 * @param options.initialSource - Initial workflow YAML/JSON source
 * @param options.executionUrl - Base URL for API endpoints (default: "/api")
 * @param options.websocketUrl - WebSocket URL for streaming execution
 * @param options.backendProvider - Custom backend provider implementation
 * @param options.theme - Theme preset ("light", "dark", "system") or config object
 * @param options.lite - Use textarea fallback instead of Monaco editor
 * @param options.showCodeEditor - Show code editor panel (default: true)
 * @param options.showPalette - Show node palette (default: true)
 * @param options.showExecutionPanel - Show execution output panel (default: true)
 * @param options.showNodeEditor - Show node editor panel (default: true)
 * @param options.onSourceChange - Callback when workflow source changes
 * @param options.onExecute - Callback when execution completes
 * @param options.onError - Callback when an error occurs
 * @param options.onReady - Callback when editor is ready
 * @param options.onSave - Callback when save button clicked, receives (source, metadata)
 * @param options.showSaveButton - Show save button (default: true if onSave provided)
 * @param options.saveButtonLabel - Custom label for save button (default: "Save")
 * @param options.showExamples - Show examples dropdown (default: true, auto-hides if empty)
 * @param options.opcodesUrl - Custom URL for opcodes endpoint
 * @param options.opcodeAdapter - Transform function for opcode API response
 * @param options.executeOverride - Custom execution function, bypasses normal flow
 * @returns EditorInstance with methods to control the editor
 *
 * @example
 * // Basic usage
 * const editor = LexFlow.mount('#editor');
 *
 * @example
 * // With save callback
 * const editor = LexFlow.mount('#editor', {
 *   onSave: async (source, metadata) => {
 *     await fetch('/api/save', { method: 'POST', body: source });
 *   },
 *   saveButtonLabel: 'Save to Cloud'
 * });
 *
 * @example
 * // With custom opcode endpoint and adapter
 * const editor = LexFlow.mount('#editor', {
 *   opcodesUrl: 'https://my-api.com/nodes',
 *   opcodeAdapter: (raw) => raw.operations.map(op => ({
 *     name: op.op_name,
 *     description: op.desc,
 *     parameters: op.args.map(a => ({
 *       name: a.name,
 *       type: a.type,
 *       required: !a.optional
 *     }))
 *   }))
 * });
 *
 * @example
 * // With execution override
 * const editor = LexFlow.mount('#editor', {
 *   executeOverride: async (source, inputs) => ({
 *     success: true,
 *     output: 'Custom execution result!',
 *     result: { custom: true }
 *   })
 * });
 */
export declare function mount(container: HTMLElement | string, options?: Omit<MountOptions, "container">): EditorInstance;
export declare function unmountAll(): void;
export declare function getMountedCount(): number;
declare const _default: {
    mount: typeof mount;
    unmountAll: typeof unmountAll;
    getMountedCount: typeof getMountedCount;
};
export default _default;
