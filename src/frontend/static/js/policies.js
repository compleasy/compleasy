// Policies.js - Handle ruleset sidebar and rule selection panel

// Toggle ruleset edit sidebar
function toggleRulesetEditPanel(rulesetId) {
    const panel = document.getElementById('ruleset-edit-panel');
    const wasHidden = panel.classList.contains('hidden');
    panel.classList.toggle('hidden');
    
    // If closing, check if we need to reopen the selection panel
    if (!wasHidden && panel.classList.contains('hidden')) {
        // Check if selection panel was open before
        const selectionPanel = document.getElementById('ruleset-selection-panel');
        if (selectionPanel && selectionPanel.dataset.wasOpen === 'true') {
            selectionPanel.classList.remove('hidden');
            selectionPanel.dataset.wasOpen = 'false';
        }
        return;
    }
    
    // Don't load data if closing
    if (panel.classList.contains('hidden')) {
        return;
    }
    
    // Update form action and title
    const form = document.getElementById('ruleset-edit-form');
    const title = document.getElementById('ruleset-edit-title');
    
    if (rulesetId) {
        // Edit mode
        form.action = `/ruleset/${rulesetId}/edit/`;
        title.textContent = 'Edit Ruleset';
        loadRulesetDetails(rulesetId);
    } else {
        // Create mode
        form.action = '/ruleset/create/';
        title.textContent = 'Create New Ruleset';
        loadRulesetDetails(); // Empty form
    }
}

// Open ruleset edit panel from selection panel (hides selection panel)
function openRulesetEditFromSelection(rulesetId) {
    const selectionPanel = document.getElementById('ruleset-selection-panel');
    if (selectionPanel && !selectionPanel.classList.contains('hidden')) {
        // Mark that selection panel was open
        selectionPanel.dataset.wasOpen = 'true';
        selectionPanel.classList.add('hidden');
    }
    
    // Open the edit panel
    toggleRulesetEditPanel(rulesetId);
}

// Close ruleset edit panel (used by cancel/close buttons)
function closeRulesetEditPanel() {
    const panel = document.getElementById('ruleset-edit-panel');
    if (panel && !panel.classList.contains('hidden')) {
        panel.classList.add('hidden');
        
        // Check if selection panel was open before
        const selectionPanel = document.getElementById('ruleset-selection-panel');
        if (selectionPanel && selectionPanel.dataset.wasOpen === 'true') {
            selectionPanel.classList.remove('hidden');
            selectionPanel.dataset.wasOpen = 'false';
        }
    }
}

// Load ruleset data into form
function loadRulesetDetails(rulesetId) {
    if (!rulesetId) {
        // Clear form for new ruleset
        document.getElementById('ruleset_name').value = '';
        document.getElementById('ruleset_description').value = '';
        document.getElementById('ruleset_id').value = '';
        document.getElementById('selected_rules').value = '';
        updateRulesCountDisplay([]);
        hideRulesetFormErrors();
        return;
    }
    
    // Convert rulesetId to a number
    rulesetId = Number(rulesetId);
    
    // Find ruleset in data (passed from Django)
    const ruleset = rulesets.find(r => r.id === rulesetId);
    if (!ruleset) {
        console.error('Ruleset not found:', rulesetId);
        return;
    }
    
    // Populate form fields
    document.getElementById('ruleset_name').value = ruleset.name;
    document.getElementById('ruleset_description').value = ruleset.description || '';
    document.getElementById('ruleset_id').value = ruleset.id;
    
    // Update rules display
    const rulesetRules = ruleset.rules || [];
    const ruleIds = rulesetRules.map(r => r.id).join(',');
    document.getElementById('selected_rules').value = ruleIds;
    updateRulesCountDisplay(rulesetRules);
    
    hideRulesetFormErrors();
}

// Update the rules count display in the ruleset edit sidebar
function updateRulesCountDisplay(selectedRules) {
    const countText = document.getElementById('rules-count-text');
    if (!countText) return;
    
    if (selectedRules.length === 0) {
        countText.textContent = 'No rules selected';
    } else if (selectedRules.length === 1) {
        countText.textContent = '1 rule selected';
    } else {
        countText.textContent = `${selectedRules.length} rules selected`;
    }
}

