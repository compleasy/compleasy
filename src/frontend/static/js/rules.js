function toggleRuleEditPanel(ruleId) {
    const panel = document.getElementById('rule-edit-panel');
    if (!panel) {
        console.error('Rule edit panel not found in DOM');
        return;
    }
    
    // If ruleId is provided (including null for create mode), show the panel
    // If ruleId is undefined, toggle the panel
    if (ruleId !== undefined) {
        // Show the panel
        panel.classList.remove('hidden');
    } else {
        // Toggle the panel
        panel.classList.toggle('hidden');
        
        // If we just closed it, return early
        if (panel.classList.contains('hidden')) {
            return;
        }
    }
    
    // Update the form action and title dynamically
    const form = document.getElementById('rule-edit-form');
    const title = document.getElementById('rule-edit-title');
    
    if (!form || !title) {
        console.error('Rule edit form or title not found in DOM', { form: !!form, title: !!title });
        // Panel is already shown, so just return
        return;
    }
    
    if (ruleId) {
        // Edit mode
        form.action = `/rule/${ruleId}/edit/`;
        title.textContent = 'Edit Rule';
        loadRuleDetails(ruleId);
    } else {
        // Create mode (ruleId is null)
        form.action = '/rule/create/';
        title.textContent = 'Create New Rule';
        loadRuleDetails();
    }
}

// Open rule edit panel from selection panel (hides selection panel)
function openRuleEditFromSelection(ruleId) {
    const selectionPanel = document.getElementById('rule-selection-panel');
    if (selectionPanel && !selectionPanel.classList.contains('hidden')) {
        // Mark that selection panel was open
        selectionPanel.dataset.wasOpen = 'true';
        selectionPanel.classList.add('hidden');
    }
    
    // Open the edit panel
    toggleRuleEditPanel(ruleId);
}
function loadRuleDetails(ruleId) {
    // Empty data if ruleId is not provided (i.e. when creating a new rule)
    if (!ruleId) {
        const enabledCheckbox = document.getElementById('rule_enabled');
        const enabledMessage = document.getElementById('rule_enabled_message');
        const nameField = document.getElementById('rule_name');
        const descField = document.getElementById('rule_description');
        const queryField = document.getElementById('rule_query');
        const idField = document.getElementById('rule_id');
        
        if (enabledCheckbox) enabledCheckbox.checked = false;
        if (enabledMessage) enabledMessage.textContent = 'DISABLED';
        if (nameField) nameField.value = '';
        if (descField) descField.value = '';
        if (queryField) queryField.value = '';
        if (idField) idField.value = '';
        hideRuleFormErrors();
        return;
    }
    
    // Convert ruleId to a number
    ruleId = Number(ruleId);
    
    // Get rule details by ID (check if rules is defined)
    if (typeof rules === 'undefined') {
        console.error('Rules data not available');
        return;
    }
    
    const rule = rules.find(r => r.id === ruleId);
    if (!rule) {
        console.error('Rule not found:', ruleId);
        return;
    }
    
    // Populate the form fields with the rule details
    const enabledCheckbox = document.getElementById('rule_enabled');
    const enabledMessage = document.getElementById('rule_enabled_message');
    const nameField = document.getElementById('rule_name');
    const descField = document.getElementById('rule_description');
    const queryField = document.getElementById('rule_query');
    const idField = document.getElementById('rule_id');
    
    if (enabledCheckbox) enabledCheckbox.checked = rule.enabled;
    if (enabledMessage) enabledMessage.textContent = rule.enabled ? 'ENABLED' : 'DISABLED';
    if (nameField) nameField.value = rule.name;
    if (descField) descField.value = rule.description || '';
    if (queryField) queryField.value = rule.rule_query;
    if (idField) idField.value = rule.id;
    hideRuleFormErrors();
}
function toggleRuleStatus() {
    const checkbox = document.getElementById('rule_enabled');
    const message = document.getElementById('rule_enabled_message');
    message.textContent = checkbox.checked ? 'ENABLED' : 'DISABLED';
}

