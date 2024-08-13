function toggleRuleEditPanel(ruleId) {
    const panel = document.getElementById('rule-edit-panel');
    panel.classList.toggle('hidden');

    // If the panel is hidden, do nothing
    if (panel.classList.contains('hidden')) {
        return;
    }

    // Update the form action dynamically
    const form = document.getElementById('rule-edit-form');

    if (ruleId) {
        console.log('Editing rule:', ruleId);
        form.action = `/rule/${ruleId}/edit/`;
        loadRuleDetails(ruleId);
    } else {
        console.log('Creating a new rule');
        form.action = '/rule/create/';
        loadRuleDetails();
    }
}
function loadRuleDetails(ruleId) {
    // Empty data if ruleId is not provided (i.e. when creating a new rule)
    if (!ruleId) {
        document.getElementById('rule_enabled').checked = false;
        document.getElementById('rule_enabled_message').textContent = 'DISABLED';
        document.getElementById('rule_name').value = '';
        document.getElementById('rule_description').value = '';
        document.getElementById('rule_query').value = '';

        return;
    }

    // Convert ruleId to a number
    ruleId = Number(ruleId);

    // Get rule details by ID
    const rule = rules.find(rule => rule.id === ruleId);
    console.log('Rule details:', rule);

    // Populate the form fields with the rule details
    document.getElementById('rule_enabled').checked = rule.enabled;
    document.getElementById('rule_enabled_message').textContent = rule.enabled ? 'ENABLED' : 'DISABLED';
    document.getElementById('rule_name').value = rule.name;
    document.getElementById('rule_description').value = rule.description;
    document.getElementById('rule_query').value = rule.rule_query;
}
function toggleRuleStatus() {
    const checkbox = document.getElementById('rule_enabled');
    const message = document.getElementById('rule_enabled_message');
    message.textContent = checkbox.checked ? 'ENABLED' : 'DISABLED';
}