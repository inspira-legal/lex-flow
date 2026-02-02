// LexFlow Editor - Main ES module entry point
// Embeddable visual workflow editor for LexFlow

// Preserve original exports for backwards compatibility
export { cn } from "./cn";
export { ThemeContext, useTheme } from "./theme";

// Main component
export { LexFlowEditor, type LexFlowEditorHandle } from "./components/LexFlowEditor";
export { default as LexFlowEditorDefault } from "./components/LexFlowEditor";

// Vanilla JS API
export { mount, unmountAll, getMountedCount } from "./vanilla";

// Types
export type {
  LexFlowEditorProps,
  ThemeOption,
  ThemeConfig,
  ThemeColors,
  MountOptions,
  EditorInstance,
  ExecuteResult,
  BackendProvider,
  BackendConfig,
  EditorMetadata,
} from "./types";
export type { ThemePreset } from "./theme/presets";

// API types for opcode adapters
export type { OpcodeInterface, OpcodeParameter } from "../api/types";

// Theme utilities (from theme/ directory)
export {
  LibraryThemeProvider,
  useLibraryTheme,
  darkThemeVars,
  lightThemeVars,
  commonVars,
  getPresetVars,
  injectThemeVars,
  removeThemeVars,
  createScopedCSS,
} from "./theme/index";

// Store utilities (for advanced users)
export {
  StoreProvider,
  useEditorStore,
  useEditorStoreApi,
  createEditorStore,
} from "./store";

export type {
  EditorStoreState,
  EditorStore,
  CreateStoresOptions,
} from "./store";

// Backend provider utilities
export {
  BackendProviderWrapper,
  useBackendProvider,
  createLexFlowProvider,
  supportsExamples,
  supportsValidation,
} from "../providers";

// Version info
export const VERSION = "__VERSION__"; // Replaced at build time