// Submit rule form via AJAX
function submitRuleForm() {
    const form = document.getElementById('rule-edit-form');
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Show loading state
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Saving...';
    submitButton.disabled = true;
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close panel and reload page
            toggleRuleEditPanel();
            location.reload();
        } else {
            // Show errors
            showRuleFormErrors(data.errors);
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showRuleFormErrors(['An error occurred while saving.']);
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
}

// Show form errors
function showRuleFormErrors(errors) {
    const errorContainer = document.getElementById('rule-form-errors');
    const errorList = document.getElementById('rule-error-list');
    
    errorList.innerHTML = '';
    
    if (typeof errors === 'object' && !Array.isArray(errors)) {
        // Django form errors: {field: [errors]}
        for (const [field, messages] of Object.entries(errors)) {
            messages.forEach(message => {
                const li = document.createElement('li');
                li.textContent = `${field}: ${message}`;
                errorList.appendChild(li);
            });
        }
    } else if (Array.isArray(errors)) {
        // Simple error messages
        errors.forEach(message => {
            const li = document.createElement('li');
            li.textContent = message;
            errorList.appendChild(li);
        });
    }
    
    errorContainer.classList.remove('hidden');
}

function hideRuleFormErrors() {
    document.getElementById('rule-form-errors').classList.add('hidden');
}

// Close rule edit panel (used by cancel/close buttons)
function closeRuleEditPanel() {
    const panel = document.getElementById('rule-edit-panel');
    if (panel && !panel.classList.contains('hidden')) {
        panel.classList.add('hidden');
        
        // Check if selection panel was open before
        const selectionPanel = document.getElementById('rule-selection-panel');
        if (selectionPanel && selectionPanel.dataset.wasOpen === 'true') {
            selectionPanel.classList.remove('hidden');
            selectionPanel.dataset.wasOpen = 'false';
        }
    }
}

// Delete rule with confirmation
function deleteRule(ruleId, ruleName) {
    if (!confirm(`Are you sure you want to delete the rule "${ruleName}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                      document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    
    if (!csrftoken) {
        alert('Error: CSRF token not found. Please refresh the page and try again.');
        return;
    }
    
    // Send DELETE request via POST (Django doesn't support DELETE method easily)
    fetch(`/rule/${ruleId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload page to show updated list
            location.reload();
        } else {
            alert('Error deleting rule: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting rule. Please try again.');
    });
}

// Event listeners
function attachRuleEditPanelListeners() {
    // Rule edit panel close/cancel buttons - only within the rule-edit-panel
    const ruleEditPanel = document.getElementById('rule-edit-panel');
    if (ruleEditPanel) {
        const buttons = ruleEditPanel.querySelectorAll('.rule-edit-panel-button');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeRuleEditPanel();
            });
        });
    }
    
    // Rule form submission
    const ruleForm = document.getElementById('rule-edit-form');
    if (ruleForm) {
        ruleForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitRuleForm();
        });
    }
    
    // Buttons in rule selection sidebar that should open rule edit panel
    // Use event delegation for all buttons (better Firefox compatibility)
    const ruleSelectionPanel = document.getElementById('rule-selection-panel');
    if (ruleSelectionPanel) {
        ruleSelectionPanel.addEventListener('click', function(e) {
            // Check if the clicked element or its parent has the rule-edit-panel-button class
            const button = e.target.closest('.rule-edit-panel-button');
            if (button) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                
                // Check if it has data-rule-id (edit button) or not (create button)
                const ruleId = button.hasAttribute('data-rule-id') ? button.dataset.ruleId : null;
                
                // Always use openRuleEditFromSelection to properly handle panel state
                openRuleEditFromSelection(ruleId);
            }
        });
    }
}

// Attach listeners when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachRuleEditPanelListeners);
} else {
    // DOM is already ready
    attachRuleEditPanelListeners();
}