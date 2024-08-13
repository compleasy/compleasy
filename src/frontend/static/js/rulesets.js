let rulesets = {};
let rules = {};


document.addEventListener('DOMContentLoaded', function() {
    rulesets = JSON.parse(document.getElementById('rulesets-data').textContent);
    rules = JSON.parse(document.getElementById('rules-data').textContent);

    // Search rules selection panel buttons by class
    document.querySelectorAll('.rule-select-panel-button').forEach(button => {
        button.addEventListener('click', function() {
            const rulesetId = button.dataset.rulesetId;
            toggleRuleSelectionPanel(rulesetId);
        });
    });

    // Search rules edition panel buttons by class
    document.querySelectorAll('.rule-edit-panel-button').forEach(button => {
        button.addEventListener('click', event => {
            const ruleId = button.dataset.ruleId;
            toggleRuleEditPanel(ruleId);
        }
        );
    });

    // If rules is empty; redirect to rules list
    if (Object.keys(rules).length === 0) {
        window.location.href = "{% url 'rule_list' %}";
    }
});

function toggleRuleSelectionPanel(rulesetId) {
    const rulesetPanel = document.getElementById('rule-selection-panel');
    rulesetPanel.classList.toggle('hidden');

    // If rulesetId is not provided, do nothing more
    if (!rulesetId) {
        return;
    }

    // Store the ruleset ID in the panel's data attribute and the hidden input field
    rulesetPanel.dataset.rulesetId = rulesetId;
    document.getElementById('ruleset_id').value = rulesetId;

    if (!rulesetPanel.classList.contains('hidden')) {
        selectRulesetRules(rulesetId);
    }

    // Update the form action dynamically
    const form = document.getElementById('rule-selection-form');
    form.action = `/ruleset/${rulesetId}/edit/`;
}

function selectRulesetRules(rulesetId) {
    // Convert the ruleset ID to a number
    rulesetId = Number(rulesetId);

    // Get the ruleset by ID
    const ruleset = rulesets.find(ruleset => ruleset.id === rulesetId);
    if (!ruleset) {
        console.error(`Ruleset with ID ${rulesetId} not found.`);
        return;
    }
    const rules = ruleset.rules;
    console.log('Rules:', rules);

    // Deselect all checkboxes first
    const ruleCheckboxes = document.querySelectorAll('#rules input[type="checkbox"]');
    ruleCheckboxes.forEach(checkbox => {
        checkbox.checked = false;
    });

    // Select the ruleset rules
    rules.forEach(rule => {
        const ruleCheckbox = document.querySelector(`#rules input[type="checkbox"][value="${rule.id}"]`);
        if (ruleCheckbox) {
            ruleCheckbox.checked = true;
        }
    });
}

function searchRuleByName(name) {
    const ruleCheckboxes = document.querySelectorAll('#rules div');
    if (!name) {
        ruleCheckboxes.forEach(checkbox => checkbox.classList.remove('hidden'));
        return;
    }
    ruleCheckboxes.forEach(checkbox => {
        const ruleName = checkbox.querySelector('label').textContent;
        if (ruleName.toLowerCase().includes(name.toLowerCase())) {
            checkbox.classList.remove('hidden');
        } else {
            checkbox.classList.add('hidden');
        }
    });
}

function submitRuleSelectionForm() {
    // Submit the form
    document.getElementById('rule-selection-form').submit();
}