// Main embeddable LexFlowEditor component

import {
  useEffect,
  useRef,
  forwardRef,
  useImperativeHandle,
} from "react";
import { MainLayout } from "@/components/layout";
import { Canvas } from "@/components/canvas";
import { CodeEditor } from "@/components/editor";
import { ExecutionPanel } from "@/components/execution";
import { NodeEditorPanel } from "@/components/node-editor";
import { NodePalette, DragPreview } from "@/components/palette";
import { ConfirmDialog } from "@/components/ui";
import { useWorkflowStore, useUiStore } from "@/store";
import { ThemeProvider } from "../theme/index";
import { BackendProviderWrapper, createLexFlowProvider, useBackendProvider, supportsExamples } from "@/providers";
import type { BackendProvider } from "@/providers";
import type { LexFlowEditorProps, ExecuteResult, ThemeOption } from "../types";
import { cn } from "../cn";
import { useKeyboardShortcuts, useWorkflowParsing } from "@/hooks";

// Global confirm dialog connected to store
function GlobalConfirmDialog() {
  const confirmDialog = useUiStore((s) => s.confirmDialog);

  if (!confirmDialog) return null;

  return (
    <ConfirmDialog
      isOpen={confirmDialog.isOpen}
      title={confirmDialog.title}
      message={confirmDialog.message}
      confirmLabel={confirmDialog.confirmLabel}
      cancelLabel={confirmDialog.cancelLabel}
      variant={confirmDialog.variant}
      onConfirm={confirmDialog.onConfirm}
      onCancel={confirmDialog.onCancel}
    />
  );
}

// Internal editor component that uses the global stores
function EditorContent({
  lite = false,
  showCodeEditor = true,
  showPalette = true,
  showExecutionPanel = true,
  showNodeEditor = true,
  onSourceChange,
  onExecute,
  onError,
  onReady,
}: Pick<
  LexFlowEditorProps,
  | "lite"
  | "showCodeEditor"
  | "showPalette"
  | "showExecutionPanel"
  | "showNodeEditor"
  | "onSourceChange"
  | "onExecute"
  | "onError"
  | "onReady"
>) {
  const { source, setExamples, setOpcodes, isExecuting, executionOutput, executionResult, executionError } = useWorkflowStore();
  const provider = useBackendProvider();

  // Enable keyboard shortcuts
  useKeyboardShortcuts();

  // Parse workflow on source changes
  useWorkflowParsing();

  // Load examples and opcodes on mount
  useEffect(() => {
    provider.listOpcodes().then(setOpcodes).catch(console.error);

    if (supportsExamples(provider)) {
      provider.listExamples().then(setExamples).catch(console.error);
    }

    onReady?.();
  }, [setExamples, setOpcodes, provider, onReady]);

  // Track source changes
  const prevSourceRef = useRef(source);
  useEffect(() => {
    if (source !== prevSourceRef.current) {
      prevSourceRef.current = source;
      onSourceChange?.(source);
    }
  }, [source, onSourceChange]);

  // Track execution errors
  useEffect(() => {
    if (executionError) {
      onError?.(executionError);
    }
  }, [executionError, onError]);

  // Track execution results
  const prevExecutingRef = useRef(isExecuting);
  useEffect(() => {
    if (prevExecutingRef.current && !isExecuting) {
      const result: ExecuteResult = {
        success: !executionError,
        output: executionOutput,
        result: executionResult,
        error: executionError ?? undefined,
      };
      onExecute?.(result);
    }
    prevExecutingRef.current = isExecuting;
  }, [isExecuting, executionError, executionOutput, executionResult, onExecute]);

  return (
    <>
      <MainLayout
        canvas={<Canvas />}
        editor={showCodeEditor ? <CodeEditor lite={lite} /> : undefined}
        executionPanel={showExecutionPanel ? <ExecutionPanel /> : undefined}
        nodeEditor={showNodeEditor ? <NodeEditorPanel /> : undefined}
        palette={showPalette ? <NodePalette /> : undefined}
      />
      <DragPreview />
      <GlobalConfirmDialog />
    </>
  );
}

