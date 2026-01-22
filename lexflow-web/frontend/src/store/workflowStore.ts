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
  connectNodes: (fromNodeId: string, toNodeId: string) => boolean
  connectBranch: (fromNodeId: string, toNodeId: string, branchLabel: string) => boolean
  disconnectNode: (nodeId: string) => boolean
  disconnectConnection: (fromNodeId: string, toNodeId: string, branchLabel?: string) => boolean
  convertOrphanToReporter: (
    orphanNodeId: string,
    targetNodeId: string,
    inputKey: string,
    isCompatible: boolean | null
  ) => boolean
  updateReporterInput: (
    reporterNodeId: string,
    inputKey: string,
    newValue: string
  ) => boolean
  deleteReporter: (parentNodeId: string, inputPath: string[]) => boolean

  // Variable and interface operations
  updateWorkflowInterface: (workflowName: string, inputs: string[], outputs: string[]) => boolean
  addVariable: (workflowName: string, name: string, defaultValue: unknown) => boolean
  updateVariable: (workflowName: string, oldName: string, newName: string, newValue: unknown) => boolean
  deleteVariable: (workflowName: string, name: string) => boolean

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

      // Connect two nodes (set fromNodeId.next = toNodeId)
      connectNodes: (fromNodeId, toNodeId) => {
        console.log('[connectNodes] Connecting', fromNodeId, '->', toNodeId)
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the fromNode's starting line
        let nodeStartLine = -1
        let nodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]
          const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match && match[2] === fromNodeId) {
            nodeStartLine = i
            nodeIndent = match[1].length
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`[connectNodes] Node "${fromNodeId}" not found in source`)
          return false
        }

        // Find the next: line within this node, or add one if it doesn't exist
        let nextLineIndex = -1
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

          // Check for next: line
          if (line.match(/^\s+next:\s*/)) {
            nextLineIndex = nodeEndLine
          }

          nodeEndLine++
        }

        const inputIndent = ' '.repeat(nodeIndent + 2)

        if (nextLineIndex !== -1) {
          // Replace existing next line
          lines[nextLineIndex] = `${inputIndent}next: ${toNodeId}`
        } else {
          // Insert next line after the node header (before opcode or first property)
          // Find the first property line
          let insertIndex = nodeStartLine + 1
          while (insertIndex < nodeEndLine) {
            const line = lines[insertIndex]
            if (line.trim() !== '' && !line.trim().startsWith('#')) {
              break
            }
            insertIndex++
          }

          lines.splice(insertIndex, 0, `${inputIndent}next: ${toNodeId}`)
        }

        const newSource = lines.join('\n')
        state.setSource(newSource)
        console.log('[connectNodes] Successfully connected nodes')
        return true
      },

      // Connect a branch (set branch: toNodeId in the appropriate branch slot)
      connectBranch: (fromNodeId, toNodeId, branchLabel) => {
        console.log('[connectBranch] Connecting branch', branchLabel, 'from', fromNodeId, 'to', toNodeId)
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the node's starting line
        let nodeStartLine = -1
        let nodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]
          const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match && match[2] === fromNodeId) {
            nodeStartLine = i
            nodeIndent = match[1].length
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`[connectBranch] Node "${fromNodeId}" not found in source`)
          return false
        }

        // Find the inputs: section within this node
        let inputsLine = -1
        let inputsIndent = -1
        let nodeEndLine = nodeStartLine + 1

        while (nodeEndLine < lines.length) {
          const line = lines[nodeEndLine]
          if (line.trim() === '' || line.trim().startsWith('#')) {
            nodeEndLine++
            continue
          }

          const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
          if (lineIndent <= nodeIndent && line.trim()) {
            break // Left node scope
          }

          const inputsMatch = line.match(/^(\s+)inputs:\s*$/)
          if (inputsMatch) {
            inputsLine = nodeEndLine
            inputsIndent = inputsMatch[1].length
            break
          }

          nodeEndLine++
        }

        if (inputsLine === -1) {
          console.warn(`[connectBranch] No inputs: section found for node "${fromNodeId}"`)
          return false
        }

        const isCatchBranch = branchLabel.startsWith('CATCH')
        const branchIndent = ' '.repeat(inputsIndent + 2)
        const branchValueIndent = ' '.repeat(inputsIndent + 4)

        // Find the branch label line within inputs, or find where to insert it
        let branchLabelLine = -1
        let inputsEndLine = inputsLine + 1

        while (inputsEndLine < lines.length) {
          const line = lines[inputsEndLine]
          if (line.trim() === '' || line.trim().startsWith('#')) {
            inputsEndLine++
            continue
          }

          const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
          if (lineIndent <= inputsIndent && line.trim()) {
            break // Left inputs scope
          }

          // Look for the branch label
          const labelMatch = line.match(/^\s+([A-Z]+\d*):\s*$/)
          if (labelMatch && labelMatch[1] === branchLabel) {
            branchLabelLine = inputsEndLine
            break
          }

          inputsEndLine++
        }

        if (branchLabelLine !== -1) {
          // Branch label exists, find and update or insert the branch: line
          const branchLabelIndent = lines[branchLabelLine].match(/^(\s*)/)?.[1].length || 0
          let searchLine = branchLabelLine + 1

          if (isCatchBranch) {
            // For CATCH branches, we need to find or create body: { branch: ... }
            let bodyLine = -1
            while (searchLine < lines.length) {
              const line = lines[searchLine]
              if (line.trim() === '' || line.trim().startsWith('#')) {
                searchLine++
                continue
              }
              const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
              if (lineIndent <= branchLabelIndent && line.trim()) {
                break // Left branch label scope
              }

              if (line.match(/^\s+body:\s*$/)) {
                bodyLine = searchLine
                break
              }
              searchLine++
            }

            if (bodyLine !== -1) {
              // Find branch: inside body and update it
              const bodyIndent = lines[bodyLine].match(/^(\s*)/)?.[1].length || 0
              let bodySearchLine = bodyLine + 1
              while (bodySearchLine < lines.length) {
                const line = lines[bodySearchLine]
                if (line.trim() === '' || line.trim().startsWith('#')) {
                  bodySearchLine++
                  continue
                }
                const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
                if (lineIndent <= bodyIndent && line.trim()) {
                  break
                }
                const branchMatch = line.match(/^(\s+)branch:\s*/)
                if (branchMatch) {
                  lines[bodySearchLine] = `${branchMatch[1]}branch: ${toNodeId}`
                  state.setSource(lines.join('\n'))
                  console.log('[connectBranch] Updated CATCH branch')
                  return true
                }
                bodySearchLine++
              }
              // branch: not found inside body, insert it
              const bodyBranchIndent = ' '.repeat(bodyIndent + 2)
              lines.splice(bodyLine + 1, 0, `${bodyBranchIndent}branch: ${toNodeId}`)
              state.setSource(lines.join('\n'))
              console.log('[connectBranch] Inserted branch inside CATCH body')
              return true
            } else {
              // body: not found, insert body: with branch:
              const catchBodyIndent = ' '.repeat(branchLabelIndent + 2)
              const catchBranchIndent = ' '.repeat(branchLabelIndent + 4)
              // Find end of CATCH section to insert body
              let insertLine = branchLabelLine + 1
              while (insertLine < lines.length) {
                const line = lines[insertLine]
                if (line.trim() === '' || line.trim().startsWith('#')) {
                  insertLine++
                  continue
                }
                const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
                if (lineIndent <= branchLabelIndent && line.trim()) {
                  break
                }
                insertLine++
              }
              lines.splice(insertLine, 0, `${catchBodyIndent}body:`, `${catchBranchIndent}branch: ${toNodeId}`)
              state.setSource(lines.join('\n'))
              console.log('[connectBranch] Inserted body with branch for CATCH')
              return true
            }
          } else {
            // Standard branch: find and update or insert branch: line
            while (searchLine < lines.length) {
              const line = lines[searchLine]
              if (line.trim() === '' || line.trim().startsWith('#')) {
                searchLine++
                continue
              }
              const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
              if (lineIndent <= branchLabelIndent && line.trim()) {
                break // Left branch label scope
              }

              const branchMatch = line.match(/^(\s+)branch:\s*/)
              if (branchMatch) {
                lines[searchLine] = `${branchMatch[1]}branch: ${toNodeId}`
                state.setSource(lines.join('\n'))
                console.log('[connectBranch] Updated branch')
                return true
              }
              searchLine++
            }

            // branch: not found, insert it
            lines.splice(branchLabelLine + 1, 0, `${branchValueIndent}branch: ${toNodeId}`)
            state.setSource(lines.join('\n'))
            console.log('[connectBranch] Inserted branch line')
            return true
          }
        } else {
          // Branch label doesn't exist, create it with branch: value
          // Insert at end of inputs section
          if (isCatchBranch) {
            // For CATCH branches, create full structure with exception_type and body
            const catchBodyIndent = ' '.repeat(inputsIndent + 4)
            const catchBranchIndent = ' '.repeat(inputsIndent + 6)
            lines.splice(inputsEndLine, 0,
              `${branchIndent}${branchLabel}:`,
              `${catchBodyIndent}exception_type: "Exception"`,
              `${catchBodyIndent}body:`,
              `${catchBranchIndent}branch: ${toNodeId}`
            )
          } else {
            // Standard branch
            lines.splice(inputsEndLine, 0,
              `${branchIndent}${branchLabel}:`,
              `${branchValueIndent}branch: ${toNodeId}`
            )
          }
          state.setSource(lines.join('\n'))
          console.log('[connectBranch] Created new branch entry')
          return true
        }
      },

      // Disconnect a node (set its next: to null)
      disconnectNode: (nodeId) => {
        console.log('[disconnectNode] Disconnecting node:', nodeId)
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
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`[disconnectNode] Node "${nodeId}" not found in source`)
          return false
        }

        // Find the next: line within this node
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

          // Check for next: line and set to null
          if (line.match(/^\s+next:\s*/)) {
            const indent = line.match(/^(\s+)next:/)?.[1] || ' '.repeat(nodeIndent + 2)
            lines[nodeEndLine] = `${indent}next: null`

            const newSource = lines.join('\n')
            state.setSource(newSource)
            console.log('[disconnectNode] Successfully disconnected node')
            return true
          }

          nodeEndLine++
        }

        // No next: line found, nothing to do
        console.log('[disconnectNode] No next: line found, node already disconnected')
        return true
      },

      // Convert an orphan node to a reporter by linking it to a target node's input
      convertOrphanToReporter: (orphanNodeId, targetNodeId, inputKey, isCompatible) => {
        console.log(
          '[convertOrphanToReporter] Converting orphan:',
          orphanNodeId,
          'to reporter for:',
          targetNodeId,
          'input:',
          inputKey
        )

        // Show confirmation if types are incompatible
        if (isCompatible === false) {
          if (
            !confirm(
              `Type mismatch detected. The orphan node's return type may not be compatible with the input "${inputKey}". Continue anyway?`
            )
          ) {
            return false
          }
        }

        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the target node's starting line
        let nodeStartLine = -1
        let nodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]
          const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match && match[2] === targetNodeId) {
            nodeStartLine = i
            nodeIndent = match[1].length
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`[convertOrphanToReporter] Target node "${targetNodeId}" not found in source`)
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
          console.warn(
            `[convertOrphanToReporter] Input "${inputKey}" not found in node "${targetNodeId}"`
          )
          return false
        }

        // Replace the input line with a node reference
        const indent = lines[targetInputLine].match(/^(\s+)/)?.[1] || '          '
        lines[targetInputLine] = `${indent}${inputKey}: { node: "${orphanNodeId}" }`

        const newSource = lines.join('\n')
        state.setSource(newSource)

        console.log('[convertOrphanToReporter] Successfully converted orphan to reporter')
        return true
      },

      // Update a reporter's input value (reporters are nodes, so we just use updateNodeInput logic)
      updateReporterInput: (reporterNodeId, inputKey, newValue) => {
        console.log('[updateReporterInput] reporterNodeId:', reporterNodeId, 'key:', inputKey, 'value:', newValue)

        if (!reporterNodeId) {
          console.warn('[updateReporterInput] No reporter node ID provided')
          return false
        }

        // Reporter nodes are just nodes, so use the same logic as updateNodeInput
        return get().updateNodeInput(reporterNodeId, inputKey, newValue)
      },

      // Delete a reporter (replace with a literal placeholder)
      deleteReporter: (parentNodeId, inputPath) => {
        console.log('[deleteReporter] parentNodeId:', parentNodeId, 'path:', inputPath)

        if (inputPath.length === 0) {
          console.warn('[deleteReporter] Empty input path')
          return false
        }

        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the parent node's starting line
        let nodeStartLine = -1
        let nodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]
          const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match && match[2] === parentNodeId) {
            nodeStartLine = i
            nodeIndent = match[1].length
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`[deleteReporter] Parent node "${parentNodeId}" not found`)
          return false
        }

        // Navigate to find the reporter's parent input and the reporter block
        let currentLine = nodeStartLine
        let currentIndent = nodeIndent
        let inputsSectionFound = false

        // Find inputs: section
        for (let i = nodeStartLine + 1; i < lines.length; i++) {
          const line = lines[i]
          if (line.trim() === '' || line.trim().startsWith('#')) continue
          const lineIndent = line.search(/\S/)
          if (lineIndent !== -1 && lineIndent <= nodeIndent) break
          if (line.match(/^\s+inputs:\s*$/)) {
            inputsSectionFound = true
            currentLine = i
            currentIndent = lineIndent
            break
          }
        }

        if (!inputsSectionFound) {
          console.warn('[deleteReporter] inputs: section not found')
          return false
        }

        // Navigate through path (except last element which is the reporter input key)
        for (let pathIdx = 0; pathIdx < inputPath.length - 1; pathIdx++) {
          const pathKey = inputPath[pathIdx]
          let found = false

          for (let i = currentLine + 1; i < lines.length; i++) {
            const line = lines[i]
            if (line.trim() === '' || line.trim().startsWith('#')) continue
            const lineIndent = line.search(/\S/)
            if (lineIndent !== -1 && lineIndent <= currentIndent) break

            const keyMatch = line.match(new RegExp(`^(\\s+)(${pathKey}):\\s*`))
            if (keyMatch) {
              currentLine = i
              currentIndent = keyMatch[1].length
              found = true

              // Find nested inputs section
              for (let j = i + 1; j < lines.length; j++) {
                const nestedLine = lines[j]
                if (nestedLine.trim() === '' || nestedLine.trim().startsWith('#')) continue
                const nestedIndent = nestedLine.search(/\S/)
                if (nestedIndent !== -1 && nestedIndent <= currentIndent) break
                if (nestedLine.match(/^\s+inputs:\s*$/)) {
                  currentLine = j
                  currentIndent = nestedIndent
                  break
                }
              }
              break
            }
          }

          if (!found) {
            console.warn(`[deleteReporter] Path key "${pathKey}" not found`)
            return false
          }
        }

        // Find the target input key (last element in path)
        const targetKey = inputPath[inputPath.length - 1]
        let targetLine = -1
        let targetIndent = -1

        for (let i = currentLine + 1; i < lines.length; i++) {
          const line = lines[i]
          if (line.trim() === '' || line.trim().startsWith('#')) continue
          const lineIndent = line.search(/\S/)
          if (lineIndent !== -1 && lineIndent <= currentIndent) break

          const keyMatch = line.match(new RegExp(`^(\\s+)(${targetKey}):\\s*`))
          if (keyMatch) {
            targetLine = i
            targetIndent = keyMatch[1].length
            break
          }
        }

        if (targetLine === -1) {
          console.warn(`[deleteReporter] Target key "${targetKey}" not found`)
          return false
        }

        // Find where the reporter block ends
        let blockEndLine = targetLine + 1
        while (blockEndLine < lines.length) {
          const line = lines[blockEndLine]
          if (line.trim() === '' || line.trim().startsWith('#')) {
            blockEndLine++
            continue
          }
          const lineIndent = line.search(/\S/)
          if (lineIndent !== -1 && lineIndent <= targetIndent) break
          blockEndLine++
        }

        // Replace the reporter block with a simple literal
        const indent = ' '.repeat(targetIndent)
        const newLines = [
          ...lines.slice(0, targetLine),
          `${indent}${targetKey}: { literal: null }`,
          ...lines.slice(blockEndLine),
        ]

        const newSource = newLines.join('\n')
        state.setSource(newSource)

        console.log('[deleteReporter] Successfully deleted reporter')
        return true
      },

      // Update workflow interface (inputs/outputs)
      updateWorkflowInterface: (workflowName, inputs, outputs) => {
        console.log('[updateWorkflowInterface] workflowName:', workflowName, 'inputs:', inputs, 'outputs:', outputs)
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the workflow and its interface section
        let inTargetWorkflow = false
        let interfaceStartLine = -1
        let interfaceEndLine = -1
        let interfaceIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]

          // Detect workflow name
          const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/)
          if (nameMatch) {
            inTargetWorkflow = nameMatch[1] === workflowName
          }

          // Find interface: in target workflow
          if (inTargetWorkflow) {
            const interfaceMatch = line.match(/^(\s*)interface:\s*$/)
            if (interfaceMatch) {
              interfaceStartLine = i
              interfaceIndent = interfaceMatch[1].length
              // Find where interface section ends
              let j = i + 1
              while (j < lines.length) {
                const nextLine = lines[j]
                if (nextLine.trim() === '' || nextLine.trim().startsWith('#')) {
                  j++
                  continue
                }
                const nextIndent = nextLine.search(/\S/)
                if (nextIndent !== -1 && nextIndent <= interfaceIndent) {
                  break
                }
                j++
              }
              interfaceEndLine = j
              break
            }
          }
        }

        if (interfaceStartLine === -1) {
          console.warn(`[updateWorkflowInterface] Interface section not found for workflow "${workflowName}"`)
          return false
        }

        // Build new interface YAML
        const indent = ' '.repeat(interfaceIndent)
        const propIndent = ' '.repeat(interfaceIndent + 2)
        const inputsStr = inputs.length > 0 ? `[${inputs.map(i => `"${i}"`).join(', ')}]` : '[]'
        const outputsStr = outputs.length > 0 ? `[${outputs.map(o => `"${o}"`).join(', ')}]` : '[]'
        const newInterfaceYaml = [
          `${indent}interface:`,
          `${propIndent}inputs: ${inputsStr}`,
          `${propIndent}outputs: ${outputsStr}`,
        ]

        // Replace interface section
        const newLines = [
          ...lines.slice(0, interfaceStartLine),
          ...newInterfaceYaml,
          ...lines.slice(interfaceEndLine),
        ]
        const newSource = newLines.join('\n')
        state.setSource(newSource)

        console.log('[updateWorkflowInterface] Successfully updated interface')
        return true
      },

      // Add a new variable to a workflow
      addVariable: (workflowName, name, defaultValue) => {
        console.log('[addVariable] workflowName:', workflowName, 'name:', name, 'value:', defaultValue)
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the workflow and its variables section
        let inTargetWorkflow = false
        let variablesLine = -1
        let variablesIndent = -1
        let variablesEndLine = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]

          // Detect workflow name
          const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/)
          if (nameMatch) {
            inTargetWorkflow = nameMatch[1] === workflowName
          }

          // Find variables: in target workflow
          if (inTargetWorkflow) {
            const varsMatch = line.match(/^(\s*)variables:\s*(.*)$/)
            if (varsMatch) {
              variablesLine = i
              variablesIndent = varsMatch[1].length
              const restOfLine = varsMatch[2].trim()

              // Check if it's inline empty {} or has content
              if (restOfLine === '{}' || restOfLine === '') {
                // Empty variables, need to expand it
                variablesEndLine = i + 1
              } else {
                // Find where variables section ends
                let j = i + 1
                while (j < lines.length) {
                  const nextLine = lines[j]
                  if (nextLine.trim() === '' || nextLine.trim().startsWith('#')) {
                    j++
                    continue
                  }
                  const nextIndent = nextLine.search(/\S/)
                  if (nextIndent !== -1 && nextIndent <= variablesIndent) {
                    break
                  }
                  j++
                }
                variablesEndLine = j
              }
              break
            }
          }
        }

        if (variablesLine === -1) {
          console.warn(`[addVariable] Variables section not found for workflow "${workflowName}"`)
          return false
        }

        const varIndent = ' '.repeat(variablesIndent + 2)
        const valueStr = formatYamlValue(defaultValue)

        // Check if variables: {} is on single line
        if (lines[variablesLine].includes('{}')) {
          // Replace inline {} with block format
          const indent = ' '.repeat(variablesIndent)
          const newLines = [
            ...lines.slice(0, variablesLine),
            `${indent}variables:`,
            `${varIndent}${name}: ${valueStr}`,
            ...lines.slice(variablesLine + 1),
          ]
          state.setSource(newLines.join('\n'))
        } else {
          // Add new variable at end of variables section
          const newLines = [
            ...lines.slice(0, variablesEndLine),
            `${varIndent}${name}: ${valueStr}`,
            ...lines.slice(variablesEndLine),
          ]
          state.setSource(newLines.join('\n'))
        }

        console.log('[addVariable] Successfully added variable')
        return true
      },

      // Update an existing variable
      updateVariable: (workflowName, oldName, newName, newValue) => {
        console.log('[updateVariable] workflowName:', workflowName, 'oldName:', oldName, 'newName:', newName, 'value:', newValue)
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the workflow and the specific variable
        let inTargetWorkflow = false
        let inVariables = false
        let variablesIndent = -1
        let varLine = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]

          // Detect workflow name
          const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/)
          if (nameMatch) {
            inTargetWorkflow = nameMatch[1] === workflowName
            inVariables = false
          }

          // Find variables: in target workflow
          if (inTargetWorkflow) {
            const varsMatch = line.match(/^(\s*)variables:\s*/)
            if (varsMatch) {
              inVariables = true
              variablesIndent = varsMatch[1].length
              continue
            }

            // Check if we've left the variables section
            if (inVariables) {
              const lineIndent = line.search(/\S/)
              if (line.trim() !== '' && !line.trim().startsWith('#') && lineIndent !== -1 && lineIndent <= variablesIndent) {
                inVariables = false
                continue
              }

              // Find the variable
              const varMatch = line.match(new RegExp(`^(\\s+)${oldName}:\\s*(.*)$`))
              if (varMatch) {
                varLine = i
                break
              }
            }
          }
        }

        if (varLine === -1) {
          console.warn(`[updateVariable] Variable "${oldName}" not found in workflow "${workflowName}"`)
          return false
        }

        const varIndent = lines[varLine].match(/^(\s+)/)?.[1] || '    '
        const valueStr = formatYamlValue(newValue)
        lines[varLine] = `${varIndent}${newName}: ${valueStr}`

        state.setSource(lines.join('\n'))
        console.log('[updateVariable] Successfully updated variable')
        return true
      },

      // Disconnect a specific connection between two nodes
      disconnectConnection: (fromNodeId, toNodeId, branchLabel) => {
        console.log('[disconnectConnection] Disconnecting', fromNodeId, '->', toNodeId, 'branch:', branchLabel)

        // If no branch label, disconnect via next: null
        if (!branchLabel) {
          return get().disconnectNode(fromNodeId)
        }

        // Branch-specific disconnection for control flow nodes
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the node's starting line
        let nodeStartLine = -1
        let nodeIndent = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]
          const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/)
          if (match && match[2] === fromNodeId) {
            nodeStartLine = i
            nodeIndent = match[1].length
            break
          }
        }

        if (nodeStartLine === -1) {
          console.warn(`[disconnectConnection] Node "${fromNodeId}" not found in source`)
          return false
        }

        // Find the inputs: section within this node
        let inputsLine = -1
        let inputsIndent = -1
        let nodeEndLine = nodeStartLine + 1

        while (nodeEndLine < lines.length) {
          const line = lines[nodeEndLine]
          if (line.trim() === '' || line.trim().startsWith('#')) {
            nodeEndLine++
            continue
          }

          const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
          if (lineIndent <= nodeIndent && line.trim()) {
            break // Left node scope
          }

          const inputsMatch = line.match(/^(\s+)inputs:\s*$/)
          if (inputsMatch) {
            inputsLine = nodeEndLine
            inputsIndent = inputsMatch[1].length
            break
          }

          nodeEndLine++
        }

        if (inputsLine === -1) {
          console.warn(`[disconnectConnection] No inputs: section found for node "${fromNodeId}"`)
          return false
        }

        // Find the branch label within inputs
        // Handle CATCH branches which have nested body: { branch: ... } structure
        const isCatchBranch = branchLabel.startsWith('CATCH')
        let branchLabelLine = -1
        let searchLine = inputsLine + 1

        while (searchLine < lines.length) {
          const line = lines[searchLine]
          if (line.trim() === '' || line.trim().startsWith('#')) {
            searchLine++
            continue
          }

          const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
          if (lineIndent <= inputsIndent && line.trim()) {
            break // Left inputs scope
          }

          // Look for the branch label (e.g., "THEN:", "ELSE:", "BODY:", "TRY:", "CATCH1:", "FINALLY:")
          const labelMatch = line.match(/^\s+([A-Z]+\d*):\s*$/)
          if (labelMatch && labelMatch[1] === branchLabel) {
            branchLabelLine = searchLine
            break
          }

          searchLine++
        }

        if (branchLabelLine === -1) {
          console.warn(`[disconnectConnection] Branch label "${branchLabel}" not found in inputs`)
          return false
        }

        // Find the branch: line within this branch section
        const branchLabelIndent = lines[branchLabelLine].match(/^(\s*)/)?.[1].length || 0
        let branchLineIndex = branchLabelLine + 1

        while (branchLineIndex < lines.length) {
          const line = lines[branchLineIndex]
          if (line.trim() === '' || line.trim().startsWith('#')) {
            branchLineIndex++
            continue
          }

          const lineIndent = line.match(/^(\s*)/)?.[1].length || 0
          if (lineIndent <= branchLabelIndent && line.trim()) {
            break // Left branch label scope
          }

          // For CATCH branches, we need to find body: then branch: inside body
          if (isCatchBranch) {
            const bodyMatch = line.match(/^(\s+)body:\s*$/)
            if (bodyMatch) {
              // Now find branch: inside body
              const bodyIndent = bodyMatch[1].length
              let bodyLine = branchLineIndex + 1
              while (bodyLine < lines.length) {
                const innerLine = lines[bodyLine]
                if (innerLine.trim() === '' || innerLine.trim().startsWith('#')) {
                  bodyLine++
                  continue
                }
                const innerIndent = innerLine.match(/^(\s*)/)?.[1].length || 0
                if (innerIndent <= bodyIndent && innerLine.trim()) {
                  break
                }
                const branchMatch = innerLine.match(/^(\s+)branch:\s*(\S+)/)
                if (branchMatch && branchMatch[2] === toNodeId) {
                  const indent = branchMatch[1]
                  lines[bodyLine] = `${indent}branch: null`
                  state.setSource(lines.join('\n'))
                  console.log('[disconnectConnection] Disconnected CATCH branch')
                  return true
                }
                bodyLine++
              }
            }
          } else {
            // Standard branch: for THEN, ELSE, BODY, TRY, FINALLY
            const branchMatch = line.match(/^(\s+)branch:\s*(\S+)/)
            if (branchMatch && branchMatch[2] === toNodeId) {
              const indent = branchMatch[1]
              lines[branchLineIndex] = `${indent}branch: null`
              state.setSource(lines.join('\n'))
              console.log('[disconnectConnection] Disconnected branch')
              return true
            }
          }

          branchLineIndex++
        }

        console.warn(`[disconnectConnection] Could not find branch reference to "${toNodeId}"`)
        return false
      },

      // Delete a variable from a workflow
      deleteVariable: (workflowName, name) => {
        console.log('[deleteVariable] workflowName:', workflowName, 'name:', name)
        const state = get()
        const { source } = state
        const lines = source.split('\n')

        // Find the workflow and the specific variable
        let inTargetWorkflow = false
        let inVariables = false
        let variablesIndent = -1
        let varLine = -1

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i]

          // Detect workflow name
          const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/)
          if (nameMatch) {
            inTargetWorkflow = nameMatch[1] === workflowName
            inVariables = false
          }

          // Find variables: in target workflow
          if (inTargetWorkflow) {
            const varsMatch = line.match(/^(\s*)variables:\s*/)
            if (varsMatch) {
              inVariables = true
              variablesIndent = varsMatch[1].length
              continue
            }

            // Check if we've left the variables section
            if (inVariables) {
              const lineIndent = line.search(/\S/)
              if (line.trim() !== '' && !line.trim().startsWith('#') && lineIndent !== -1 && lineIndent <= variablesIndent) {
                inVariables = false
                continue
              }

              // Find the variable
              const varMatch = line.match(new RegExp(`^(\\s+)${name}:\\s*(.*)$`))
              if (varMatch) {
                varLine = i
                break
              }
            }
          }
        }

        if (varLine === -1) {
          console.warn(`[deleteVariable] Variable "${name}" not found in workflow "${workflowName}"`)
          return false
        }

        // Remove the variable line
        const newLines = [...lines.slice(0, varLine), ...lines.slice(varLine + 1)]
        state.setSource(newLines.join('\n'))

        console.log('[deleteVariable] Successfully deleted variable')
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

// Helper function to format a value for YAML
function formatYamlValue(value: unknown): string {
  if (value === null) return 'null'
  if (value === undefined) return 'null'
  if (typeof value === 'string') {
    // Check if string needs quoting
    if (value === '' || value.includes(':') || value.includes('#') || value.includes('\n') ||
        value.startsWith(' ') || value.endsWith(' ') || /^[\[\]{}>|*&!%@`]/.test(value)) {
      return JSON.stringify(value)
    }
    // Check if it looks like a number, boolean, or null
    if (/^-?\d+(\.\d+)?$/.test(value) || value === 'true' || value === 'false' || value === 'null') {
      return JSON.stringify(value)
    }
    return value
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }
  // For arrays and objects, use JSON format
  return JSON.stringify(value)
}
