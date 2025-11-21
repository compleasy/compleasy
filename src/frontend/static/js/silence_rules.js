// Silence Rules Sidebar Management

let silenceRules = [];

// Event delegation for Firefox compatibility
document.addEventListener('DOMContentLoaded', function() {
    const listPanel = document.getElementById('silence-rules-panel');
    if (!listPanel) {
        return;
    }

    // Use event delegation for all buttons in the list panel
    listPanel.addEventListener('click', function(e) {
        const closeBtn = e.target.closest('.silence-rules-panel-button');
        if (closeBtn) {
            e.preventDefault();
            e.stopPropagation();
            toggleSilenceRulesPanel();
            return;
        }

        const editBtn = e.target.closest('[data-edit-rule]');
        if (editBtn) {
            e.preventDefault();
            e.stopPropagation();
            const ruleId = parseInt(editBtn.getAttribute('data-edit-rule'));
            openSilenceRuleEditFromList(ruleId);
            return;
        }

        const deleteBtn = e.target.closest('[data-delete-rule]');
        if (deleteBtn) {
            e.preventDefault();
            e.stopPropagation();
            const ruleId = parseInt(deleteBtn.getAttribute('data-delete-rule'));
            if (confirm('Are you sure you want to delete this silence rule?')) {
                deleteSilenceRule(ruleId);
            }
            return;
        }

        const toggleBtn = e.target.closest('[data-toggle-rule]');
        if (toggleBtn) {
            e.preventDefault();
            e.stopPropagation();
            const ruleId = parseInt(toggleBtn.getAttribute('data-toggle-rule'));
            toggleSilenceRule(ruleId);
            return;
        }

        const cancelBtn = e.target.closest('#silence-rule-cancel-btn');
        if (cancelBtn) {
            e.preventDefault();
            e.stopPropagation();
            return;
        }
    });

    // Event delegation for edit panel buttons
    const editPanel = document.getElementById('silence-rule-edit-panel');
    if (editPanel) {
        editPanel.addEventListener('click', function(e) {
            const closeBtn = e.target.closest('.silence-rule-edit-panel-button');
            if (closeBtn) {
                e.preventDefault();
                e.stopPropagation();
                closeSilenceRuleEditPanel();
            }
        });
    }

    // Handle form submission
    const form = document.getElementById('silence-rule-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitSilenceRuleForm();
        });
    }
});

function toggleSilenceRulesPanel() {
    const panel = document.getElementById('silence-rules-panel');
    panel.classList.toggle('hidden');
    
    if (!panel.classList.contains('hidden')) {
        loadSilenceRules();
    } else {
        closeSilenceRuleEditPanel(true);
    }
}

function openSilenceRuleEditFromList(ruleId) {
    const listPanel = document.getElementById('silence-rules-panel');
    if (listPanel && !listPanel.classList.contains('hidden')) {
        listPanel.dataset.wasOpen = 'true';
        listPanel.classList.add('hidden');
    }
    toggleSilenceRuleEditPanel(ruleId);
}

function toggleSilenceRuleEditPanel(ruleId) {
    const panel = document.getElementById('silence-rule-edit-panel');
    if (!panel) {
        console.error('Silence rule edit panel not found in DOM');
        return;
    }

    panel.classList.remove('hidden');

    const form = document.getElementById('silence-rule-form');
    const title = document.getElementById('silence-rule-edit-title');

    if (!form || !title) {
        console.error('Silence rule edit form or title missing from DOM');
        return;
    }

    if (ruleId) {
        form.action = `/activity/silence/${ruleId}/edit/`;
        title.textContent = 'Edit Silence Rule';
        loadSilenceRuleDetails(ruleId);
    } else {
        form.action = '/activity/silence/create/';
        title.textContent = 'Add Silence Rule';
        loadSilenceRuleDetails();
    }
}

