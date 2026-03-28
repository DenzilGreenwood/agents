// CIAF Demo App - Interactive Frontend
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '/api';

let selectedAgent = null;
let systemInitialized = false;

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    console.log('CIAF Demo App initializing...');
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize system
    await initializeSystem();
    
    // Load initial data
    await Promise.all([
        loadAgents(),
        loadRoles()
    ]);
    
    // Setup code tabs
    setupCodeTabs();
    
    console.log('CIAF Demo App ready');
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('executeBtn').addEventListener('click', executeAction);
    document.getElementById('elevateBtn').addEventListener('click', requestElevation);
    document.getElementById('refreshAuditBtn').addEventListener('click', loadAuditTrail);
    document.getElementById('agentSelect').addEventListener('change', (e) => {
        selectedAgent = e.target.value;
    });
}

// Initialize CIAF system
async function initializeSystem() {
    try {
        updateStatus('Initializing...', 'warning');
        
        const response = await fetch(`${API_BASE}/init`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            systemInitialized = true;
            updateStatus('System Online', 'success');
        } else {
            updateStatus('Initialization Failed', 'error');
            showError('Failed to initialize CIAF system');
        }
    } catch (error) {
        console.error('Initialization error:', error);
        updateStatus('Connection Error', 'error');
    }
}

// Update status badge
function updateStatus(text, type = 'success') {
    const statusText = document.getElementById('statusText');
    const statusDot = document.querySelector('.status-dot');
    
    statusText.textContent = text;
    
    const colors = {
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
    };
    
    statusDot.style.background = colors[type] || colors.success;
}

// Load agents
async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/agents`);
        const data = await response.json();
        
        const container = document.getElementById('agentsContainer');
        const select = document.getElementById('agentSelect');
        
        if (!data.agents || data.agents.length === 0) {
            container.innerHTML = '<div class="loading">No agents available</div>';
            return;
        }
        
        // Render agent cards
        container.innerHTML = data.agents.map(agent => `
            <div class="agent-card" data-agent-id="${agent.id}" onclick="selectAgent('${agent.id}')">
                <div class="agent-name">🤖 ${agent.name}</div>
                <div class="agent-id">${agent.id}</div>
                <div class="agent-info">
                    <div class="agent-badge">🏢 Tenant: ${agent.tenant}</div>
                    <div class="agent-badge">🎭 Roles: ${agent.roles.join(', ')}</div>
                </div>
            </div>
        `).join('');
        
        // Populate select dropdown
        select.innerHTML = '<option value="">-- Select Agent --</option>' + 
            data.agents.map(agent => 
                `<option value="${agent.id}">${agent.name} (${agent.tenant})</option>`
            ).join('');
            
    } catch (error) {
        console.error('Error loading agents:', error);
        showError('Failed to load agents');
    }
}

// Select agent
function selectAgent(agentId) {
    selectedAgent = agentId;
    
    // Update UI
    document.querySelectorAll('.agent-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    const selectedCard = document.querySelector(`[data-agent-id="${agentId}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    // Update select dropdown
    document.getElementById('agentSelect').value = agentId;
}

