// Workflow state management with Zustand

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { WorkflowTree, ExampleInfo, OpcodeInterface } from '../api/types'

const MAX_HISTORY = 50

interface WorkflowState {
  // Source code
  source: string
  setSource: (source: string, addToHistory?: boolean) => void

  // History for undo/redo
  history: string[]
  historyIndex: number
  canUndo: boolean
  canRedo: boolean
  undo: () => void
  redo: () => void

  // Parsed tree
  tree: WorkflowTree | null
  parseError: string | null
  isParsing: boolean
  setTree: (tree: WorkflowTree | null) => void
  setParseError: (error: string | null) => void
  setIsParsing: (isParsing: boolean) => void

  // Selection
  selectedNodeId: string | null
  selectNode: (id: string | null) => void

  // Node operations
  deleteNode: (nodeId: string) => boolean
  addNode: (opcode: OpcodeInterface, workflowName?: string) => string | null
  duplicateNode: (nodeId: string) => string | null
  updateNodeInput: (nodeId: string, inputKey: string, newValue: string) => boolean

  // Examples
  examples: ExampleInfo[]
  setExamples: (examples: ExampleInfo[]) => void

  // Opcodes catalog
  opcodes: OpcodeInterface[]
  setOpcodes: (opcodes: OpcodeInterface[]) => void

  // Execution
  isExecuting: boolean
  executionOutput: string
  executionResult: unknown
  executionError: string | null
  setIsExecuting: (isExecuting: boolean) => void
  setExecutionOutput: (output: string) => void
  appendExecutionOutput: (chunk: string) => void
  setExecutionResult: (result: unknown) => void
  setExecutionError: (error: string | null) => void
  clearExecution: () => void

  // Inputs for execution
  workflowInputs: Record<string, unknown>
  setWorkflowInput: (key: string, value: unknown) => void
  clearWorkflowInputs: () => void
}

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

