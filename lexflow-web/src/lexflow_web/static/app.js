// LexFlow Web Frontend Application - Interactive Visualization

// State
const state = {
    treeData: null,
    rawWorkflow: null,  // Original parsed workflow data
    interface: null,
    ws: null,
    isExecuting: false,
    zoom: 1.0,
    collapsedBranches: new Set(),
    editingNode: null
};

// DOM Elements
const elements = {
    editor: document.getElementById('editor'),
    parseStatus: document.getElementById('parse-status'),
    visualization: document.getElementById('visualization'),
    treeCanvas: document.getElementById('tree-canvas'),
    inputsContainer: document.getElementById('inputs-container'),
    output: document.getElementById('output'),
    resultContainer: document.getElementById('result-container'),
    result: document.getElementById('result'),
    examplesSelect: document.getElementById('examples-select'),
    executeBtn: document.getElementById('execute-btn'),
    clearOutputBtn: document.getElementById('clear-output-btn'),
    editorPanel: document.getElementById('editor-panel'),
    toggleEditorBtn: document.getElementById('toggle-editor-btn'),
    zoomInBtn: document.getElementById('zoom-in-btn'),
    zoomOutBtn: document.getElementById('zoom-out-btn'),
    zoomResetBtn: document.getElementById('zoom-reset-btn'),
    zoomLevel: document.getElementById('zoom-level'),
    modal: document.getElementById('node-editor-modal'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    modalCloseBtn: document.getElementById('modal-close-btn'),
    modalCancelBtn: document.getElementById('modal-cancel-btn'),
    modalSaveBtn: document.getElementById('modal-save-btn')
};

// Debounce utility
function debounce(fn, delay) {
    let timer = null;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Initialize application
async function init() {
    await loadExamples();

    // Editor events
    elements.editor.addEventListener('input', debounce(parseWorkflow, 500));
    elements.examplesSelect.addEventListener('change', loadSelectedExample);
    elements.executeBtn.addEventListener('click', executeWorkflow);
    elements.clearOutputBtn.addEventListener('click', clearOutput);

    // Editor toggle
    elements.toggleEditorBtn.addEventListener('click', toggleEditor);

    // Zoom controls
    elements.zoomInBtn.addEventListener('click', () => setZoom(state.zoom + 0.25));
    elements.zoomOutBtn.addEventListener('click', () => setZoom(state.zoom - 0.25));
    elements.zoomResetBtn.addEventListener('click', () => setZoom(1.0));

    // Mouse wheel zoom
    elements.visualization.addEventListener('wheel', (e) => {
        if (e.ctrlKey) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            setZoom(state.zoom + delta);
        }
    });

    // Modal events
    elements.modalCloseBtn.addEventListener('click', closeModal);
    elements.modalCancelBtn.addEventListener('click', closeModal);
    elements.modalSaveBtn.addEventListener('click', saveNodeChanges);
    elements.modal.querySelector('.modal-backdrop').addEventListener('click', closeModal);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !elements.modal.classList.contains('hidden')) {
            closeModal();
        }
    });

    // Parse initial content
    if (elements.editor.value.trim()) {
        parseWorkflow();
    }
}

// Toggle editor panel
function toggleEditor() {
    elements.editorPanel.classList.toggle('collapsed');
    elements.toggleEditorBtn.textContent = elements.editorPanel.classList.contains('collapsed') ? '>' : '<';
}

// Zoom controls
function setZoom(level) {
    state.zoom = Math.max(0.25, Math.min(2.0, level));
    document.documentElement.style.setProperty('--zoom', state.zoom);
    elements.zoomLevel.textContent = Math.round(state.zoom * 100) + '%';
}

// Load examples list
async function loadExamples() {
    try {
        const response = await fetch('/api/examples');
        const examples = await response.json();

        const categories = {};
        examples.forEach(ex => {
            if (!categories[ex.category]) {
                categories[ex.category] = [];
            }
            categories[ex.category].push(ex);
        });

        Object.keys(categories).sort().forEach(category => {
            const group = document.createElement('optgroup');
            group.label = category.replace(/_/g, ' ');

            categories[category].forEach(ex => {
                const option = document.createElement('option');
                option.value = ex.path;
                option.textContent = ex.name;
                group.appendChild(option);
            });

            elements.examplesSelect.appendChild(group);
        });
    } catch (error) {
        console.error('Failed to load examples:', error);
    }
}

