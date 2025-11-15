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
        // Try to parse JSON even if response is not ok
        return response.json().then(data => {
            if (!response.ok) {
                // If response has an error message, use it
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            return data;
        });
    })
    .then(data => {
        if (data.success) {
            displayRuleEvaluation(data);
        } else {
            // Even on error, try to display rule info if available
            if (data.rule) {
                displayRuleBasicInfo(data.rule);
            }
            // Show error in a more visible way - update the result field and show error message
            const resultDiv = document.getElementById('rule-view-result');
            if (resultDiv) {
                resultDiv.textContent = 'Error';
                resultDiv.className = 'mt-1 p-2 border rounded-md font-semibold text-center';
                resultDiv.classList.add('bg-red-100', 'border-red-400', 'text-red-800');
            }
            showRuleEvaluationError(data.error || 'Failed to load rule evaluation');
        }
    })
    .catch(error => {
        console.error('Error loading rule evaluation:', error);
        showRuleEvaluationError(error.message || 'An error occurred while loading rule evaluation.');
    });
}

function displayRuleBasicInfo(rule) {
    // Display rule basic info
    const nameDiv = document.getElementById('rule-view-name');
    if (nameDiv) {
        nameDiv.textContent = rule.name || '-';
    }
    
    const descriptionDiv = document.getElementById('rule-view-description');
    if (descriptionDiv) {
        descriptionDiv.textContent = rule.description || '-';
    }
    
    // Show/hide disabled label and query evaluation section
    const disabledLabel = document.getElementById('rule-view-disabled-label');
    const queryEvaluationSection = document.getElementById('rule-view-query-evaluation');
    
    if (rule.enabled) {
        // Rule is enabled - hide disabled label, show query evaluation
        if (disabledLabel) {
            disabledLabel.classList.add('hidden');
        }
        if (queryEvaluationSection) {
            queryEvaluationSection.classList.remove('hidden');
        }
    } else {
        // Rule is disabled - show disabled label, hide query evaluation
        if (disabledLabel) {
            disabledLabel.classList.remove('hidden');
        }
        if (queryEvaluationSection) {
            queryEvaluationSection.classList.add('hidden');
        }
    }
}

function displayRuleEvaluation(data) {
    const rule = data.rule;
    const evaluation = data.evaluation;
    
    // Display rule basic info
    displayRuleBasicInfo(rule);
    
    // Display query evaluation
    const queryDiv = document.getElementById('rule-view-query');
    if (queryDiv) {
        // Use data.query if available, otherwise fall back to rule.rule_query
        queryDiv.textContent = data.query || rule.rule_query || '-';
    }
    
    // Display evaluation details
    const actualDiv = document.getElementById('rule-view-actual');
    if (actualDiv) {
        // Reset classes
        actualDiv.className = 'mt-1 p-2 bg-gray-50 border border-gray-200 rounded-md text-sm';
        
        if (evaluation.result === null || evaluation.result === undefined) {
            actualDiv.innerHTML = '<span class="text-red-600 font-semibold">Query evaluation failed - invalid syntax</span>';
        } else if (!evaluation.passed && evaluation.field_values && Object.keys(evaluation.field_values).length > 0) {
            // Rule failed - show the actual field values from the report
            let html = '<div class="space-y-1">';
            html += '<div class="text-gray-600 text-xs mb-2">Actual values from report:</div>';
            for (const [field, value] of Object.entries(evaluation.field_values)) {
                html += `<div class="font-mono text-xs"><span class="font-semibold text-gray-700">${field}</span> = <span class="text-gray-900">${value}</span></div>`;
            }
            html += '</div>';
            actualDiv.innerHTML = html;
        } else {
            // Rule passed or no field values available - show evaluation result
            const resultText = evaluation.result ? 'true' : 'false';
            actualDiv.innerHTML = `<span class="text-gray-700">Query evaluated to: <strong>${resultText}</strong></span>`;
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

