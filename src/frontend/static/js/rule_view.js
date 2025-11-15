function toggleRuleViewPanel(deviceId, ruleId) {
    const panel = document.getElementById('rule-view-panel');
    
    // Close other sidebars first
    closeOtherSidebars();
    
    // Toggle the panel
    panel.classList.toggle('hidden');
    
    // Don't load data if closing
    if (panel.classList.contains('hidden')) {
        return;
    }
    
    // Load rule evaluation data
    loadRuleEvaluation(deviceId, ruleId);
}

function closeOtherSidebars() {
    // Close rule edit panel
    const ruleEditPanel = document.getElementById('rule-edit-panel');
    if (ruleEditPanel && !ruleEditPanel.classList.contains('hidden')) {
        ruleEditPanel.classList.add('hidden');
    }
    
    // Close ruleset selection panel
    const rulesetSelectionPanel = document.getElementById('ruleset-selection-panel');
    if (rulesetSelectionPanel && !rulesetSelectionPanel.classList.contains('hidden')) {
        rulesetSelectionPanel.classList.add('hidden');
    }
    
    // Close ruleset edit panel
    const rulesetEditPanel = document.getElementById('ruleset-edit-panel');
    if (rulesetEditPanel && !rulesetEditPanel.classList.contains('hidden')) {
        rulesetEditPanel.classList.add('hidden');
    }
}

function loadRuleEvaluation(deviceId, ruleId) {
    // Show loading state
    const actualValueDiv = document.getElementById('rule-view-actual');
    if (actualValueDiv) {
        actualValueDiv.innerHTML = '<span class="text-gray-500 italic">Loading...</span>';
    }
    
    // Fetch evaluation data
    fetch(`/device/${deviceId}/rule/${ruleId}/evaluate/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            displayRuleEvaluation(data);
        } else {
            showRuleEvaluationError(data.error || 'Failed to load rule evaluation');
        }
    })
    .catch(error => {
        console.error('Error loading rule evaluation:', error);
        showRuleEvaluationError('An error occurred while loading rule evaluation.');
    });
}

function displayRuleEvaluation(data) {
    const rule = data.rule;
    const queryComponents = data.query_components;
    const evaluation = data.evaluation;
    
    // Display rule basic info
    const nameDiv = document.getElementById('rule-view-name');
    if (nameDiv) {
        nameDiv.textContent = rule.name || '-';
    }
    
    const descriptionDiv = document.getElementById('rule-view-description');
    if (descriptionDiv) {
        descriptionDiv.textContent = rule.description || '-';
    }
    
    const statusDiv = document.getElementById('rule-view-status');
    if (statusDiv) {
        statusDiv.textContent = rule.enabled ? 'Enabled' : 'Disabled';
        // Reset classes and add appropriate ones
        statusDiv.className = 'mt-1 p-2 border rounded-md';
        if (rule.enabled) {
            statusDiv.classList.add('bg-green-50', 'border-green-200', 'text-green-800');
        } else {
            statusDiv.classList.add('bg-gray-50', 'border-gray-200', 'text-gray-600');
        }
    }
    
    // Display query evaluation
    const queryDiv = document.getElementById('rule-view-query');
    if (queryDiv) {
        queryDiv.textContent = rule.rule_query || '-';
    }
    
    const fieldDiv = document.getElementById('rule-view-field');
    if (fieldDiv) {
        fieldDiv.textContent = queryComponents.field || '-';
    }
    
    const operatorDiv = document.getElementById('rule-view-operator');
    if (operatorDiv) {
        operatorDiv.textContent = queryComponents.operator || '-';
    }
    
    const expectedDiv = document.getElementById('rule-view-expected');
    if (expectedDiv) {
        expectedDiv.textContent = queryComponents.expected_value || '-';
    }
    
    // Display actual value
    const actualDiv = document.getElementById('rule-view-actual');
    if (actualDiv) {
        if (!evaluation.key_found) {
            actualDiv.innerHTML = '<span class="text-red-600 font-semibold">Key not found in report</span>';
        } else {
            actualDiv.textContent = evaluation.actual_value || '-';
        }
    }
    
    // Display evaluation result
    const resultDiv = document.getElementById('rule-view-result');
    if (resultDiv) {
        // Reset classes
        resultDiv.className = 'mt-1 p-2 border rounded-md font-semibold text-center';
        
        if (evaluation.result === null || evaluation.result === undefined) {
            resultDiv.textContent = 'Evaluation Error';
            resultDiv.classList.add('bg-yellow-100', 'border-yellow-400', 'text-yellow-800');
        } else if (evaluation.passed) {
            resultDiv.textContent = 'Pass';
            resultDiv.classList.add('bg-green-100', 'border-green-400', 'text-green-800');
        } else {
            resultDiv.textContent = 'Fail';
            resultDiv.classList.add('bg-red-100', 'border-red-400', 'text-red-800');
        }
    }
}

function showRuleEvaluationError(errorMessage) {
    const actualDiv = document.getElementById('rule-view-actual');
    if (actualDiv) {
        actualDiv.innerHTML = `<span class="text-red-600 font-semibold">${errorMessage}</span>`;
    }
    
    const resultDiv = document.getElementById('rule-view-result');
    if (resultDiv) {
        resultDiv.textContent = 'Error';
        resultDiv.className = 'mt-1 p-2 border rounded-md font-semibold text-center';
        resultDiv.classList.add('bg-red-100', 'border-red-400', 'text-red-800');
    }
}

function closeRuleViewPanel() {
    const panel = document.getElementById('rule-view-panel');
    if (panel && !panel.classList.contains('hidden')) {
        panel.classList.add('hidden');
    }
}

// Event listeners
function attachRuleViewPanelListeners() {
    // Rule view panel close/cancel buttons
    const ruleViewPanel = document.getElementById('rule-view-panel');
    if (ruleViewPanel) {
        const buttons = ruleViewPanel.querySelectorAll('.rule-view-panel-button');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeRuleViewPanel();
            });
        });
    }
}

// Attach listeners when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachRuleViewPanelListeners);
} else {
    // DOM is already ready
    attachRuleViewPanelListeners();
}

