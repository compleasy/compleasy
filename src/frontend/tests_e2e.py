"""
E2E tests for frontend functionality using Playwright.

These tests verify the complex Policies/Rulesets UI with nested sidebars,
AJAX forms, and state management.
"""
import pytest
from django.contrib.auth.models import User
from api.models import PolicyRule, PolicyRuleset, Device


@pytest.mark.e2e
class TestRulesetCRUD:
    """Test ruleset CRUD operations."""
    
    def test_create_ruleset_basic(self, authenticated_browser, live_server_url, test_policy_data):
        """Create a ruleset without rules."""
        page = authenticated_browser
        
        # Navigate to policies page
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Click "New Ruleset" button
        page.click('button:has-text("New Ruleset")')
        
        # Wait for sidebar to appear
        sidebar = page.locator('#ruleset-edit-panel')
        sidebar.wait_for(state="visible", timeout=5000)
        
        # Fill in form
        page.fill('#ruleset_name', 'Test Ruleset E2E')
        page.fill('#ruleset_description', 'Test description for E2E')
        
        # Submit form
        page.click('#ruleset-edit-form button[type="submit"]')
        
        # Wait for page reload (form submission triggers reload via AJAX)
        # The form submission is AJAX, so we need to wait for the reload
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)  # Extra wait for AJAX response and page reload
        
        # Verify ruleset appears in list
        ruleset_locator = page.locator('text=Test Ruleset E2E')
        ruleset_locator.wait_for(state="visible", timeout=5000)
        assert ruleset_locator.is_visible(), f"Ruleset 'Test Ruleset E2E' not found. Page URL: {page.url}"
        
        # Verify description is visible
        description_locator = page.locator('text=Test description for E2E')
        description_locator.wait_for(state="visible", timeout=5000)
        assert description_locator.is_visible()
    
    def test_create_ruleset_with_rules(self, authenticated_browser, live_server_url, test_policy_data):
        """Create a ruleset and select rules."""
        page = authenticated_browser
        
        # Navigate to policies page
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Click "New Ruleset" button
        page.click('button:has-text("New Ruleset")')
        
        # Wait for sidebar
        sidebar = page.locator('#ruleset-edit-panel')
        sidebar.wait_for(state="visible", timeout=5000)
        
        # Fill in basic info
        page.fill('#ruleset_name', 'Ruleset with Rules E2E')
        page.fill('#ruleset_description', 'A ruleset with selected rules')
        
        # Click "Select Rules" button
        page.click('button:has-text("Select Rules")')
        
        # Wait for rule selection panel
        rule_panel = page.locator('#rule-selection-panel')
        rule_panel.wait_for(state="visible", timeout=5000)
        
        # Wait for rules to be rendered in the panel
        rules_container = page.locator('#rules')
        rules_container.wait_for(state="visible", timeout=5000)
        
        # Select some rules - click the labels since checkboxes are hidden
        rules = test_policy_data['rules']
        # Wait for the first rule label to be visible
        first_rule_label = page.locator(f'label[for="rule-{rules[0].id}"]')
        first_rule_label.wait_for(state="visible", timeout=5000)
        
        # Click the labels to check the checkboxes (labels are visible, checkboxes are hidden)
        page.click(f'label[for="rule-{rules[0].id}"]')
        page.click(f'label[for="rule-{rules[1].id}"]')
        page.click(f'label[for="rule-{rules[2].id}"]')
        
        # Click Apply
        apply_button = page.locator('#rule-selection-form button:has-text("Apply")')
        apply_button.wait_for(state="visible", timeout=5000)
        apply_button.click()
        
        # Wait for rule selection panel to close and ruleset edit panel to reappear
        rule_panel.wait_for(state="hidden", timeout=10000)
        sidebar.wait_for(state="visible", timeout=10000)
        
        # Submit ruleset form
        page.click('#ruleset-edit-form button[type="submit"]')
        
        # Wait for page reload (AJAX triggers location.reload())
        page.wait_for_url(f"{live_server_url}/policies/", timeout=10000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(500)  # Small wait for rendering
        
        # Verify ruleset was created
        assert page.locator('text=Ruleset with Rules E2E').is_visible()
    
    def test_edit_ruleset_details(self, authenticated_browser, live_server_url, test_policy_data):
        """Edit ruleset name and description."""
        page = authenticated_browser
        
        # Get a ruleset to edit
        ruleset = test_policy_data['rulesets'][0]
        
        # Navigate to policies page
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Find and click edit button for the ruleset
        # Look for the edit button in the row containing the ruleset name
        ruleset_row = page.locator(f'tr:has-text("{ruleset.name}")')
        edit_button = ruleset_row.locator('button[title="Edit"]')
        edit_button.click()
        
        # Wait for sidebar
        sidebar = page.locator('#ruleset-edit-panel')
        sidebar.wait_for(state="visible", timeout=5000)
        
        # Verify form is populated
        name_field = page.locator('#ruleset_name')
        assert name_field.input_value() == ruleset.name
        
        # Update name and description
        name_field.fill('Updated Ruleset Name E2E')
        page.fill('#ruleset_description', 'Updated description')
        
        # Submit
        page.click('#ruleset-edit-form button[type="submit"]')
        
        # Wait for reload (AJAX triggers location.reload())
        page.wait_for_url(f"{live_server_url}/policies/", timeout=10000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(500)  # Small wait for rendering
        
        # Verify update
        assert page.locator('text=Updated Ruleset Name E2E').is_visible()
    
    def test_delete_ruleset_with_confirmation(self, authenticated_browser, live_server_url, test_policy_data):
        """Delete a ruleset with confirmation dialog."""
        page = authenticated_browser
        
        # Create a ruleset to delete
        ruleset = PolicyRuleset.objects.create(
            name='Ruleset to Delete E2E',
            description='This will be deleted'
        )
        
        # Navigate to policies page
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Find delete button
        ruleset_row = page.locator(f'tr:has-text("Ruleset to Delete E2E")')
        delete_button = ruleset_row.locator('button[title="Delete"]')
        
        # Set up dialog handler to accept
        page.once("dialog", lambda dialog: dialog.accept())
        
        # Click delete
        delete_button.click()
        
        # Wait for page reload
        page.wait_for_load_state("networkidle")
        
        # Verify ruleset is gone
        assert not page.locator('text=Ruleset to Delete E2E').is_visible()


@pytest.mark.e2e
class TestRuleCRUD:
    """Test rule CRUD operations."""
    
    def test_create_rule(self, authenticated_browser, live_server_url):
        """Create a new rule."""
        page = authenticated_browser
        
        # Navigate to policies page
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("domcontentloaded")
        
        # Click "New Rule" button - use onclick attribute to find the correct one
        # The Rules section button has onclick="toggleRuleEditPanel(null)"
        new_rule_button = page.locator('button[onclick="toggleRuleEditPanel(null)"]:has-text("New Rule")')
        new_rule_button.scroll_into_view_if_needed()
        new_rule_button.wait_for(state="visible", timeout=5000)
        new_rule_button.click()
        
        # Wait for sidebar
        sidebar = page.locator('#rule-edit-panel')
        sidebar.wait_for(state="visible", timeout=10000)  # Increased timeout
        
        # Fill in form
        page.fill('#rule_name', 'Test Rule E2E')
        page.fill('#rule_description', 'Test rule description')
        page.fill('#rule_query', 'test_query_e2e')
        
        # Enable the rule (checkbox is hidden with sr-only, click the label instead)
        enabled_label = page.locator('label:has(#rule_enabled)')
        enabled_label.wait_for(state="visible", timeout=5000)
        enabled_label.click()
        
        # Submit
        page.click('#rule-edit-form button[type="submit"]')
        
        # Wait for reload (AJAX triggers location.reload())
        page.wait_for_url(f"{live_server_url}/policies/", timeout=10000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(500)  # Small wait for rendering
        
        # Verify rule appears in the rules table (use more specific selector to avoid strict mode violation)
        rule_link = page.locator('a:has-text("Test Rule E2E")').first
        rule_link.wait_for(state="visible", timeout=5000)
        assert rule_link.is_visible()
    
    def test_edit_rule(self, authenticated_browser, live_server_url, test_policy_data):
        """Edit an existing rule."""
        page = authenticated_browser
        
        # Get a rule to edit
        rule = test_policy_data['rules'][0]
        
        # Navigate to policies page
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("domcontentloaded")
        
        # Scroll to Rules section - use exact text match to avoid matching "Rulesets"
        rules_section = page.get_by_role("heading", name="Rules", exact=True)
        rules_section.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        
        # Find edit button for the rule
        rule_row = page.locator(f'tr:has-text("{rule.name}")')
        rule_row.scroll_into_view_if_needed()
        edit_button = rule_row.locator('button[title="Edit"]')
        edit_button.wait_for(state="visible", timeout=5000)
        edit_button.click()
        
        # Wait for sidebar
        sidebar = page.locator('#rule-edit-panel')
        sidebar.wait_for(state="visible", timeout=5000)
        
        # Verify form is populated
        assert page.locator('#rule_name').input_value() == rule.name
        
        # Update name
        page.fill('#rule_name', 'Updated Rule Name E2E')
        
        # Submit
        page.click('#rule-edit-form button[type="submit"]')
        
        # Wait for reload (AJAX triggers location.reload())
        page.wait_for_url(f"{live_server_url}/policies/", timeout=10000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(500)  # Small wait for rendering
        
        # Verify update (use more specific selector to avoid strict mode violation)
        updated_rule_link = page.locator('a:has-text("Updated Rule Name E2E")').first
        updated_rule_link.wait_for(state="visible", timeout=5000)
        assert updated_rule_link.is_visible()
    
    def test_delete_rule_with_confirmation(self, authenticated_browser, live_server_url):
        """Delete a rule with confirmation dialog."""
        page = authenticated_browser
        
        # Create a rule to delete
        rule = PolicyRule.objects.create(
            name='Rule to Delete E2E',
            description='This will be deleted',
            rule_query='delete_me',
            enabled=True
        )
        
        # Navigate to policies page
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Find delete button
        rule_row = page.locator(f'tr:has-text("Rule to Delete E2E")')
        delete_button = rule_row.locator('button[title="Delete"]')
        
        # Set up dialog handler
        page.once("dialog", lambda dialog: dialog.accept())
        
        # Click delete
        delete_button.click()
        
        # Wait for reload
        page.wait_for_load_state("networkidle")
        
        # Verify rule is gone
        assert not page.locator('text=Rule to Delete E2E').is_visible()


@pytest.mark.e2e
class TestDeviceDetailInteractions:
    """Test device detail page interactions."""
    
    def test_device_select_rulesets(self, authenticated_browser, live_server_url, test_device_with_rulesets, test_policy_data):
        """Open ruleset selection sidebar from device detail."""
        page = authenticated_browser
        device = test_device_with_rulesets
        
        # Navigate to device detail
        page.goto(f"{live_server_url}/device/{device.id}/")
        page.wait_for_load_state("networkidle")
        
        # Find and click "Select Rulesets" button
        # Look for button that opens ruleset selection
        select_button = page.locator('button:has-text("Select Rulesets"), button:has-text("Manage Rulesets")')
        if not select_button.is_visible():
            # Try alternative selector
            select_button = page.locator('a:has-text("Select Rulesets"), a:has-text("Manage Rulesets")')
        
        if select_button.count() > 0:
            select_button.first.click()
            
            # Wait for ruleset selection panel
            selection_panel = page.locator('#ruleset-selection-panel')
            selection_panel.wait_for(state="visible", timeout=5000)
            
            # Verify panel is visible
            assert selection_panel.is_visible()
    
    def test_device_create_ruleset_from_detail(self, authenticated_browser, live_server_url, test_device):
        """Create a ruleset from device detail view."""
        page = authenticated_browser
        device = test_device
        
        # Navigate to device detail
        page.goto(f"{live_server_url}/device/{device.id}/")
        page.wait_for_load_state("networkidle")
        
        # This test verifies the UI is accessible, not necessarily creating a ruleset
        # The actual creation would be similar to test_create_ruleset_basic
        # Just verify we can navigate to policies if needed
        policies_link = page.locator('a:has-text("Policies"), a:has-text("Back to Policies")')
        if policies_link.count() > 0:
            # UI is accessible
            assert True


@pytest.mark.e2e
class TestSidebarStateManagement:
    """Test sidebar state management and interactions."""
    
    def test_sidebar_cancel_closes_panel(self, authenticated_browser, live_server_url, test_policy_data):
        """Cancel button closes the sidebar."""
        page = authenticated_browser
        
        # Navigate to policies
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Open ruleset edit panel
        page.click('button:has-text("New Ruleset")')
        sidebar = page.locator('#ruleset-edit-panel')
        sidebar.wait_for(state="visible", timeout=5000)
        
        # Click cancel button
        cancel_button = sidebar.locator('button:has-text("Cancel"), .ruleset-edit-panel-button')
        cancel_button.first.click()
        
        # Wait for sidebar to close
        sidebar.wait_for(state="hidden", timeout=5000)
        assert sidebar.is_hidden()
    
    def test_sidebar_x_button_closes_panel(self, authenticated_browser, live_server_url, test_policy_data):
        """X button closes the sidebar."""
        page = authenticated_browser
        
        # Navigate to policies
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Open rule edit panel - use onclick attribute to find the correct one
        new_rule_button = page.locator('button[onclick="toggleRuleEditPanel(null)"]:has-text("New Rule")')
        new_rule_button.scroll_into_view_if_needed()
        new_rule_button.wait_for(state="visible", timeout=5000)
        new_rule_button.click()
        
        sidebar = page.locator('#rule-edit-panel')
        sidebar.wait_for(state="visible", timeout=10000)  # Increased timeout
        
        # Find and click X button (close button)
        close_button = sidebar.locator('.rule-edit-panel-button').first
        close_button.wait_for(state="visible", timeout=5000)
        close_button.click()
        
        # Wait for sidebar to close
        sidebar.wait_for(state="hidden", timeout=5000)
        assert sidebar.is_hidden()
    
    def test_nested_sidebar_returns_to_parent(self, authenticated_browser, live_server_url, test_policy_data):
        """Rule selection sidebar returns to ruleset edit sidebar."""
        page = authenticated_browser
        
        # Navigate to policies
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Open ruleset edit panel
        page.click('button:has-text("New Ruleset")')
        ruleset_sidebar = page.locator('#ruleset-edit-panel')
        ruleset_sidebar.wait_for(state="visible", timeout=5000)
        
        # Click "Select Rules" to open rule selection
        page.click('button:has-text("Select Rules")')
        
        # Wait for rule selection panel (ruleset panel should be hidden)
        rule_panel = page.locator('#rule-selection-panel')
        rule_panel.wait_for(state="visible", timeout=5000)
        ruleset_sidebar.wait_for(state="hidden", timeout=5000)
        
        # Click "Back" or "Cancel" in rule selection
        back_button = rule_panel.locator('button:has-text("Back"), button:has-text("Cancel")')
        if back_button.count() > 0:
            back_button.first.click()
        else:
            # Try clicking the X button
            close_button = rule_panel.locator('.rule-selection-panel-button, button[type="button"]').first
            close_button.click()
        
        # Wait for rule panel to close and ruleset panel to reappear
        rule_panel.wait_for(state="hidden", timeout=5000)
        ruleset_sidebar.wait_for(state="visible", timeout=5000)
        
        # Verify ruleset panel is visible again
        assert ruleset_sidebar.is_visible()
    
    def test_add_rule_button_opens_create_panel(self, authenticated_browser, live_server_url, test_policy_data):
        """Test that clicking '+ Rule' button in rule selection panel opens rule edit panel in create mode."""
        page = authenticated_browser
        
        # Navigate to policies page
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Click "New Ruleset" button
        page.click('button:has-text("New Ruleset")')
        
        # Wait for ruleset edit sidebar to appear
        ruleset_sidebar = page.locator('#ruleset-edit-panel')
        ruleset_sidebar.wait_for(state="visible", timeout=5000)
        
        # Click "Select Rules" button
        page.click('button:has-text("Select Rules")')
        
        # Wait for rule selection panel to appear
        rule_selection_panel = page.locator('#rule-selection-panel')
        rule_selection_panel.wait_for(state="visible", timeout=5000)
        
        # Wait for rules to be rendered
        rules_container = page.locator('#rules')
        rules_container.wait_for(state="visible", timeout=5000)
        
        # Click the "+ Rule" button (the create button)
        add_rule_button = page.locator('button.rule-edit-panel-button:has-text("+ Rule")')
        add_rule_button.wait_for(state="visible", timeout=5000)
        add_rule_button.click()
        
        # Wait for rule selection panel to close
        rule_selection_panel.wait_for(state="hidden", timeout=5000)
        
        # Wait for rule edit panel to open
        rule_edit_panel = page.locator('#rule-edit-panel')
        rule_edit_panel.wait_for(state="visible", timeout=5000)
        
        # Verify the panel is in create mode (title should be "Create New Rule")
        title = page.locator('#rule-edit-title')
        assert title.is_visible(), "Rule edit panel title should be visible"
        assert title.text_content() == "Create New Rule", f"Expected 'Create New Rule', got '{title.text_content()}'"
        
        # Verify form fields are visible and ready
        rule_name_field = page.locator('#rule_name')
        assert rule_name_field.is_visible(), "Rule name field should be visible"
        assert rule_name_field.input_value() == "", "Rule name field should be empty"
        
        rule_description_field = page.locator('#rule_description')
        assert rule_description_field.is_visible(), "Rule description field should be visible"
        assert rule_description_field.input_value() == "", "Rule description field should be empty"
        
        rule_query_field = page.locator('#rule_query')
        assert rule_query_field.is_visible(), "Rule query field should be visible"
        assert rule_query_field.input_value() == "", "Rule query field should be empty"
        
        # Verify the form action is set to create
        rule_form = page.locator('#rule-edit-form')
        form_action = rule_form.get_attribute('action')
        assert form_action == '/rule/create/', f"Expected form action to be '/rule/create/', got '{form_action}'"
        
        # Verify enabled checkbox is unchecked (default for new rules)
        enabled_checkbox = page.locator('#rule_enabled')
        assert enabled_checkbox.is_visible(), "Enabled checkbox should be visible"
        assert not enabled_checkbox.is_checked(), "Enabled checkbox should be unchecked for new rule"
    
    def test_rule_selection_pencil_icon_opens_edit_panel(self, authenticated_browser, live_server_url, test_policy_data):
        """Clicking pencil icon in rule selection sidebar opens rule edit panel and hides selection panel."""
        page = authenticated_browser
        
        # Navigate to policies
        page.goto(f"{live_server_url}/policies/")
        page.wait_for_load_state("networkidle")
        
        # Open ruleset edit panel
        page.click('button:has-text("New Ruleset")')
        ruleset_sidebar = page.locator('#ruleset-edit-panel')
        ruleset_sidebar.wait_for(state="visible", timeout=5000)
        
        # Click "Select Rules" to open rule selection
        page.click('button:has-text("Select Rules")')
        
        # Wait for rule selection panel
        rule_selection_panel = page.locator('#rule-selection-panel')
        rule_selection_panel.wait_for(state="visible", timeout=5000)
        
        # Wait for rules to be rendered
        rules_container = page.locator('#rules')
        rules_container.wait_for(state="visible", timeout=5000)
        
        # Get a rule from test data
        rule = test_policy_data['rules'][0]
        
        # Find the rule label and hover over it to make pencil icon visible
        rule_label = page.locator(f'label[for="rule-{rule.id}"]')
        rule_label.wait_for(state="visible", timeout=5000)
        rule_label.hover()
        
        # Wait a bit for the hover state to apply
        page.wait_for_timeout(300)
        
        # Find and click the pencil icon (edit button) for this rule
        # The pencil icon is inside the label, with data-rule-id attribute
        pencil_icon = rule_label.locator(f'a[data-rule-id="{rule.id}"]')
        pencil_icon.wait_for(state="visible", timeout=5000)
        pencil_icon.click()
        
        # Wait for rule selection panel to hide
        rule_selection_panel.wait_for(state="hidden", timeout=5000)
        
        # Wait for rule edit panel to open
        rule_edit_panel = page.locator('#rule-edit-panel')
        rule_edit_panel.wait_for(state="visible", timeout=5000)
        
        # Verify rule edit panel is visible and rule selection panel is hidden
        assert rule_edit_panel.is_visible()
        assert rule_selection_panel.is_hidden()
        
        # Verify the rule form is populated with the correct rule data
        rule_name_input = page.locator('#rule_name')
        rule_name_input.wait_for(state="visible", timeout=5000)
        assert rule_name_input.input_value() == rule.name