// Load selected example
async function loadSelectedExample() {
    const path = elements.examplesSelect.value;
    if (!path) return;

    try {
        const response = await fetch(`/api/examples/${path}`);
        const data = await response.json();
        elements.editor.value = data.content;
        parseWorkflow();
    } catch (error) {
        console.error('Failed to load example:', error);
    }
}

// Parse workflow and update visualization
async function parseWorkflow() {
    const content = elements.editor.value.trim();
    if (!content) {
        elements.parseStatus.textContent = '';
        elements.parseStatus.className = 'status';
        elements.treeCanvas.innerHTML = '<div class="placeholder">Enter a workflow to see visualization</div>';
        elements.inputsContainer.innerHTML = '<div class="placeholder">No inputs defined</div>';
        state.treeData = null;
        state.rawWorkflow = null;
        state.interface = null;
        return;
    }

    elements.parseStatus.textContent = 'Parsing...';
    elements.parseStatus.className = 'status parsing';

    try {
        const response = await fetch('/api/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ workflow: content })
        });

        const data = await response.json();

        if (data.success) {
            elements.parseStatus.textContent = 'Valid';
            elements.parseStatus.className = 'status valid';
            state.treeData = data.tree;
            state.interface = data.interface;
            // Parse the raw workflow for editing
            try {
                state.rawWorkflow = content.trim().startsWith('{')
                    ? JSON.parse(content)
                    : jsyaml ? jsyaml.load(content) : null;
            } catch {
                state.rawWorkflow = null;
            }
            renderVisualization();
            renderInputs();
        } else {
            elements.parseStatus.textContent = 'Invalid';
            elements.parseStatus.className = 'status invalid';
            elements.treeCanvas.innerHTML = `<div class="placeholder" style="color: var(--color-red)">${escapeHtml(data.error)}</div>`;
        }
    } catch (error) {
        elements.parseStatus.textContent = 'Error';
        elements.parseStatus.className = 'status invalid';
        console.error('Parse error:', error);
    }
}

// Render tree visualization
function renderVisualization() {
    if (!state.treeData) {
        elements.treeCanvas.innerHTML = '<div class="placeholder">No data to visualize</div>';
        return;
    }

    elements.treeCanvas.innerHTML = renderWorkflowTree(state.treeData);

    // Add click handlers to nodes
    document.querySelectorAll('.node-panel').forEach(panel => {
        panel.addEventListener('click', (e) => {
            // Don't open editor if clicking fold toggle
            if (e.target.classList.contains('fold-toggle')) return;
            const nodeId = panel.closest('.tree-node')?.dataset.id;
            if (nodeId) openNodeEditor(nodeId);
        });
    });

    // Add click handlers to nested reporters
    document.querySelectorAll('.nested-reporter').forEach(reporter => {
        reporter.addEventListener('click', (e) => {
            e.stopPropagation();
            const nodeId = reporter.dataset.id;
            if (nodeId) openNodeEditor(nodeId);
        });
    });

    // Add fold toggle handlers
    document.querySelectorAll('.fold-toggle').forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            const nodeId = toggle.dataset.nodeId;
            if (nodeId) toggleBranch(nodeId);
        });
    });
}

// Toggle branch collapse
function toggleBranch(nodeId) {
    if (state.collapsedBranches.has(nodeId)) {
        state.collapsedBranches.delete(nodeId);
    } else {
        state.collapsedBranches.add(nodeId);
    }
    renderVisualization();
}

