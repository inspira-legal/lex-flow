// UI state management with Zustand

import { create } from 'zustand'
import type { FormattedValue, OpcodeInterface } from '../api/types'

// Reporter selection info
export interface SelectedReporter {
  parentNodeId: string
  inputPath: string[] // Path to reach this reporter (e.g., ['condition'] or ['condition', 'left'])
  opcode: string
  inputs: Record<string, FormattedValue>
}

interface UiState {
  // Canvas
  zoom: number
  panX: number
  panY: number
  isDraggingWorkflow: boolean
  setZoom: (zoom: number) => void
  setPan: (x: number, y: number) => void
  resetView: () => void
  setIsDraggingWorkflow: (dragging: boolean) => void

  // Panels
  isEditorOpen: boolean
  isNodeEditorOpen: boolean
  isPaletteOpen: boolean
  isExecutionPanelOpen: boolean
  toggleEditor: () => void
  toggleNodeEditor: () => void
  togglePalette: () => void
  toggleExecutionPanel: () => void
  openNodeEditor: () => void
  closeNodeEditor: () => void

  // Node execution status (for visualization)
  nodeStatus: Record<string, 'idle' | 'running' | 'success' | 'error'>
  setNodeStatus: (nodeId: string, status: 'idle' | 'running' | 'success' | 'error') => void
  clearNodeStatuses: () => void

  // Node search
  searchQuery: string
  searchResults: string[]
  setSearchQuery: (query: string) => void
  setSearchResults: (results: string[]) => void

  // Workflow positions (for dragging)
  workflowPositions: Record<string, { x: number; y: number }>
  setWorkflowPosition: (name: string, x: number, y: number) => void
  resetWorkflowPositions: () => void

  // Selected reporter
  selectedReporter: SelectedReporter | null
  selectReporter: (reporter: SelectedReporter | null) => void

  // Drag-drop from palette
  draggingOpcode: OpcodeInterface | null
  setDraggingOpcode: (opcode: OpcodeInterface | null) => void
}

export const useUiStore = create<UiState>((set) => ({
  // Canvas
  zoom: 1,
  panX: 0,
  panY: 0,
  isDraggingWorkflow: false,
  setZoom: (zoom) => set({ zoom: Math.max(0.25, Math.min(2, zoom)) }),
  setPan: (x, y) => set({ panX: x, panY: y }),
  resetView: () => set({ zoom: 1, panX: 0, panY: 0 }),
  setIsDraggingWorkflow: (dragging) => set({ isDraggingWorkflow: dragging }),

  // Panels
  isEditorOpen: true,
  isNodeEditorOpen: false,
  isPaletteOpen: false,
  isExecutionPanelOpen: true,
  toggleEditor: () => set((s) => ({ isEditorOpen: !s.isEditorOpen })),
  toggleNodeEditor: () => set((s) => ({ isNodeEditorOpen: !s.isNodeEditorOpen })),
  togglePalette: () => set((s) => ({ isPaletteOpen: !s.isPaletteOpen })),
  toggleExecutionPanel: () => set((s) => ({ isExecutionPanelOpen: !s.isExecutionPanelOpen })),
  openNodeEditor: () => set({ isNodeEditorOpen: true }),
  closeNodeEditor: () => set({ isNodeEditorOpen: false }),

  // Node status
  nodeStatus: {},
  setNodeStatus: (nodeId, status) =>
    set((s) => ({ nodeStatus: { ...s.nodeStatus, [nodeId]: status } })),
  clearNodeStatuses: () => set({ nodeStatus: {} }),

  // Node search
  searchQuery: '',
  searchResults: [],
  setSearchQuery: (query) => set({ searchQuery: query }),
  setSearchResults: (results) => set({ searchResults: results }),

  // Workflow positions
  workflowPositions: {},
  setWorkflowPosition: (name, x, y) =>
    set((s) => ({ workflowPositions: { ...s.workflowPositions, [name]: { x, y } } })),
  resetWorkflowPositions: () => set({ workflowPositions: {} }),

  // Selected reporter
  selectedReporter: null,
  selectReporter: (reporter) =>
    set({ selectedReporter: reporter, ...(reporter ? { isNodeEditorOpen: true } : {}) }),

  // Drag-drop from palette
  draggingOpcode: null,
  setDraggingOpcode: (opcode) => set({ draggingOpcode: opcode }),
}))