// Open rule selection panel from ruleset edit sidebar
function openRuleSelectionFromEdit() {
    const rulesetIdInput = document.getElementById('ruleset_id');
    const rulesetId = rulesetIdInput ? rulesetIdInput.value : null;
    
    // Store that we're opening from edit panel and hide it
    const editPanel = document.getElementById('ruleset-edit-panel');
    if (editPanel && !editPanel.classList.contains('hidden')) {
        editPanel.dataset.ruleSelectionOpen = 'true';
        editPanel.classList.add('hidden');
    }
    
    // Open rule selection panel
    toggleRuleSelectionPanel(rulesetId);
}

// Submit ruleset form via AJAX
function submitRulesetForm() {
    const form = document.getElementById('ruleset-edit-form');
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
            closeRulesetEditPanel();
            location.reload();
        } else {
            // Show errors
            showRulesetFormErrors(data.errors);
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showRulesetFormErrors(['An error occurred while saving.']);
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
}

// Show form errors
function showRulesetFormErrors(errors) {
    const errorContainer = document.getElementById('ruleset-form-errors');
    const errorList = document.getElementById('ruleset-error-list');
    
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

function hideRulesetFormErrors() {
    document.getElementById('ruleset-form-errors').classList.add('hidden');
}

// Toggle rule selection sidebar for assigning rules to ruleset
function toggleRuleSelectionPanel(rulesetId) {
    const panel = document.getElementById('rule-selection-panel');
    const wasHidden = panel.classList.contains('hidden');
    panel.classList.toggle('hidden');
    
    // Clear any error messages when opening the panel
    if (wasHidden && !panel.classList.contains('hidden')) {
        const errorContainer = document.getElementById('rule-selection-errors');
        if (errorContainer) {
            errorContainer.classList.add('hidden');
            errorContainer.textContent = '';
        }
    }
    
    // If closing, check if we need to reopen the edit panel
    if (!wasHidden && panel.classList.contains('hidden')) {
        const editPanel = document.getElementById('ruleset-edit-panel');
        if (editPanel && editPanel.dataset.ruleSelectionOpen === 'true') {
            editPanel.dataset.ruleSelectionOpen = 'false';
            editPanel.classList.remove('hidden');
        }
        return;
    }
    
    // Store the ruleset ID in the panel's data attribute
    if (rulesetId) {
        panel.dataset.rulesetId = rulesetId;
        
        if (!panel.classList.contains('hidden')) {
            selectRulesetRules(rulesetId);
        }
        
        // Update the form action dynamically
        const form = document.getElementById('rule-selection-form');
        if (form) {
            form.action = `/ruleset/${rulesetId}/edit/`;
        }
    } else {
        // For new ruleset, clear selections and set form action to create
        panel.dataset.rulesetId = '';
        const ruleCheckboxes = document.querySelectorAll('#rules input[type="checkbox"]');
        ruleCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        
        const form = document.getElementById('rule-selection-form');
        if (form) {
            form.action = '/ruleset/create/';
        }
    }
}

function selectRulesetRules(rulesetId) {
    // Convert the ruleset ID to a number
    rulesetId = Number(rulesetId);
    
    // Get the ruleset by ID
    const ruleset = rulesets.find(r => r.id === rulesetId);
    if (!ruleset) {
        console.error(`Ruleset with ID ${rulesetId} not found.`);
        return;
    }
    const rulesetRules = ruleset.rules || [];
    
    // Deselect all checkboxes first
    const ruleCheckboxes = document.querySelectorAll('#rules input[type="checkbox"]');
    ruleCheckboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Select the ruleset rules
    rulesetRules.forEach(rule => {
        const ruleCheckbox = document.querySelector(`#rules input[type="checkbox"][value="${rule.id}"]`);
        if (ruleCheckbox) {
            ruleCheckbox.checked = true;
        }
    });
}

function searchRuleByName(name) {
    const ruleCheckboxes = document.querySelectorAll('#rules > div');
    if (!name) {
        ruleCheckboxes.forEach(checkbox => checkbox.classList.remove('hidden'));
        return;
    }
    
    ruleCheckboxes.forEach(checkbox => {
        // Get the rule name from the checkbox label
        const ruleName = checkbox.querySelector('label').textContent.trim();
        if (ruleName.toLowerCase().includes(name.toLowerCase())) {
            checkbox.classList.remove('hidden');
        } else {
            checkbox.classList.add('hidden');
        }
    });
}

// Update selected rules in ruleset edit form when rules are selected
function updateSelectedRulesInEditForm() {
    const ruleCheckboxes = document.querySelectorAll('#rules input[type="checkbox"]');
    const selectedRuleIds = [];
    
    ruleCheckboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedRuleIds.push(checkbox.value);
        }
    });
    
    // Update hidden field in ruleset edit form
    const selectedRulesInput = document.getElementById('selected_rules');
    if (selectedRulesInput) {
        selectedRulesInput.value = selectedRuleIds.join(',');
    }
    
    // Update rules count display
    const selectedRules = selectedRuleIds.map(id => {
        const rule = rules.find(r => r.id === Number(id));
        return rule;
    }).filter(r => r !== undefined);
    
    updateRulesCountDisplay(selectedRules);
}