// Render workflow tree
function renderWorkflowTree(tree) {
    const variables = tree.variables || {};
    const varStr = Object.entries(variables)
        .map(([k, v]) => `${k}=${formatValueShort(v)}`)
        .join(', ');

    const interfaceStr = [];
    if (tree.interface?.inputs?.length > 0) {
        interfaceStr.push(`inputs: [${tree.interface.inputs.join(', ')}]`);
    }
    if (tree.interface?.outputs?.length > 0) {
        interfaceStr.push(`outputs: [${tree.interface.outputs.join(', ')}]`);
    }

    let meta = '';
    if (interfaceStr.length > 0) {
        meta += `<div class="workflow-meta">Interface: ${escapeHtml(interfaceStr.join(' | '))}</div>`;
    }
    if (varStr) {
        meta += `<div class="workflow-meta">Variables: ${escapeHtml(varStr)}</div>`;
    }

    const childrenHtml = tree.children?.length > 0
        ? `<div class="tree-children">${tree.children.map(renderNode).join('')}</div>`
        : '';

    return `
        <div class="tree-workflow">
            <div class="tree-header">
                <span class="workflow-name">WORKFLOW: ${escapeHtml(tree.name)}</span>
                ${meta}
            </div>
            ${childrenHtml}
        </div>
    `;
}

// Render a tree node
function renderNode(node) {
    if (node.type === 'branch') {
        return renderBranch(node);
    }

    const isControlFlow = node.type === 'control_flow';
    const isCollapsed = state.collapsedBranches.has(node.id);
    const panelClass = isControlFlow ? 'node-panel control-flow' : 'node-panel';

    // Fold toggle for control flow
    const foldToggle = isControlFlow && node.children?.length > 0
        ? `<span class="fold-toggle" data-node-id="${escapeHtml(node.id)}">${isCollapsed ? '▶' : '▼'}</span>`
        : '';

    let inputsHtml = '';
    const inputs = node.inputs || {};
    if (Object.keys(inputs).length > 0) {
        inputsHtml = `
            <div class="node-inputs">
                ${Object.entries(inputs).map(([key, value]) =>
                    `<div class="node-input">
                        <span class="input-key">${escapeHtml(key)}:</span>
                        ${renderInputValue(value)}
                    </div>`
                ).join('')}
            </div>
        `;
    }

    // Loop config for control flow
    let configHtml = '';
    if (node.config) {
        configHtml = `
            <div class="loop-config">
                ${Object.entries(node.config).map(([key, value]) =>
                    `<div class="config-item">
                        <span class="config-key">${escapeHtml(key)}:</span>
                        ${renderInputValue(value)}
                    </div>`
                ).join('')}
            </div>
        `;
    }

    let childrenHtml = '';
    if (node.children?.length > 0 && !isCollapsed) {
        childrenHtml = `<div class="tree-children">${node.children.map(renderNode).join('')}</div>`;
    } else if (node.children?.length > 0 && isCollapsed) {
        childrenHtml = `<div class="collapsed-indicator">${node.children.length} branch(es) collapsed</div>`;
    }

    return `
        <div class="tree-node" data-id="${escapeHtml(node.id)}">
            <div class="${panelClass}">
                <div class="node-header">
                    <span class="node-opcode">${escapeHtml(node.opcode)}</span>
                    <span class="node-id">(${escapeHtml(node.id)})</span>
                    ${foldToggle}
                </div>
                ${inputsHtml}
                ${configHtml}
            </div>
            ${childrenHtml}
        </div>
    `;
}

// Render a branch
function renderBranch(branch) {
    let labelClass = 'branch-label';
    let labelText = branch.name;

    if (branch.name === 'CATCH') {
        labelClass += ' catch';
        const exType = branch.exception_type || 'Exception';
        const varName = branch.var_name ? ` as ${branch.var_name}` : '';
        labelText = `CATCH <span class="exception-type">${escapeHtml(exType)}</span>${escapeHtml(varName)}:`;
    } else {
        labelText = `${branch.name}:`;
    }

    const childrenHtml = branch.children?.length > 0
        ? branch.children.map(renderNode).join('')
        : '';

    const loopBack = branch.name === 'BODY' ? '<div class="loop-back">↑ loops back</div>' : '';

    return `
        <div class="tree-branch">
            <div class="branch-header">
                <span class="${labelClass}">${labelText}</span>
            </div>
            <div class="tree-children">
                ${childrenHtml}
                ${loopBack}
            </div>
        </div>
    `;
}

