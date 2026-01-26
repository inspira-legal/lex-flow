import { useRef, useCallback } from "react";
import { useExecutionStore } from "../store";
import { useBackendProvider } from "../providers";

interface ExecuteMessage {
  type: "start";
  workflow: string;
  inputs?: Record<string, unknown>;
  include_metrics?: boolean;
}

interface OutputMessage {
  type: "output";
  line: string;
}

interface CompleteMessage {
  type: "complete";
  result: unknown;
  metrics?: Record<string, unknown>;
}

interface ErrorMessage {
  type: "error";
  message: string;
}

// Web opcode messages
interface InputRequestMessage {
  type: "input_request";
  prompt: string;
}

interface SelectRequestMessage {
  type: "select_request";
  prompt: string;
  options: string[];
}

interface ConfirmRequestMessage {
  type: "confirm_request";
  message: string;
}

interface ButtonRequestMessage {
  type: "button_request";
  label: string;
}

interface RenderHtmlMessage {
  type: "render_html";
  html: string;
}

interface RenderMarkdownMessage {
  type: "render_markdown";
  content: string;
}

interface RenderTableMessage {
  type: "render_table";
  data: Record<string, unknown>[];
}

interface RenderImageMessage {
  type: "render_image";
  src: string;
  alt: string;
}

interface ProgressMessage {
  type: "progress";
  value: number;
  max: number;
  label: string;
}

interface AlertMessage {
  type: "alert";
  message: string;
  variant: "info" | "success" | "warning" | "error";
}

interface ClearContentMessage {
  type: "clear_content";
}

type ServerMessage =
  | OutputMessage
  | CompleteMessage
  | ErrorMessage
  | InputRequestMessage
  | SelectRequestMessage
  | ConfirmRequestMessage
  | RenderHtmlMessage
  | RenderMarkdownMessage
  | RenderTableMessage
  | RenderImageMessage
  | ProgressMessage
  | AlertMessage
  | ClearContentMessage;

export function useWebSocketExecution() {
  const wsRef = useRef<WebSocket | null>(null);
  const provider = useBackendProvider();
  const {
    setIsExecuting,
    appendExecutionOutput,
    setExecutionResult,
    setExecutionError,
    clearExecution,
    setPendingPrompt,
    addRenderedContent,
    clearRenderedContent,
    addAlert,
    setProgress,
  } = useExecutionStore();

  const respondToPrompt = useCallback((value: unknown) => {
    const ws = wsRef.current;
    const { pendingPrompt } = useExecutionStore.getState();

    if (!ws || !pendingPrompt) return;

    ws.send(
      JSON.stringify({
        type: `${pendingPrompt.type}_response`,
        value,
      }),
    );
    setPendingPrompt(null);
  }, [setPendingPrompt]);

  const execute = useCallback(
    async (
      workflow: string,
      inputs?: Record<string, unknown>,
      includeMetrics?: boolean,
    ) => {
      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close();
      }

      clearExecution();
      setIsExecuting(true);

      // Get WebSocket URL from provider
      const wsUrl = provider.getWebSocketUrl();

      // Fallback to REST execution if WebSocket not supported
      if (!wsUrl) {
        try {
          const result = await provider.executeWorkflow(
            workflow,
            inputs,
            includeMetrics,
          );
          if (result.success) {
            if (result.output) {
              appendExecutionOutput(result.output);
            }
            setExecutionResult(result.result);
          } else {
            setExecutionError(result.error || "Execution failed");
          }
        } catch (err) {
          setExecutionError(
            err instanceof Error ? err.message : "Execution failed",
          );
        } finally {
          setIsExecuting(false);
        }
        return;
      }

      // Use WebSocket for streaming execution
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        const message: ExecuteMessage = {
          type: "start",
          workflow,
          inputs,
          include_metrics: includeMetrics,
        };
        ws.send(JSON.stringify(message));
      };

      ws.onmessage = (event) => {
        try {
          const data: ServerMessage = JSON.parse(event.data);

          switch (data.type) {
            case "output":
              appendExecutionOutput(data.line + "\n");
              break;

            case "complete":
              setExecutionResult(data.result);
              setIsExecuting(false);
              // Don't auto-clear progress - let workflow control it via web_clear
              ws.close();
              break;

            case "error":
              setExecutionError(data.message);
              setIsExecuting(false);
              ws.close();
              break;

            // Web opcode messages
            case "input_request":
              setPendingPrompt({ type: "input", prompt: data.prompt });
              break;

            case "select_request":
              setPendingPrompt({
                type: "select",
                prompt: data.prompt,
                options: data.options,
              });
              break;

            case "confirm_request":
              setPendingPrompt({
                type: "confirm",
                prompt: data.message,
                message: data.message,
              });
              break;

            case "render_html":
              addRenderedContent({ type: "html", content: data.html });
              break;

            case "render_markdown":
              addRenderedContent({ type: "markdown", content: data.content });
              break;

            case "render_table":
              addRenderedContent({ type: "table", content: data.data });
              break;

            case "render_image":
              addRenderedContent({
                type: "image",
                content: { src: data.src, alt: data.alt },
              });
              break;

            case "progress":
              setProgress({
                value: data.value,
                max: data.max,
                label: data.label,
              });
              break;

            case "alert":
              addAlert({ message: data.message, variant: data.variant });
              break;

            case "clear_content":
              clearRenderedContent();
              break;
          }
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      ws.onerror = () => {
        setExecutionError("WebSocket connection failed");
        setIsExecuting(false);
      };

      ws.onclose = () => {
        wsRef.current = null;
      };
    },
    [
      provider,
      clearExecution,
      setIsExecuting,
      appendExecutionOutput,
      setExecutionResult,
      setExecutionError,
      setPendingPrompt,
      addRenderedContent,
      clearRenderedContent,
      addAlert,
      setProgress,
    ],
  );

  const cancel = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsExecuting(false);
      setPendingPrompt(null);
    }
  }, [setIsExecuting, setPendingPrompt]);

  return { execute, cancel, respondToPrompt };
}
