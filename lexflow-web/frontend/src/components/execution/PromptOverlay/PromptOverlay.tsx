import { useState, useEffect, useRef } from "react"
import type { PendingPrompt } from "@/store/executionStore"
import { cn } from "@/lib/cn"
import {
  overlayVariants,
  cardVariants,
  promptTextVariants,
  inputVariants,
  selectVariants,
  actionsVariants,
  submitBtnVariants,
  cancelBtnVariants,
  buttonPromptVariants,
  actionButtonVariants,
} from "./styles"

interface PromptOverlayProps {
  prompt: PendingPrompt
  onSubmit: (value: unknown) => void
}

export function PromptOverlay({ prompt, onSubmit }: PromptOverlayProps) {
  const [inputValue, setInputValue] = useState("")
  const [selectValue, setSelectValue] = useState(prompt.options?.[0] || "")
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-focus input when opened
  useEffect(() => {
    if (prompt.type === "input" && inputRef.current) {
      inputRef.current.focus()
    }
  }, [prompt.type])

  // Reset state when prompt changes
  useEffect(() => {
    setInputValue("")
    if (prompt.options?.length) {
      setSelectValue(prompt.options[0])
    }
  }, [prompt])

  const handleInputSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(inputValue)
  }

  const handleSelectSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(selectValue)
  }

  const handleConfirm = (value: boolean) => {
    onSubmit(value)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      // For confirm, treat Escape as "No"
      if (prompt.type === "confirm") {
        onSubmit(false)
      }
    }
  }

  return (
    <div className={cn(overlayVariants())} onKeyDown={handleKeyDown} role="presentation">
      <div
        className={cn(cardVariants())}
        role="dialog"
        aria-modal="true"
        aria-labelledby="prompt-label"
      >
        {prompt.type === "input" && (
          <form onSubmit={handleInputSubmit}>
            <label id="prompt-label" htmlFor="prompt-input" className={cn(promptTextVariants())}>
              {prompt.prompt || "Enter a value:"}
            </label>
            <input
              ref={inputRef}
              id="prompt-input"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className={cn(inputVariants())}
              placeholder="Type here..."
            />
            <div className={cn(actionsVariants())}>
              <button type="submit" className={cn(submitBtnVariants())}>
                Submit
              </button>
            </div>
          </form>
        )}

        {prompt.type === "select" && (
          <form onSubmit={handleSelectSubmit}>
            <label id="prompt-label" htmlFor="prompt-select" className={cn(promptTextVariants())}>
              {prompt.prompt || "Select an option:"}
            </label>
            <select
              id="prompt-select"
              value={selectValue}
              onChange={(e) => setSelectValue(e.target.value)}
              className={cn(selectVariants())}
            >
              {prompt.options?.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            <div className={cn(actionsVariants())}>
              <button type="submit" className={cn(submitBtnVariants())}>
                Select
              </button>
            </div>
          </form>
        )}

        {prompt.type === "confirm" && (
          <div>
            <p id="prompt-label" className={cn(promptTextVariants())}>
              {prompt.message || prompt.prompt || "Are you sure?"}
            </p>
            <div className={cn(actionsVariants())}>
              <button className={cn(cancelBtnVariants())} onClick={() => handleConfirm(false)}>
                No
              </button>
              <button
                className={cn(submitBtnVariants())}
                onClick={() => handleConfirm(true)}
                autoFocus
              >
                Yes
              </button>
            </div>
          </div>
        )}

        {prompt.type === "button" && (
          <div className={cn(buttonPromptVariants())}>
            <button
              id="prompt-label"
              className={cn(actionButtonVariants())}
              onClick={() => onSubmit(true)}
              autoFocus
            >
              {prompt.label || "Click"}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