// Render input value - with nested reporter support
function renderInputValue(value) {
    if (!value) return '<span class="input-value">null</span>';

    switch (value.type) {
        case 'literal':
            return `<span class="input-value literal">${escapeHtml(formatValueShort(value.value))}</span>`;

        case 'variable':
            return `<span class="input-value variable">Variable(${escapeHtml(value.name)})</span>`;

        case 'reporter':
            // Render as a mini clickable node
            const reporterInputs = Object.entries(value.inputs || {})
                .map(([k, v]) => `<div class="reporter-input"><span class="input-key">${escapeHtml(k)}:</span> ${renderInputValue(v)}</div>`)
                .join('');

            return `
                <div class="nested-reporter" data-id="${escapeHtml(value.id)}">
                    <div class="reporter-header">
                        <span class="reporter-opcode">${escapeHtml(value.opcode)}</span>
                        <span class="reporter-id">(${escapeHtml(value.id)})</span>
                    </div>
                    ${reporterInputs ? `<div class="reporter-inputs">${reporterInputs}</div>` : ''}
                </div>
            `;

        case 'branch':
            return `<span class="input-value branch">→branch(${escapeHtml(value.target)})</span>`;

        case 'workflow_call':
            return `<span class="input-value branch">→workflow(${escapeHtml(value.name)})</span>`;

        case 'dict':
            return `<span class="input-value">${escapeHtml(formatValueShort(value.value))}</span>`;

        default:
            return `<span class="input-value">${escapeHtml(JSON.stringify(value))}</span>`;
    }
}

// Format value for short display
function formatValueShort(value) {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'string') {
        if (value.length > 40) {
            return `'${value.substring(0, 37)}...'`;
        }
        return `'${value}'`;
    }
    if (typeof value === 'number' || typeof value === 'boolean') {
        return String(value);
    }
    if (Array.isArray(value)) {
        if (value.length > 3) {
            return `[${value.slice(0, 3).map(formatValueShort).join(', ')}, ...]`;
        }
        return `[${value.map(formatValueShort).join(', ')}]`;
    }
    if (typeof value === 'object') {
        const keys = Object.keys(value);
        if (keys.length > 2) {
            return `{...}`;
        }
        return JSON.stringify(value);
    }
    return String(value);
}

// Find node in tree by ID
function findNodeInTree(tree, nodeId, path = []) {
    if (!tree) return null;

    // Check if this node matches
    if (tree.id === nodeId) {
        return { node: tree, path };
    }

    // Search children
    if (tree.children) {
        for (let i = 0; i < tree.children.length; i++) {
            const result = findNodeInTree(tree.children[i], nodeId, [...path, 'children', i]);
            if (result) return result;
        }
    }

    // Search inputs for reporter nodes
    if (tree.inputs) {
        for (const [key, value] of Object.entries(tree.inputs)) {
            if (value && value.type === 'reporter' && value.id === nodeId) {
                return { node: value, path: [...path, 'inputs', key], isReporter: true };
            }
            // Recursively check nested reporters
            if (value && value.inputs) {
                const result = findReporterInInputs(value, nodeId, [...path, 'inputs', key]);
                if (result) return result;
            }
        }
    }

    // Search config for reporters
    if (tree.config) {
        for (const [key, value] of Object.entries(tree.config)) {
            if (value && value.type === 'reporter' && value.id === nodeId) {
                return { node: value, path: [...path, 'config', key], isReporter: true };
            }
        }
    }

    return null;
}

function findReporterInInputs(obj, nodeId, path) {
    if (obj.id === nodeId) {
        return { node: obj, path, isReporter: true };
    }
    if (obj.inputs) {
        for (const [key, value] of Object.entries(obj.inputs)) {
            if (value && value.type === 'reporter') {
                const result = findReporterInInputs(value, nodeId, [...path, 'inputs', key]);
                if (result) return result;
            }
        }
    }
    return null;
}

