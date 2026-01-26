import { useState, useEffect, useRef } from "react";
import type { PendingPrompt } from "../../store/executionStore";
import styles from "./PromptOverlay.module.css";

interface PromptOverlayProps {
  prompt: PendingPrompt;
  onSubmit: (value: unknown) => void;
}

export function PromptOverlay({ prompt, onSubmit }: PromptOverlayProps) {
  const [inputValue, setInputValue] = useState("");
  const [selectValue, setSelectValue] = useState(prompt.options?.[0] || "");
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-focus input when opened
  useEffect(() => {
    if (prompt.type === "input" && inputRef.current) {
      inputRef.current.focus();
    }
  }, [prompt.type]);

  // Reset state when prompt changes
  useEffect(() => {
    setInputValue("");
    if (prompt.options?.length) {
      setSelectValue(prompt.options[0]);
    }
  }, [prompt]);

  const handleInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(inputValue);
  };

  const handleSelectSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(selectValue);
  };

  const handleConfirm = (value: boolean) => {
    onSubmit(value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      // For confirm, treat Escape as "No"
      if (prompt.type === "confirm") {
        onSubmit(false);
      }
    }
  };

  return (
    <div className={styles.overlay} onKeyDown={handleKeyDown}>
      <div className={styles.card}>
        {prompt.type === "input" && (
          <form onSubmit={handleInputSubmit}>
            <label className={styles.promptText}>
              {prompt.prompt || "Enter a value:"}
            </label>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className={styles.input}
              placeholder="Type here..."
            />
            <div className={styles.actions}>
              <button type="submit" className={styles.submitBtn}>
                Submit
              </button>
            </div>
          </form>
        )}

        {prompt.type === "select" && (
          <form onSubmit={handleSelectSubmit}>
            <label className={styles.promptText}>
              {prompt.prompt || "Select an option:"}
            </label>
            <select
              value={selectValue}
              onChange={(e) => setSelectValue(e.target.value)}
              className={styles.select}
            >
              {prompt.options?.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            <div className={styles.actions}>
              <button type="submit" className={styles.submitBtn}>
                Select
              </button>
            </div>
          </form>
        )}

        {prompt.type === "confirm" && (
          <div>
            <p className={styles.promptText}>
              {prompt.message || prompt.prompt || "Are you sure?"}
            </p>
            <div className={styles.actions}>
              <button
                className={styles.cancelBtn}
                onClick={() => handleConfirm(false)}
              >
                No
              </button>
              <button
                className={styles.submitBtn}
                onClick={() => handleConfirm(true)}
                autoFocus
              >
                Yes
              </button>
            </div>
          </div>
        )}

        {prompt.type === "button" && (
          <div className={styles.buttonPrompt}>
            <button
              className={styles.actionButton}
              onClick={() => onSubmit(true)}
              autoFocus
            >
              {prompt.label || "Click"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