// Delete ruleset with confirmation
function deleteRuleset(rulesetId, rulesetName) {
    if (!confirm(`Are you sure you want to delete the ruleset "${rulesetName}"?\n\nThis action cannot be undone.`)) {
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
    fetch(`/ruleset/${rulesetId}/delete/`, {
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
            alert('Error deleting ruleset: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting ruleset. Please try again.');
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Ruleset edit panel close/cancel buttons - only within the ruleset-edit-panel
    const rulesetEditPanel = document.getElementById('ruleset-edit-panel');
    if (rulesetEditPanel) {
        const buttons = rulesetEditPanel.querySelectorAll('.ruleset-edit-panel-button');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeRulesetEditPanel();
            });
        });
    }
    
    // Ruleset form submission
    const rulesetForm = document.getElementById('ruleset-edit-form');
    if (rulesetForm) {
        rulesetForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitRulesetForm();
        });
    }
    
    // Rule selection panel buttons
    document.querySelectorAll('.rule-select-panel-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const panel = document.getElementById('rule-selection-panel');
            const rulesetId = panel ? panel.dataset.rulesetId : null;
            toggleRuleSelectionPanel(rulesetId);
        });
    });
    
    // Rule selection form submission - update ruleset edit form instead of submitting directly
    const ruleSelectionForm = document.getElementById('rule-selection-form');
    if (ruleSelectionForm) {
        ruleSelectionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const panel = document.getElementById('rule-selection-panel');
            const rulesetId = panel ? panel.dataset.rulesetId : null;
            
            // Update selected rules in ruleset edit form
            updateSelectedRulesInEditForm();
            
            // If editing existing ruleset, submit to update rules
            if (rulesetId) {
                const formData = new FormData(ruleSelectionForm);
                fetch(ruleSelectionForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(response => {
                    if (response.ok) {
                        // Close rule selection panel
                        toggleRuleSelectionPanel(rulesetId);
                        // Reload page to refresh data
                        location.reload();
                    } else {
                        // Try to parse error response
                        response.json().then(data => {
                            const errorContainer = document.getElementById('rule-selection-errors');
                            if (errorContainer) {
                                let errorMessage = 'Error updating rules';
                                if (data.errors) {
                                    // Handle different error formats
                                    if (data.errors.__all__ && Array.isArray(data.errors.__all__)) {
                                        errorMessage = data.errors.__all__[0];
                                    } else if (typeof data.errors === 'string') {
                                        errorMessage = data.errors;
                                    } else if (data.message) {
                                        errorMessage = data.message;
                                    }
                                } else if (data.message) {
                                    errorMessage = data.message;
                                }
                                errorContainer.textContent = errorMessage;
                                errorContainer.classList.remove('hidden');
                                // Scroll to error
                                errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            } else {
                                console.error('Error updating rules:', errorMessage);
                                alert(errorMessage);
                            }
                        }).catch(() => {
                            // If JSON parsing fails, show generic error
                            const errorContainer = document.getElementById('rule-selection-errors');
                            if (errorContainer) {
                                errorContainer.textContent = 'Error updating rules. Please try again.';
                                errorContainer.classList.remove('hidden');
                            } else {
                                alert('Error updating rules. Please try again.');
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorContainer = document.getElementById('rule-selection-errors');
                    if (errorContainer) {
                        errorContainer.textContent = 'Network error. Please check your connection and try again.';
                        errorContainer.classList.remove('hidden');
                    } else {
                        alert('Network error. Please check your connection and try again.');
                    }
                });
            } else {
                // For new ruleset, just close the panel (rules are stored in hidden field)
                toggleRuleSelectionPanel(null);
            }
        });
    }
    
    // Update selected rules when checkboxes change
    const rulesContainer = document.getElementById('rules');
    if (rulesContainer) {
        rulesContainer.addEventListener('change', function(e) {
            if (e.target.type === 'checkbox') {
                updateSelectedRulesInEditForm();
            }
        });
    }
});

