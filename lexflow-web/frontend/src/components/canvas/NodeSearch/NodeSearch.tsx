import { useState, useCallback, useEffect, useRef } from "react"
import { useWorkflowStore, useUiStore, useSelectionStore } from "@/store"
import { cn } from "@/lib/cn"
import {
  searchButtonVariants,
  searchBarVariants,
  inputVariants,
  resultCountVariants,
  navButtonsVariants,
  navBtnVariants,
  closeBtnVariants,
} from "./styles"

export function NodeSearch() {
  const { tree } = useWorkflowStore()
  const { searchQuery, setSearchQuery, searchResults, setSearchResults } = useUiStore()
  const { selectNode } = useSelectionStore()
  const [isOpen, setIsOpen] = useState(false)
  const [currentResultIndex, setCurrentResultIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  // Find matching nodes when search query changes
  useEffect(() => {
    if (!tree || !searchQuery.trim()) {
      setSearchResults([])
      setCurrentResultIndex(0)
      return
    }

    const query = searchQuery.toLowerCase()
    const results: string[] = []

    // Search through all workflows and nodes
    for (const workflow of tree.workflows) {
      const searchNodes = (children: typeof workflow.children) => {
        for (const node of children) {
          const matchesId = node.id.toLowerCase().includes(query)
          const matchesOpcode = node.opcode?.toLowerCase().includes(query)
          const matchesType = node.type.toLowerCase().includes(query)

          if (matchesId || matchesOpcode || matchesType) {
            results.push(node.id)
          }

          // Search branch children
          for (const branch of node.children) {
            searchNodes(branch.children)
          }
        }
      }
      searchNodes(workflow.children)
    }

    setSearchResults(results)
    setCurrentResultIndex(0)
  }, [searchQuery, tree, setSearchResults])

  // Keyboard shortcut to open search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + F to open search
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "f") {
        const target = e.target as HTMLElement
        const isMonaco = target.closest(".monaco-editor")
        if (!isMonaco) {
          e.preventDefault()
          setIsOpen(true)
          setTimeout(() => inputRef.current?.focus(), 50)
        }
      }

      // Escape to close search
      if (e.key === "Escape" && isOpen) {
        handleClose()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen])

  const handleClose = useCallback(() => {
    setIsOpen(false)
    setSearchQuery("")
    setSearchResults([])
    setCurrentResultIndex(0)
  }, [setSearchQuery, setSearchResults])

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setSearchQuery(e.target.value)
    },
    [setSearchQuery]
  )

  const navigateToResult = useCallback(
    (index: number) => {
      if (searchResults.length > 0) {
        const nodeId = searchResults[index]
        selectNode(nodeId)
        setCurrentResultIndex(index)
      }
    },
    [searchResults, selectNode]
  )

  const handlePrevious = useCallback(() => {
    if (searchResults.length > 0) {
      const newIndex =
        currentResultIndex > 0 ? currentResultIndex - 1 : searchResults.length - 1
      navigateToResult(newIndex)
    }
  }, [currentResultIndex, searchResults.length, navigateToResult])

  const handleNext = useCallback(() => {
    if (searchResults.length > 0) {
      const newIndex =
        currentResultIndex < searchResults.length - 1 ? currentResultIndex + 1 : 0
      navigateToResult(newIndex)
    }
  }, [currentResultIndex, searchResults.length, navigateToResult])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        if (e.shiftKey) {
          handlePrevious()
        } else {
          handleNext()
        }
      }
    },
    [handlePrevious, handleNext]
  )

  if (!isOpen) {
    return (
      <button
        className={cn(searchButtonVariants())}
        onClick={() => {
          setIsOpen(true)
          setTimeout(() => inputRef.current?.focus(), 50)
        }}
        aria-label="Search nodes (Ctrl+F)"
      >
        <SearchIcon />
      </button>
    )
  }

  return (
    <div className={cn(searchBarVariants())} role="search" aria-label="Search nodes">
      <SearchIcon />
      <input
        ref={inputRef}
        type="text"
        value={searchQuery}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder="Search nodes..."
        className={cn(inputVariants())}
        autoFocus
        aria-label="Search query"
        aria-describedby={searchQuery ? "search-result-count" : undefined}
      />
      {searchQuery && (
        <span id="search-result-count" className={cn(resultCountVariants())} aria-live="polite">
          {searchResults.length > 0
            ? `${currentResultIndex + 1}/${searchResults.length}`
            : "No results"}
        </span>
      )}
      <div className={cn(navButtonsVariants())} role="group" aria-label="Navigate results">
        <button
          onClick={handlePrevious}
          disabled={searchResults.length === 0}
          aria-label="Previous result (Shift+Enter)"
          className={cn(navBtnVariants())}
        >
          <ChevronUpIcon />
        </button>
        <button
          onClick={handleNext}
          disabled={searchResults.length === 0}
          aria-label="Next result (Enter)"
          className={cn(navBtnVariants())}
        >
          <ChevronDownIcon />
        </button>
      </div>
      <button
        onClick={handleClose}
        className={cn(closeBtnVariants())}
        aria-label="Close search (Escape)"
      >
        <CloseIcon />
      </button>
    </div>
  )
}

function SearchIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="M21 21l-4.35-4.35" />
    </svg>
  )
}

function ChevronUpIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <path d="M18 15l-6-6-6 6" />
    </svg>
  )
}

function ChevronDownIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <path d="M6 9l6 6 6-6" />
    </svg>
  )
}

function CloseIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <path d="M18 6L6 18M6 6l12 12" />
    </svg>
  )
}