// Open node editor modal
function openNodeEditor(nodeId) {
    const result = findNodeInTree(state.treeData, nodeId);
    if (!result) {
        console.error('Node not found:', nodeId);
        return;
    }

    state.editingNode = { ...result, nodeId };
    const node = result.node;
    const isReporter = result.isReporter;

    elements.modalTitle.textContent = `Edit ${isReporter ? 'Reporter' : 'Node'}: ${nodeId}`;

    // Build form fields
    let formHtml = `
        <div class="modal-field">
            <label>Node ID</label>
            <input type="text" id="edit-node-id" value="${escapeHtml(nodeId)}" />
            <div class="help-text">Unique identifier for this node</div>
        </div>
        <div class="modal-field">
            <label>Opcode</label>
            <input type="text" id="edit-opcode" value="${escapeHtml(node.opcode || '')}" />
            <div class="help-text">The operation this node performs</div>
        </div>
    `;

    // Add input fields
    const inputs = node.inputs || {};
    for (const [key, value] of Object.entries(inputs)) {
        const displayValue = getEditableValue(value);
        formHtml += `
            <div class="modal-field">
                <label>Input: ${escapeHtml(key)}</label>
                <textarea id="edit-input-${escapeHtml(key)}" data-input-key="${escapeHtml(key)}">${escapeHtml(displayValue)}</textarea>
                <div class="help-text">Type: ${value?.type || 'unknown'}</div>
            </div>
        `;
    }

    // Add config fields for control flow
    if (node.config) {
        for (const [key, value] of Object.entries(node.config)) {
            const displayValue = getEditableValue(value);
            formHtml += `
                <div class="modal-field">
                    <label>Config: ${escapeHtml(key)}</label>
                    <input type="text" id="edit-config-${escapeHtml(key)}" data-config-key="${escapeHtml(key)}" value="${escapeHtml(displayValue)}" />
                </div>
            `;
        }
    }

    elements.modalBody.innerHTML = formHtml;
    elements.modal.classList.remove('hidden');
}

// Get editable value from input
function getEditableValue(value) {
    if (!value) return '';
    if (value.type === 'literal') {
        return typeof value.value === 'string' ? value.value : JSON.stringify(value.value);
    }
    if (value.type === 'variable') {
        return `$${value.name}`;
    }
    if (value.type === 'reporter') {
        return `@${value.id}`;
    }
    return JSON.stringify(value);
}

// Parse edited value back to structure
function parseEditedValue(text) {
    text = text.trim();

    // Variable reference
    if (text.startsWith('$')) {
        return { type: 'variable', name: text.substring(1) };
    }

    // Node reference
    if (text.startsWith('@')) {
        return { type: 'reporter', id: text.substring(1) };
    }

    // Try JSON
    try {
        const parsed = JSON.parse(text);
        return { type: 'literal', value: parsed };
    } catch {
        // Treat as string literal
        return { type: 'literal', value: text };
    }
}

// Close modal
function closeModal() {
    elements.modal.classList.add('hidden');
    state.editingNode = null;
}

// Save node changes
function saveNodeChanges() {
    if (!state.editingNode) return;

    const newNodeId = document.getElementById('edit-node-id').value.trim();
    const newOpcode = document.getElementById('edit-opcode').value.trim();

    // Collect input changes
    const inputChanges = {};
    document.querySelectorAll('[data-input-key]').forEach(el => {
        const key = el.dataset.inputKey;
        inputChanges[key] = parseEditedValue(el.value);
    });

    // Collect config changes
    const configChanges = {};
    document.querySelectorAll('[data-config-key]').forEach(el => {
        const key = el.dataset.configKey;
        const value = el.value.trim();
        // Try to parse as number or keep as string
        configChanges[key] = isNaN(value) ? value : Number(value);
    });

    // Update the tree data
    const { node, path, nodeId } = state.editingNode;

    // Update node properties
    if (newOpcode) node.opcode = newOpcode;

    // Update inputs
    for (const [key, value] of Object.entries(inputChanges)) {
        if (node.inputs) {
            node.inputs[key] = value;
        }
    }

    // Update config
    for (const [key, value] of Object.entries(configChanges)) {
        if (node.config) {
            node.config[key] = { type: 'literal', value };
        }
    }

    // Handle node ID change
    if (newNodeId !== nodeId) {
        node.id = newNodeId;
    }

    // Re-render visualization
    renderVisualization();

    // Sync changes back to YAML (simplified - just update the editor with a note)
    syncTreeToEditor();

    closeModal();
}

