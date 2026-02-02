import { useRef, useState } from "react"
import { useWorkflowStore, useUiStore } from "@/store"
import { cn } from "@/lib/cn"
import { IconButton } from "@/components/ui"
import {
  FileIcon,
  UploadIcon,
  DownloadIcon,
  SaveIcon,
  UndoIcon,
  RedoIcon,
  PlusIcon,
  CodeIcon,
} from "@/components/icons"
import { ThemeToggle } from "@/components/layout/ThemeToggle"
import { ExamplesSelect } from "./ExamplesSelect"
import {
  headerVariants,
  logoVariants,
  dividerVariants,
  sectionVariants,
} from "./styles"
import {
  extractMetadata,
  injectMetadata,
  createMetadataFromState,
} from "@/services/metadata"
import type { HeaderProps } from "./types"

const DEFAULT_WORKFLOW = `workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        next: hello
      hello:
        opcode: io_print
        inputs:
          MESSAGE: { literal: "Hello, LexFlow!" }
`

export function Header({
  className,
  onSave,
  showSaveButton,
  saveButtonLabel = "Save",
  showExamples,
}: HeaderProps) {
  const { source, setSource, undo, redo, canUndo, canRedo } = useWorkflowStore()
  const { togglePalette, toggleEditor, isEditorOpen } = useUiStore()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    if (!onSave || isSaving) return
    setIsSaving(true)
    try {
      const { nodePositions, workflowPositions, layoutMode, zoom, panX, panY } =
        useUiStore.getState()

      const metadata = createMetadataFromState(
        layoutMode,
        nodePositions,
        workflowPositions,
        zoom,
        panX,
        panY
      )

      await onSave(source, metadata)
    } finally {
      setIsSaving(false)
    }
  }

  // Show save button if explicitly enabled, or if onSave is provided and not explicitly disabled
  const shouldShowSaveButton = showSaveButton ?? !!onSave

  const handleNew = () => {
    if (source !== DEFAULT_WORKFLOW) {
      useUiStore.getState().showConfirmDialog({
        title: "New Workflow",
        message: "Create a new workflow? Unsaved changes will be lost.",
        confirmLabel: "Create",
        variant: "default",
        onConfirm: () => setSource(DEFAULT_WORKFLOW),
      })
    }
  }

  const handleExport = async () => {
    const { nodePositions, workflowPositions, layoutMode, zoom, panX, panY } =
      useUiStore.getState()

    const metadata = createMetadataFromState(
      layoutMode,
      nodePositions,
      workflowPositions,
      zoom,
      panX,
      panY
    )

    const sourceWithMetadata = injectMetadata(source, metadata)
    const blob = new Blob([sourceWithMetadata], { type: "text/yaml" })

    if ("showSaveFilePicker" in window) {
      try {
        const handle = await (window as any).showSaveFilePicker({
          suggestedName: "workflow.yaml",
          types: [
            {
              description: "YAML files",
              accept: { "text/yaml": [".yaml", ".yml"] },
            },
          ],
        })
        const writable = await handle.createWritable()
        await writable.write(blob)
        await writable.close()
        return
      } catch (err) {
        if ((err as Error).name === "AbortError") return
      }
    }

    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "workflow.yaml"
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleImport = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const content = event.target?.result as string
      const metadata = extractMetadata(content)

      setSource(content)

      if (metadata) {
        const ui = useUiStore.getState()

        ui.resetNodePositions()
        ui.resetWorkflowPositions()
        ui.setLayoutMode(metadata.layout.mode)

        for (const [id, pos] of Object.entries(metadata.layout.nodePositions)) {
          ui.setNodePosition(id, pos.x, pos.y)
        }
        for (const [name, pos] of Object.entries(
          metadata.layout.workflowPositions
        )) {
          ui.setWorkflowPosition(name, pos.x, pos.y)
        }

        ui.setZoom(metadata.viewport.zoom)
        ui.setPan(metadata.viewport.panX, metadata.viewport.panY)
      }
    }
    reader.readAsText(file)
    e.target.value = ""
  }

  return (
    <header className={cn(headerVariants(), className)}>
      {/* Left section */}
      <div className={cn(sectionVariants(), "flex-1")}>
        <h1 className={logoVariants()} style={{ marginLeft: '8px' }}>LexFlow</h1>
        <div className={dividerVariants()} />

        <IconButton
          icon={<FileIcon />}
          label="New Workflow"
          onClick={handleNew}
        />
        <IconButton
          icon={<UploadIcon />}
          label="Import Workflow"
          onClick={handleImport}
        />
        <IconButton
          icon={<DownloadIcon />}
          label="Export Workflow"
          onClick={handleExport}
        />
        {shouldShowSaveButton && onSave && (
          <IconButton
            icon={<SaveIcon />}
            label={saveButtonLabel}
            onClick={handleSave}
            disabled={isSaving}
          />
        )}

        <div className={dividerVariants()} />

        <IconButton
          icon={<UndoIcon />}
          label="Undo (Ctrl+Z)"
          onClick={undo}
          disabled={!canUndo}
        />
        <IconButton
          icon={<RedoIcon />}
          label="Redo (Ctrl+Y)"
          onClick={redo}
          disabled={!canRedo}
        />

        <div className={dividerVariants()} />

        <IconButton
          icon={<PlusIcon />}
          label="Node Palette (Ctrl+P)"
          onClick={togglePalette}
        />

        <input
          ref={fileInputRef}
          type="file"
          accept=".yaml,.yml,.json"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* Center section */}
      <div className="flex items-center justify-center">
        {showExamples !== false && <ExamplesSelect />}
      </div>

      {/* Right section */}
      <div className={cn(sectionVariants(), "flex-1 justify-end")}>
        <ThemeToggle />
        <IconButton
          icon={<CodeIcon />}
          label="Toggle Editor (Ctrl+B)"
          onClick={toggleEditor}
          className={isEditorOpen ? "bg-surface-3" : ""}
        />
      </div>
    </header>
  )
}
