import React, { useState, useMemo, useRef, useEffect } from "react"
import type { OpcodeInterface } from "@/api/types"
import { getCategories, getCategoryByOpcode } from "@/services/grammar"
import { cn } from "@/lib/cn"
import {
  menuVariants,
  searchContainerVariants,
  searchInputVariants,
  contentVariants,
  noResultsVariants,
  categoryVariants,
  categoryHeaderVariants,
  categoryIconVariants,
  categoryLabelVariants,
  categoryCountVariants,
  expandIconVariants,
  categoryItemsVariants,
  opcodeItemVariants,
  opcodeNameVariants,
  opcodeRawVariants,
  opcodeDescVariants,
  searchResultItemVariants,
  highlightVariants,
} from "./styles"
import type { AddNodeMenuProps } from "./types"

// Menu dimensions for viewport adjustment (menu width: 320px, max-height: 480px + padding)
const MENU_WIDTH_WITH_PADDING = 340
const MENU_HEIGHT_WITH_PADDING = 500

export function AddNodeMenu({
  x,
  y,
  opcodes,
  onSelect,
  onClose,
}: AddNodeMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const [search, setSearch] = useState("")
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)

  const CATEGORIES = getCategories()

  // Focus search input on mount
  useEffect(() => {
    searchInputRef.current?.focus()
  }, [])

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose()
      }
    }

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose()
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    document.addEventListener("keydown", handleEscape)

    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
      document.removeEventListener("keydown", handleEscape)
    }
  }, [onClose])

  // Group opcodes by category
  const grouped = useMemo(() => {
    const groups: Record<string, OpcodeInterface[]> = {}
    for (const cat of CATEGORIES) {
      groups[cat.id] = []
    }
    groups["other"] = []

    for (const opcode of opcodes) {
      let matched = false
      for (const cat of CATEGORIES) {
        if (opcode.name.startsWith(cat.prefix)) {
          groups[cat.id].push(opcode)
          matched = true
          break
        }
      }
      if (!matched) {
        groups["other"].push(opcode)
      }
    }

    return groups
  }, [opcodes, CATEGORIES])

  // Filter opcodes based on search
  const filteredOpcodes = useMemo(() => {
    if (!search) return null
    const lower = search.toLowerCase()
    return opcodes.filter(
      (op) =>
        op.name.toLowerCase().includes(lower) ||
        (op.description?.toLowerCase().includes(lower) ?? false)
    )
  }, [opcodes, search])

  // Adjust position to stay within viewport
  const adjustedX = Math.min(x, window.innerWidth - MENU_WIDTH_WITH_PADDING)
  const adjustedY = Math.min(y, window.innerHeight - MENU_HEIGHT_WITH_PADDING)

  const handleSelect = (opcode: OpcodeInterface) => {
    onSelect(opcode)
    onClose()
  }

  // Generate formatDisplayName dynamically based on category prefixes
  const formatDisplayName = useMemo(() => {
    const prefixes = CATEGORIES.map((cat) => cat.prefix).join("|")
    const regex = new RegExp(`^(${prefixes}|workflow_)`)
    return (name: string): string => {
      return name
        .replace(regex, "")
        .split("_")
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ")
    }
  }, [CATEGORIES])

  const highlightText = (text: string, query: string): React.ReactNode => {
    if (!query) return <>{text}</>

    const lowerText = text.toLowerCase()
    const lowerQuery = query.toLowerCase()
    const index = lowerText.indexOf(lowerQuery)

    if (index === -1) return <>{text}</>

    return (
      <>
        {text.slice(0, index)}
        <span className={cn(highlightVariants())}>
          {text.slice(index, index + query.length)}
        </span>
        {text.slice(index + query.length)}
      </>
    )
  }

  // Reusable category section renderer
  const renderCategorySection = (
    categoryId: string,
    label: string,
    icon: string,
    color: string,
    categoryOpcodes: OpcodeInterface[]
  ) => {
    if (categoryOpcodes.length === 0) return null

    const isExpanded = expandedCategory === categoryId

    return (
      <div key={categoryId} className={cn(categoryVariants())}>
        <button
          className={cn(categoryHeaderVariants())}
          onClick={() =>
            setExpandedCategory(isExpanded ? null : categoryId)
          }
          style={{ "--cat-color": color } as React.CSSProperties}
        >
          <span className={cn(categoryIconVariants())}>{icon}</span>
          <span className={cn(categoryLabelVariants())}>{label}</span>
          <span className={cn(categoryCountVariants())}>
            {categoryOpcodes.length}
          </span>
          <span
            className={cn(expandIconVariants())}
            style={{
              transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)",
            }}
          >
            ▶
          </span>
        </button>

        {isExpanded && (
          <div className={cn(categoryItemsVariants())}>
            {categoryOpcodes.map((opcode) => (
              <button
                key={opcode.name}
                className={cn(opcodeItemVariants())}
                onClick={() => handleSelect(opcode)}
                role="menuitem"
              >
                <span className={cn(opcodeNameVariants())}>
                  {formatDisplayName(opcode.name)}
                </span>
                <span className={cn(opcodeRawVariants())}>{opcode.name}</span>
                {opcode.description && (
                  <span className={cn(opcodeDescVariants())}>
                    {opcode.description}
                  </span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div
      ref={menuRef}
      className={cn(menuVariants())}
      style={{
        position: "fixed",
        left: adjustedX,
        top: adjustedY,
        zIndex: 1000,
      }}
      role="menu"
      aria-label="Add node menu"
    >
      <div className={cn(searchContainerVariants())}>
        <input
          ref={searchInputRef}
          type="text"
          placeholder="Search opcodes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className={cn(searchInputVariants())}
        />
      </div>

      <div className={cn(contentVariants())}>
        {filteredOpcodes ? (
          <>
            {filteredOpcodes.length === 0 ? (
              <p className={cn(noResultsVariants())}>No opcodes found</p>
            ) : (
              filteredOpcodes.map((opcode) => {
                const category = getCategoryByOpcode(opcode.name)
                return (
                  <button
                    key={opcode.name}
                    className={cn(searchResultItemVariants())}
                    onClick={() => handleSelect(opcode)}
                    role="menuitem"
                    style={
                      category
                        ? ({ "--cat-color": category.color } as React.CSSProperties)
                        : undefined
                    }
                  >
                    <div className="flex items-center gap-2 w-full">
                      {category && (
                        <span className={cn(categoryIconVariants())}>
                          {category.icon}
                        </span>
                      )}
                      <span className={cn(opcodeNameVariants())}>
                        {highlightText(formatDisplayName(opcode.name), search)}
                      </span>
                    </div>
                    <span className={cn(opcodeRawVariants())}>
                      {highlightText(opcode.name, search)}
                    </span>
                    {opcode.description && (
                      <span className={cn(opcodeDescVariants())}>
                        {highlightText(opcode.description, search)}
                      </span>
                    )}
                  </button>
                )
              })
            )}
          </>
        ) : (
          <>
            {CATEGORIES.map((cat) =>
              renderCategorySection(
                cat.id,
                cat.label,
                cat.icon,
                cat.color,
                grouped[cat.id]
              )
            )}
            {renderCategorySection(
              "other",
              "Other",
              "⚙",
              "#64748B",
              grouped["other"]
            )}
          </>
        )}
      </div>
    </div>
  )
}