function closeSilenceRuleEditPanel(forceOnly = false) {
    const panel = document.getElementById('silence-rule-edit-panel');
    if (panel && !panel.classList.contains('hidden')) {
        panel.classList.add('hidden');
    }

    if (forceOnly) {
        return;
    }

    const listPanel = document.getElementById('silence-rules-panel');
    if (listPanel && listPanel.dataset.wasOpen === 'true') {
        listPanel.classList.remove('hidden');
        listPanel.dataset.wasOpen = 'false';
        loadSilenceRules();
    }
}

function loadSilenceRuleDetails(ruleId) {
    if (!ruleId) {
        document.getElementById('silence_key_pattern').value = '';
        document.getElementById('silence_event_type').value = 'all';
        document.getElementById('silence_host_pattern').value = '*';
        document.getElementById('silence_is_active').checked = true;
        document.getElementById('silence_rule_id').value = '';
        hideFormErrors();
        return;
    }

    ruleId = Number(ruleId);
    const rule = silenceRules.find(r => r.id === ruleId);
    if (!rule) {
        console.error('Rule not found:', ruleId);
        return;
    }

    document.getElementById('silence_key_pattern').value = rule.key_pattern;
    document.getElementById('silence_event_type').value = rule.event_type;
    document.getElementById('silence_host_pattern').value = rule.host_pattern;
    document.getElementById('silence_is_active').checked = rule.is_active;
    document.getElementById('silence_rule_id').value = ruleId;
    hideFormErrors();
}

