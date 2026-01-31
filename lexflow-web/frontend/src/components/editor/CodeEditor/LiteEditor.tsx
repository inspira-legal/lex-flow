// Lightweight textarea-based code editor for lite mode (no Monaco)

import { useCallback, useRef, useEffect, type ChangeEvent, type KeyboardEvent } from "react";
import { cn } from "@/lib/cn";
import {
  editorContainerVariants,
  editorHeaderVariants,
  editorTitleVariants,
  editorStatusVariants,
  editorWrapperVariants,
} from "./styles";
import type { CodeEditorProps } from "./types";

interface LiteEditorProps extends CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  isParsing?: boolean;
}

export function LiteEditor({ className, value, onChange, isParsing }: LiteEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumbersRef = useRef<HTMLDivElement>(null);

  // Handle tab key for indentation
  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newValue = value.substring(0, start) + "  " + value.substring(end);
      onChange(newValue);
      // Set cursor position after the tab
      requestAnimationFrame(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2;
      });
    }
  }, [value, onChange]);

  const handleChange = useCallback((e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  }, [onChange]);

  // Sync scroll between textarea and line numbers
  const handleScroll = useCallback(() => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  }, []);

  // Listen for goto-line events
  useEffect(() => {
    const handleGotoLine = (e: CustomEvent<{ line: number }>) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      const lines = value.split("\n");
      const targetLine = Math.min(Math.max(1, e.detail.line), lines.length);

      // Calculate position
      let pos = 0;
      for (let i = 0; i < targetLine - 1; i++) {
        pos += lines[i].length + 1;
      }

      textarea.focus();
      textarea.setSelectionRange(pos, pos);

      // Scroll to line
      const lineHeight = 20; // Approximate
      textarea.scrollTop = (targetLine - 1) * lineHeight - textarea.clientHeight / 2;
    };

    window.addEventListener("lexflow:goto-line", handleGotoLine as EventListener);
    return () => {
      window.removeEventListener("lexflow:goto-line", handleGotoLine as EventListener);
    };
  }, [value]);

  // Calculate line numbers
  const lineCount = value.split("\n").length;
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1);

  return (
    <div className={cn(editorContainerVariants(), className)}>
      <div className={editorHeaderVariants()}>
        <span className={editorTitleVariants()}>Editor</span>
        {isParsing && <span className={editorStatusVariants()}>Parsing...</span>}
      </div>
      <div className={cn(editorWrapperVariants(), "flex")}>
        {/* Line numbers */}
        <div
          ref={lineNumbersRef}
          className="flex-none w-12 bg-surface-1 text-text-muted text-sm font-mono text-right py-2 pr-2 overflow-hidden select-none"
          style={{ lineHeight: "20px" }}
        >
          {lineNumbers.map((num) => (
            <div key={num}>{num}</div>
          ))}
        </div>
        {/* Editor textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onScroll={handleScroll}
          spellCheck={false}
          className={cn(
            "flex-1 resize-none p-2",
            "bg-surface-0 text-text-primary",
            "font-mono text-sm",
            "border-none outline-none",
            "focus:ring-0 focus:outline-none"
          )}
          style={{
            lineHeight: "20px",
            tabSize: 2,
          }}
        />
      </div>
    </div>
  );
}
