"""
E2E test fixtures for Playwright-based frontend tests.
"""
import pytest
from api.models import PolicyRule, PolicyRuleset, Device, Organization


@pytest.fixture
def live_server_url(live_server):
    """Return the live server URL."""
    return live_server.url


@pytest.fixture
def authenticated_browser(request, live_server_url, test_user):
    """
    Create an authenticated browser session.
    
    Logs in the test user and returns the page object.
    Note: pytest-playwright uses synchronous Playwright API by default.
    """
    # Try to get the page fixture (only available when pytest-playwright is installed)
    try:
        page = request.getfixturevalue('page')
    except pytest.FixtureLookupError:
        pytest.skip("Playwright not available - skipping E2E test")
    
    # Set a known password for the test user (Django ORM is synchronous)
    test_user.set_password('testpassword123')
    test_user.save()
    
    # Navigate to login page (sync API)
    page.goto(f"{live_server_url}/login/")
    
    # Fill in login form
    page.fill('input[name="username"]', test_user.username)
    page.fill('input[name="password"]', 'testpassword123')
    
    # Submit form
    page.click('button[type="submit"]')
    
    # Wait for redirect (login successful)
    page.wait_for_url(f"{live_server_url}/**", timeout=5000)
    
    return page


@pytest.fixture
def test_policy_data(db, test_user):
    """
    Create sample policy data: rulesets and rules.
    
    Returns a dict with:
    - rules: list of PolicyRule objects
    - rulesets: list of PolicyRuleset objects
    """
    # Create default organization if needed
    default_org, _ = Organization.objects.get_or_create(
        slug='default',
        defaults={'name': 'Default Organization', 'is_active': True}
    )
    
    # Create sample rules
    rules = []
    for i in range(5):
        rule = PolicyRule.objects.create(
            name=f"Test Rule {i+1}",
            description=f"Description for test rule {i+1}",
            rule_query=f"test_query_{i+1}",
            enabled=True
        )
        rules.append(rule)
    
    # Create sample rulesets
    rulesets = []
    
    # Ruleset 1: Empty ruleset
    ruleset1 = PolicyRuleset.objects.create(
        name="Empty Ruleset",
        description="A ruleset with no rules"
    )
    rulesets.append(ruleset1)
    
    # Ruleset 2: Ruleset with some rules
    ruleset2 = PolicyRuleset.objects.create(
        name="Ruleset with Rules",
        description="A ruleset with multiple rules"
    )
    ruleset2.rules.add(rules[0], rules[1], rules[2])
    rulesets.append(ruleset2)
    
    # Ruleset 3: Another ruleset with different rules
    ruleset3 = PolicyRuleset.objects.create(
        name="Another Ruleset",
        description="Another ruleset with different rules"
    )
    ruleset3.rules.add(rules[2], rules[3], rules[4])
    rulesets.append(ruleset3)
    
    return {
        'rules': rules,
        'rulesets': rulesets
    }


@pytest.fixture
def test_device_with_rulesets(db, test_device, test_policy_data):
    """
    Create a test device with some rulesets assigned.
    """
    # Assign first two rulesets to the device
    test_device.rulesets.add(
        test_policy_data['rulesets'][0],
        test_policy_data['rulesets'][1]
    )
    return test_device


def wait_for_sidebar_animation(page, timeout=500):
    """
    Wait for sidebar animation to complete.
    
    Sidebars use CSS transitions, so we need to wait a bit
    for animations to finish before interacting.
    """
    page.wait_for_timeout(timeout)