// Load roles
async function loadRoles() {
    try {
        const response = await fetch(`${API_BASE}/roles`);
        const data = await response.json();
        
        const container = document.getElementById('rolesContainer');
        
        if (!data.roles || data.roles.length === 0) {
            container.innerHTML = '<div class="loading">No roles available</div>';
            return;
        }
        
        container.innerHTML = data.roles.map(role => `
            <div class="role-card">
                <div class="role-name">🎭 ${role.name}</div>
                <ul class="permission-list">
                    ${role.permissions.map(perm => `
                        <li class="permission-item">
                            <div>
                                <strong>${perm.action}</strong> on <em>${perm.resource_type}</em>
                                ${perm.description ? `<br><small>${perm.description}</small>` : ''}
                            </div>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading roles:', error);
        showError('Failed to load roles');
    }
}

// Execute action
async function executeAction() {
    const agentId = document.getElementById('agentSelect').value;
    const action = document.getElementById('actionSelect').value;
    const resourceId = document.getElementById('resourceId').value;
    const resourceTenant = document.getElementById('resourceTenant').value;
    const justification = document.getElementById('justification').value;
    
    if (!agentId) {
        showResult('Please select an agent', 'error');
        return;
    }
    
    if (!resourceId) {
        showResult('Please enter a resource ID', 'error');
        return;
    }
    
    const resultPanel = document.getElementById('executionResult');
    resultPanel.classList.remove('hidden');
    resultPanel.className = 'result-panel warning';
    resultPanel.innerHTML = '<div class="result-header">⏳ Executing...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                agent_id: agentId,
                action: action,
                resource_id: resourceId,
                resource_tenant: resourceTenant,
                justification: justification || 'Demo execution'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.allowed && data.executed) {
                showResult(
                    `✓ Action Executed Successfully\n\n${JSON.stringify(data.result, null, 2)}`, 
                    'success',
                    data.obligations
                );
            } else {
                showResult(
                    `✗ Action Denied\n\nReason: ${data.reason}\n\n${data.reason.includes('elevation') ? 'Hint: Try requesting privilege elevation first.' : ''}`, 
                    'error'
                );
            }
            
            // Refresh audit trail
            setTimeout(loadAuditTrail, 500);
        } else {
            showResult(`Error: ${data.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Execution error:', error);
        showResult(`Request failed: ${error.message}`, 'error');
    }
}

// Request privilege elevation
async function requestElevation() {
    const agentId = document.getElementById('agentSelect').value;
    
    if (!agentId) {
        showResult('Please select an agent first', 'error');
        return;
    }
    
    const resultPanel = document.getElementById('executionResult');
    resultPanel.classList.remove('hidden');
    resultPanel.className = 'result-panel warning';
    resultPanel.innerHTML = '<div class="result-header">⏳ Requesting elevation...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/elevate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                agent_id: agentId,
                elevated_role: 'data_admin',
                duration_minutes: 30,
                ticket_reference: `DEMO-${Date.now()}`
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showResult(
                `✓ Privilege Elevation Granted\n\nGrant ID: ${data.grant_id}\n${data.expires_at ? `Expires: ${new Date(data.expires_at).toLocaleString()}` : 'Duration: 30 minutes'}\nElevated Role: ${data.elevated_role}\n\nYou can now execute sensitive operations like delete_data.`, 
                'success'
            );
        } else {
            showResult(`Error: ${data.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Elevation error:', error);
        showResult(`Request failed: ${error.message}`, 'error');
    }
}

// Show execution result
function showResult(message, type = 'success', obligations = []) {
    const resultPanel = document.getElementById('executionResult');
    resultPanel.classList.remove('hidden');
    resultPanel.className = `result-panel ${type}`;
    
    const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : '⚠';
    const title = type === 'success' ? 'Success' : type === 'error' ? 'Failed' : 'Warning';
    
    let obligationsHtml = '';
    if (obligations && obligations.length > 0) {
        obligationsHtml = `
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <strong>Compliance Obligations:</strong>
                <ul style="margin-left: 1.5rem; margin-top: 0.5rem;">
                    ${obligations.map(o => `<li>${o}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    resultPanel.innerHTML = `
        <div class="result-header">${icon} ${title}</div>
        <div class="result-content">${message}</div>
        ${obligationsHtml}
    `;
}

// Show error
function showError(message) {
    showResult(message, 'error');
}

// Load audit trail
async function loadAuditTrail() {
    try {
        const response = await fetch(`${API_BASE}/audit`);
        const data = await response.json();
        
        const container = document.getElementById('auditContainer');
        const chainStatus = document.getElementById('chainStatus');
        const totalActions = document.getElementById('totalActions');
        
        // Update status badges
        chainStatus.textContent = `Chain Status: ${data.chain_valid ? '✓ Valid' : '✗ Invalid'}`;
        chainStatus.style.background = data.chain_valid ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)';
        chainStatus.style.color = data.chain_valid ? '#10b981' : '#ef4444';
        
        totalActions.textContent = `Total Actions: ${data.total_actions}`;
        
        // Render audit entries
        const actions = data.recent_actions || data.execution_log || [];
        
        if (actions.length === 0) {
            container.innerHTML = '<div class="loading">No actions recorded yet</div>';
            return;
        }
        
        container.innerHTML = actions.reverse().map(entry => {
            const timestamp = entry.timestamp || new Date().toISOString();
            const allowed = entry.allowed !== undefined ? entry.allowed : true;
            
            return `
                <div class="audit-entry ${allowed ? '' : 'denied'}">
                    <div class="audit-timestamp">${new Date(timestamp).toLocaleString()}</div>
                    <div class="audit-details">
                        <div class="audit-action">
                            ${entry.action} 
                            ${entry.hash ? `<span style="font-size: 0.75rem; color: #cbd5e1;">(${entry.hash})</span>` : ''}
                        </div>
                        <div class="audit-resource">
                            Agent: ${entry.agent || entry.principal_id} → Resource: ${entry.resource || entry.resource_id}
                        </div>
                        ${entry.reason ? `<div style="font-size: 0.75rem; color: #cbd5e1; margin-top: 0.25rem;">${entry.reason}</div>` : ''}
                    </div>
                    <div class="audit-status-badge ${allowed ? 'allowed' : 'denied'}">
                        ${allowed ? (entry.executed !== false ? '✓ Allowed' : '✓ Allowed (Not Executed)') : '✗ Denied'}
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading audit trail:', error);
        document.getElementById('auditContainer').innerHTML = 
            '<div class="loading">Error loading audit trail</div>';
    }
}

// Setup code tabs
function setupCodeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const codePanels = document.querySelectorAll('.code-panel');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            
            // Update buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update panels
            codePanels.forEach(panel => {
                if (panel.dataset.tab === tab) {
                    panel.classList.add('active');
                } else {
                    panel.classList.remove('active');
                }
            });
        });
    });
}

// Auto-refresh audit trail every 10 seconds
setInterval(() => {
    if (systemInitialized && document.getElementById('auditContainer').children.length > 0) {
        loadAuditTrail();
    }
}, 10000);