// Imperative handle interface
export interface LexFlowEditorHandle {
  getSource(): string;
  setSource(source: string): void;
  execute(inputs?: Record<string, unknown>): Promise<ExecuteResult>;
  setTheme(theme: ThemeOption): void;
  toggleCodeEditor(): void;
  togglePalette(): void;
  toggleExecutionPanel(): void;
}

// Main exported component
export const LexFlowEditor = forwardRef<LexFlowEditorHandle, LexFlowEditorProps>(
  function LexFlowEditor(
    {
      initialSource,
      executionUrl,
      websocketUrl,
      backendProvider: customProvider,
      theme = "dark",
      lite = false,
      showCodeEditor = true,
      showPalette = true,
      showExecutionPanel = true,
      showNodeEditor = true,
      onSourceChange,
      onExecute,
      onError,
      onReady,
      className,
      style,
    },
    ref
  ) {
    const containerRef = useRef<HTMLDivElement>(null);

    // Create backend provider
    const providerRef = useRef<BackendProvider>(
      customProvider ??
        createLexFlowProvider({
          apiBaseUrl: executionUrl ?? "/api",
          wsUrl: websocketUrl,
          supportsExamples: true,
          supportsWebSocket: true,
        })
    );

    // Set initial source on mount
    useEffect(() => {
      if (initialSource) {
        useWorkflowStore.getState().setSource(initialSource, false);
      }
    }, []); // Only on mount

    // Expose imperative handle
    useImperativeHandle(
      ref,
      () => ({
        getSource: () => {
          return useWorkflowStore.getState().source;
        },
        setSource: (source: string) => {
          useWorkflowStore.getState().setSource(source);
        },
        execute: async (inputs?: Record<string, unknown>) => {
          const store = useWorkflowStore.getState();
          store.setIsExecuting(true);
          store.clearExecution();

          try {
            const result = await providerRef.current.executeWorkflow(
              store.source,
              inputs
            );
            store.setExecutionOutput(result.output ?? "");
            store.setExecutionResult(result.result);
            if (result.error) {
              store.setExecutionError(result.error);
            }
            store.setIsExecuting(false);
            return {
              success: result.success,
              output: result.output,
              result: result.result,
              error: result.error ?? undefined,
            };
          } catch (err) {
            const error = err instanceof Error ? err.message : "Execution failed";
            store.setExecutionError(error);
            store.setIsExecuting(false);
            return { success: false, error };
          }
        },
        setTheme: () => {
          // Theme is controlled through props
        },
        toggleCodeEditor: () => {
          useUiStore.getState().toggleEditor();
        },
        togglePalette: () => {
          useUiStore.getState().togglePalette();
        },
        toggleExecutionPanel: () => {
          useUiStore.getState().toggleExecutionPanel();
        },
      }),
      []
    );

    // Apply theme class to container
    useEffect(() => {
      const container = containerRef.current;
      if (!container) return;

      const resolvedTheme = theme === "system"
        ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
        : (typeof theme === "string" ? theme : theme.preset ?? "dark");

      if (resolvedTheme === "light") {
        container.classList.add("light");
      } else {
        container.classList.remove("light");
      }
    }, [theme]);

    return (
      <div
        ref={containerRef}
        className={cn("lexflow-editor h-full w-full", className)}
        style={style}
      >
        <ThemeProvider>
          <BackendProviderWrapper provider={providerRef.current}>
            <EditorContent
              lite={lite}
              showCodeEditor={showCodeEditor}
              showPalette={showPalette}
              showExecutionPanel={showExecutionPanel}
              showNodeEditor={showNodeEditor}
              onSourceChange={onSourceChange}
              onExecute={onExecute}
              onError={onError}
              onReady={onReady}
            />
          </BackendProviderWrapper>
        </ThemeProvider>
      </div>
    );
  }
);

export default LexFlowEditor;