export const useWorkflowStore = create<WorkflowState>()(
  persist(
    (set, get) => ({
      // Source
      source: DEFAULT_WORKFLOW,
      setSource: (source, addToHistory = true) => {
        const state = get()
        if (addToHistory && source !== state.source) {
          // Add to history
          const newHistory = state.history.slice(0, state.historyIndex + 1)
          newHistory.push(source)
          // Limit history size
          if (newHistory.length > MAX_HISTORY) {
            newHistory.shift()
          }
          set({
            source,
            history: newHistory,
            historyIndex: newHistory.length - 1,
            canUndo: newHistory.length > 1,
            canRedo: false,
          })
        } else {
          set({ source })
        }
      },

      // History
      history: [DEFAULT_WORKFLOW],
      historyIndex: 0,
      canUndo: false,
      canRedo: false,

      undo: () => {
        const state = get()
        if (state.historyIndex > 0) {
          const newIndex = state.historyIndex - 1
          set({
            source: state.history[newIndex],
            historyIndex: newIndex,
            canUndo: newIndex > 0,
            canRedo: true,
          })
        }
      },

      redo: () => {
        const state = get()
        if (state.historyIndex < state.history.length - 1) {
          const newIndex = state.historyIndex + 1
          set({
            source: state.history[newIndex],
            historyIndex: newIndex,
            canUndo: true,
            canRedo: newIndex < state.history.length - 1,
          })
        }
      },

      // Parsed tree
      tree: null,
      parseError: null,
      isParsing: false,
      setTree: (tree) => set({ tree, parseError: null }),
      setParseError: (error) => set({ parseError: error, tree: null }),
      setIsParsing: (isParsing) => set({ isParsing }),

      // Selection
      selectedNodeId: null,
      selectNode: (id) => set({ selectedNodeId: id }),

      // Node operations
      deleteNode: (nodeId) => {
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the node's starting line (looks for "  nodeId:" pattern under nodes:)
        let nodeStartLine = -1
        let nodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]
          // Match node ID at start of a block (after whitespace)
          const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match && match[2] === nodeId) {
            nodeStartLine = i
            nodeIndent = match[1].length
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`Node "${nodeId}" not found in source`)
          return false
        }

        // Find where the node block ends (next line with same or less indent that's not empty)
        let nodeEndLine = nodeStartLine + 1
        while (nodeEndLine < lines.length) {
          const line = lines[nodeEndLine]
          // Empty lines or comments continue the block
          if (line.trim() === '' || line.trim().startsWith('#')) {
            nodeEndLine++
            continue
          }
          // Check indent
          const currentIndent = line.search(/\S/)
          if (currentIndent !== -1 && currentIndent <= nodeIndent) {
            break
          }
          nodeEndLine++
        }

        // Remove the node lines
        const newLines = [...lines.slice(0, nodeStartLine), ...lines.slice(nodeEndLine)]
        const newSource = newLines.join('\n')

        // Update source (which adds to history)
        state.setSource(newSource)

        // Deselect the node
        set({ selectedNodeId: null })

        return true
      },

      // Add a new node to a workflow
      addNode: (opcode, workflowName = 'main') => {
        console.log('[addNode] Starting with opcode:', opcode.name, 'workflow:', workflowName)
        const state = get()
        const { source } = state
        const lines = source.split('\n')
        console.log('[addNode] Source lines:', lines.length)

        // Find the nodes: section for the target workflow
        let inTargetWorkflow = false
        let nodesLineIndex = -1
        let nodesIndent = -1
        let lastNodeEndIndex = -1
        let lastNodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]

          // Detect workflow name
          const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/)
          if (nameMatch) {
            inTargetWorkflow = nameMatch[1] === workflowName
          }

          // Find nodes: in target workflow
          if (inTargetWorkflow) {
            const nodesMatch = line.match(/^(\s*)nodes:\s*$/)
            if (nodesMatch) {
              nodesLineIndex = i
              nodesIndent = nodesMatch[1].length
              continue
            }

            // Track nodes within the nodes section
            if (nodesLineIndex !== -1) {
              const nodeIdMatch = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
              if (nodeIdMatch) {
                const indent = nodeIdMatch[1].length
                // Node definition is at nodesIndent + 2
                if (indent === nodesIndent + 2) {
                  lastNodeIndent = indent
                  // Find where this node ends
                  let j = i + 1
                  while (j < lines.length) {
                    const nextLine = lines[j]
                    if (nextLine.trim() === '' || nextLine.trim().startsWith('#')) {
                      j++
                      continue
                    }
                    const nextIndent = nextLine.search(/\S/)
                    if (nextIndent !== -1 && nextIndent <= indent) {
                      break
                    }
                    j++
                  }
                  lastNodeEndIndex = j
                }
              }
            }
          }
        }

        console.log('[addNode] Found nodes at line:', nodesLineIndex, 'indent:', nodesIndent)
        console.log('[addNode] Last node ends at:', lastNodeEndIndex, 'indent:', lastNodeIndent)

        if (nodesLineIndex === -1) {
          console.warn(`nodes: section not found for workflow "${workflowName}"`)
          return null
        }

        // Generate unique node ID
        const prefix = opcode.name.split('_')[0]
        const existingIds = new Set<string>()
        for (const line of lines) {
          const match = line.match(/^\s+([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match) existingIds.add(match[1])
        }

        let newId = `${prefix}_1`
        let counter = 1
        while (existingIds.has(newId)) {
          counter++
          newId = `${prefix}_${counter}`
        }

        // Build YAML snippet for new node
        const indent = ' '.repeat(lastNodeIndent !== -1 ? lastNodeIndent : nodesIndent + 2)
        const inputIndent = indent + '  '
        const valueIndent = inputIndent + '  '

        let nodeYaml = `${indent}${newId}:\n`
        nodeYaml += `${inputIndent}opcode: ${opcode.name}\n`
        nodeYaml += `${inputIndent}next: null\n`

        // Add inputs section with default values
        if (opcode.parameters.length > 0) {
          nodeYaml += `${inputIndent}inputs:\n`
          for (const param of opcode.parameters) {
            const paramName = param.name.toUpperCase()
            const defaultValue = param.default !== undefined ? JSON.stringify(param.default) : '""'
            nodeYaml += `${valueIndent}${paramName}: { literal: ${defaultValue} }\n`
          }
        }

        // Insert after the last node, or right after nodes: if no nodes exist
        const insertIndex = lastNodeEndIndex !== -1 ? lastNodeEndIndex : nodesLineIndex + 1
        console.log('[addNode] Insert index:', insertIndex)
        console.log('[addNode] New node YAML:\n', nodeYaml)

        const newLines = [...lines.slice(0, insertIndex), nodeYaml.trimEnd(), ...lines.slice(insertIndex)]
        const newSource = newLines.join('\n')

        console.log('[addNode] Calling setSource with new source length:', newSource.length)
        state.setSource(newSource)
        set({ selectedNodeId: newId })

        console.log('[addNode] Done, returning new ID:', newId)
        return newId
      },

      // Duplicate an existing node
      duplicateNode: (nodeId) => {
        console.log('[duplicateNode] Starting with nodeId:', nodeId)
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the node's starting line
        let nodeStartLine = -1
        let nodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]
          const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match && match[2] === nodeId) {
            nodeStartLine = i
            nodeIndent = match[1].length
            console.log('[duplicateNode] Found node at line:', i, 'indent:', nodeIndent)
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`[duplicateNode] Node "${nodeId}" not found in source`)
          return null
        }

        // Find where the node block ends
        let nodeEndLine = nodeStartLine + 1
        while (nodeEndLine < lines.length) {
          const line = lines[nodeEndLine]
          if (line.trim() === '' || line.trim().startsWith('#')) {
            nodeEndLine++
            continue
          }
          const currentIndent = line.search(/\S/)
          if (currentIndent !== -1 && currentIndent <= nodeIndent) {
            break
          }
          nodeEndLine++
        }

        console.log('[duplicateNode] Node ends at line:', nodeEndLine)

        // Extract node lines
        const nodeLines = lines.slice(nodeStartLine, nodeEndLine)
        console.log('[duplicateNode] Extracted lines:', nodeLines)

        // Generate new ID
        const existingIds = new Set<string>()
        for (const line of lines) {
          const match = line.match(/^\s+([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match) existingIds.add(match[1])
        }

        let newId = `${nodeId}_copy`
        let counter = 1
        while (existingIds.has(newId)) {
          counter++
          newId = `${nodeId}_copy_${counter}`
        }

        // Modify the first line to use new ID and set next: null
        const newNodeLines = [...nodeLines]
        newNodeLines[0] = newNodeLines[0].replace(nodeId + ':', newId + ':')
        console.log('[duplicateNode] New ID:', newId)

        // Replace next: <something> with next: null
        for (let i = 1; i < newNodeLines.length; i++) {
          if (newNodeLines[i].match(/^\s+next:\s*\S/)) {
            const indent = newNodeLines[i].match(/^(\s+)next:/)?.[1] || '        '
            newNodeLines[i] = `${indent}next: null`
          }
        }

        console.log('[duplicateNode] New node lines:', newNodeLines)

        // Insert after the original node
        const newLines = [
          ...lines.slice(0, nodeEndLine),
          ...newNodeLines,
          ...lines.slice(nodeEndLine),
        ]
        const newSource = newLines.join('\n')

        console.log('[duplicateNode] Calling setSource, new length:', newSource.length)
        state.setSource(newSource)
        set({ selectedNodeId: newId })

        console.log('[duplicateNode] Done!')
        return newId
      },

      // Update a node input value
      updateNodeInput: (nodeId, inputKey, newValue) => {
        console.log('[updateNodeInput] nodeId:', nodeId, 'inputKey:', inputKey, 'newValue:', newValue)
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the node's starting line
        let nodeStartLine = -1
        let nodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]
          const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match && match[2] === nodeId) {
            nodeStartLine = i
            nodeIndent = match[1].length
            console.log('[updateNodeInput] Found node at line:', i)
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`[updateNodeInput] Node "${nodeId}" not found in source`)
          return false
        }

        // Find the inputs: section and the specific input
        let inputsLineIndex = -1
        let targetInputLine = -1

        for (let i = nodeStartLine + 1; i < lines.length; i++) {
          const line = lines[i]

          // Check if we've left the node block
          if (line.trim() !== '' && !line.trim().startsWith('#')) {
            const currentIndent = line.search(/\S/)
            if (currentIndent !== -1 && currentIndent <= nodeIndent) {
              break
            }
          }

          // Find inputs:
          if (line.match(/^\s+inputs:\s*$/)) {
            inputsLineIndex = i
            continue
          }

          // Find the specific input key
          if (inputsLineIndex !== -1) {
            const inputMatch = line.match(new RegExp(`^(\\s+)(${inputKey}):\\s*(.*)$`))
            if (inputMatch) {
              targetInputLine = i
              break
            }
          }
        }

        if (targetInputLine === -1) {
          console.warn(`Input "${inputKey}" not found in node "${nodeId}"`)
          return false
        }

        // Parse the new value
        let formattedValue: string
        if (newValue.startsWith('$')) {
          // Variable reference
          formattedValue = `{ variable: "${newValue.slice(1)}" }`
        } else {
          // Try to parse as JSON, fall back to string literal
          try {
            const parsed = JSON.parse(newValue)
            formattedValue = `{ literal: ${JSON.stringify(parsed)} }`
          } catch {
            formattedValue = `{ literal: "${newValue}" }`
          }
        }

        // Replace the input line
        const indent = lines[targetInputLine].match(/^(\s+)/)?.[1] || '          '
        lines[targetInputLine] = `${indent}${inputKey}: ${formattedValue}`

        const newSource = lines.join('\n')
        state.setSource(newSource)

        return true
      },

      // Examples
      examples: [],
      setExamples: (examples) => set({ examples }),

      // Opcodes
      opcodes: [],
      setOpcodes: (opcodes) => set({ opcodes }),

      // Execution
      isExecuting: false,
      executionOutput: '',
      executionResult: null,
      executionError: null,
      setIsExecuting: (isExecuting) => set({ isExecuting }),
      setExecutionOutput: (output) => set({ executionOutput: output }),
      appendExecutionOutput: (chunk) =>
        set((state) => ({ executionOutput: state.executionOutput + chunk })),
      setExecutionResult: (result) => set({ executionResult: result }),
      setExecutionError: (error) => set({ executionError: error }),
      clearExecution: () =>
        set({
          executionOutput: '',
          executionResult: null,
          executionError: null,
        }),

      // Inputs
      workflowInputs: {},
      setWorkflowInput: (key, value) =>
        set((state) => ({
          workflowInputs: { ...state.workflowInputs, [key]: value },
        })),
      clearWorkflowInputs: () => set({ workflowInputs: {} }),
    }),
    {
      name: 'lexflow-workflow',
      // Only persist the source code, not transient state
      partialize: (state) => ({ source: state.source }),
    }
  )
)