function loadSilenceRules() {
    const container = document.getElementById('silence-rules-container');
    container.innerHTML = '<p class="text-sm text-gray-500">Loading rules...</p>';
    
    fetch('/activity/silence/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => response.json())
    .then(data => {
        silenceRules = data.rules || [];
        renderSilenceRulesList();
    })
    .catch(error => {
        console.error('Error loading silence rules:', error);
        container.innerHTML = '<p class="text-sm text-red-500">Error loading rules</p>';
    });
}

function renderSilenceRulesList() {
    const container = document.getElementById('silence-rules-container');
    
    if (silenceRules.length === 0) {
        container.innerHTML = '<p class="text-sm text-gray-500">No silence rules configured. Add one below.</p>';
        return;
    }
    
    container.innerHTML = silenceRules.map(rule => {
        const eventTypeLabels = {
            'all': 'All',
            'added': 'Added',
            'changed': 'Changed',
            'removed': 'Removed',
        };
        const eventTypeLabel = eventTypeLabels[rule.event_type] || rule.event_type;
        const statusClass = rule.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
        const statusText = rule.is_active ? 'Active' : 'Inactive';
        
        return `
            <div class="border border-gray-200 rounded-lg p-3 group/rule ${!rule.is_active ? 'opacity-60' : ''}">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="font-semibold text-gray-900">${escapeHtml(rule.key_pattern)}</div>
                        <div class="text-sm text-gray-600 mt-1">
                            <span class="inline-block px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                                ${escapeHtml(eventTypeLabel)}
                            </span>
                            <span class="text-gray-500">Host: ${escapeHtml(rule.host_pattern)}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        <button type="button" data-toggle-rule="${rule.id}" 
                                class="inline-flex items-center cursor-pointer focus:outline-none" 
                                title="${rule.is_active ? 'Deactivate' : 'Activate'}">
                            <div class="relative w-11 h-6 ${rule.is_active ? 'bg-blue-600' : 'bg-gray-200'} rounded-full transition-colors">
                                <div class="absolute top-[2px] start-[2px] bg-white border border-gray-300 rounded-full h-5 w-5 transition-transform ${rule.is_active ? 'translate-x-full rtl:-translate-x-full' : ''}"></div>
                            </div>
                        </button>
                        <button type="button" data-edit-rule="${rule.id}" 
                                class="group relative rounded-full p-1 bg-transparent text-gray-600 hover:text-gray-800" title="Edit">
                            <div class="opacity-0 group-hover:opacity-100 absolute inset-0 bg-black/10 rounded-full"></div>
                            <svg class="size-4 invisible group-hover/rule:visible relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                                xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                                    d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125">
                                </path>
                            </svg>
                        </button>
                        <button type="button" data-delete-rule="${rule.id}" 
                                class="text-red-600 hover:text-red-800" title="Delete">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                                xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16">
                                </path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function submitSilenceRuleForm() {
    const form = document.getElementById('silence-rule-form');
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
            // Reload rules list
            loadSilenceRules();
            submitButton.textContent = originalText;
            submitButton.disabled = false;
            closeSilenceRuleEditPanel();
        } else {
            // Show errors
            showFormErrors(data.errors);
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFormErrors(['An error occurred while saving.']);
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
}

function deleteSilenceRule(ruleId) {
    const csrftoken = getCsrfToken();
    if (!csrftoken || csrftoken.length < 32) {
        console.error('Invalid CSRF token:', csrftoken ? `length=${csrftoken.length}` : 'not found');
        alert('CSRF token not found or invalid. Please refresh the page and try again.');
        return;
    }
    
    fetch(`/activity/silence/${ruleId}/delete/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => {
        if (!response.ok) {
            // Handle non-200 responses
            if (response.status === 403) {
                throw new Error('CSRF verification failed. Please refresh the page and try again.');
            }
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Reload rules list
            loadSilenceRules();
            // Reload activity page to show filtered results
            location.reload();
        } else {
            alert('Error deleting rule: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting rule: ' + error.message);
    });
}

function toggleSilenceRule(ruleId) {
    const csrftoken = getCsrfToken();
    if (!csrftoken || csrftoken.length < 32) {
        console.error('Invalid CSRF token:', csrftoken ? `length=${csrftoken.length}` : 'not found');
        alert('CSRF token not found or invalid. Please refresh the page and try again.');
        return;
    }
    
    // Find the rule in the current list
    const rule = silenceRules.find(r => r.id === ruleId);
    if (!rule) {
        console.error('Rule not found:', ruleId);
        return;
    }
    
    const oldState = rule.is_active;
    const newState = !oldState;
    
    // Optimistically update the UI
    rule.is_active = newState;
    renderSilenceRulesList();
    
    fetch(`/activity/silence/${ruleId}/toggle/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => {
        if (!response.ok) {
            // Revert optimistic update on error
            rule.is_active = oldState;
            renderSilenceRulesList();
            if (response.status === 403) {
                throw new Error('CSRF verification failed. Please refresh the page and try again.');
            }
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update the rule with the server's response
            rule.is_active = data.is_active;
            renderSilenceRulesList();
            // Note: Activity view will reflect changes on next manual refresh or when sidebar is reopened
        } else {
            // Revert optimistic update on error
            rule.is_active = oldState;
            renderSilenceRulesList();
            alert('Error toggling rule: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Revert optimistic update on error
        rule.is_active = oldState;
        renderSilenceRulesList();
        alert('Error toggling rule: ' + error.message);
    });
}

function showFormErrors(errors) {
    const errorContainer = document.getElementById('silence-rule-form-errors');
    const errorList = document.getElementById('silence-rule-error-list');
    
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

function hideFormErrors() {
    document.getElementById('silence-rule-form-errors').classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getCsrfToken() {
    // Try multiple methods to get CSRF token
    // 1. From form's hidden input (most reliable)
    let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    // 2. From cookie if not found in form
    if (!csrftoken) {
        const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
        if (cookieMatch) {
            csrftoken = cookieMatch[1];
        }
    }
    
    // 3. Try to find it in any form on the page
    if (!csrftoken) {
        const form = document.querySelector('form');
        if (form) {
            const tokenInput = form.querySelector('[name=csrfmiddlewaretoken]');
            if (tokenInput) {
                csrftoken = tokenInput.value;
            }
        }
    }
    
    if (!csrftoken) {
        console.error('CSRF token not found. Available cookies:', document.cookie);
        return '';
    }
    
    return csrftoken;
}