// Sync tree changes back to editor (simplified version)
function syncTreeToEditor() {
    // For now, add a comment indicating changes were made via visualization
    // Full YAML regeneration would require a YAML library
    const currentContent = elements.editor.value;
    if (!currentContent.includes('# Modified via visualization')) {
        // Don't modify - just show a notification that changes were made visually
        console.log('Node changes applied to visualization. Re-parse to sync with editor.');
    }
}

// Render inputs form
function renderInputs() {
    const inputs = state.interface?.inputs || [];

    if (inputs.length === 0) {
        elements.inputsContainer.innerHTML = '<div class="placeholder">No inputs defined</div>';
        return;
    }

    elements.inputsContainer.innerHTML = inputs.map(name => `
        <div class="input-field">
            <label for="input-${escapeHtml(name)}">${escapeHtml(name)}:</label>
            <input type="text" id="input-${escapeHtml(name)}" name="${escapeHtml(name)}" placeholder="value">
        </div>
    `).join('');
}

// Get inputs from form
function getInputValues() {
    const inputs = state.interface?.inputs || [];
    if (inputs.length === 0) return null;

    const values = {};
    inputs.forEach(name => {
        const input = document.getElementById(`input-${name}`);
        if (input && input.value.trim()) {
            try {
                values[name] = JSON.parse(input.value);
            } catch {
                values[name] = input.value;
            }
        }
    });

    return Object.keys(values).length > 0 ? values : null;
}

// Execute workflow
async function executeWorkflow() {
    const content = elements.editor.value.trim();
    if (!content) {
        showError('No workflow to execute');
        return;
    }

    if (state.isExecuting) return;

    state.isExecuting = true;
    elements.executeBtn.disabled = true;
    elements.executeBtn.textContent = 'Running...';

    clearOutput();
    elements.resultContainer.classList.add('hidden');
    elements.resultContainer.classList.remove('error');

    try {
        const inputs = getInputValues();

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws/execute`);

        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: 'start',
                workflow: content,
                inputs: inputs,
                include_metrics: false
            }));
        };

        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);

            switch (msg.type) {
                case 'output':
                    appendOutput(msg.line);
                    break;
                case 'complete':
                    showResult(msg.result);
                    ws.close();
                    break;
                case 'error':
                    showError(msg.message);
                    ws.close();
                    break;
            }
        };

        ws.onerror = (error) => {
            showError('WebSocket connection error');
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            state.isExecuting = false;
            elements.executeBtn.disabled = false;
            elements.executeBtn.textContent = 'Execute';
        };

        state.ws = ws;
    } catch (error) {
        showError(error.message);
        state.isExecuting = false;
        elements.executeBtn.disabled = false;
        elements.executeBtn.textContent = 'Execute';
    }
}

// Append output line
function appendOutput(line) {
    const placeholder = elements.output.querySelector('.placeholder');
    if (placeholder) {
        placeholder.remove();
    }

    const lineEl = document.createElement('div');
    lineEl.className = 'output-line';
    lineEl.textContent = line;
    elements.output.appendChild(lineEl);

    elements.output.scrollTop = elements.output.scrollHeight;
}

// Show result
function showResult(result) {
    elements.resultContainer.classList.remove('hidden', 'error');
    elements.result.textContent = result !== null ? JSON.stringify(result, null, 2) : 'null';
}

// Show error
function showError(message) {
    elements.resultContainer.classList.remove('hidden');
    elements.resultContainer.classList.add('error');
    elements.resultContainer.querySelector('h3').textContent = 'Error:';
    elements.result.textContent = message;
}

// Clear output
function clearOutput() {
    elements.output.innerHTML = '<div class="placeholder">Click Execute to run the workflow</div>';
    elements.resultContainer.classList.add('hidden');
    elements.resultContainer.classList.remove('error');
    elements.resultContainer.querySelector('h3').textContent = 'Result:';
}

// Escape HTML
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Start application
init();
