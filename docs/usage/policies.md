# Policy Management

Learn how to create and manage compliance policies in Compleasy.

## Overview

Policies in Compleasy allow you to:

- Define security and operational requirements
- Apply rules to devices
- Track compliance against policies
- Get recommendations for improvement

## Policy Components

### Policy Rules

Individual rules that define specific requirements:

- **Test ID** - Lynis test identifier
- **Operator** - Comparison operator (equals, greater than, etc.)
- **Value** - Expected or threshold value
- **Severity** - Warning or error level

### Policy Rule Sets

Collections of rules that can be applied to devices:

- **Name** - Descriptive name for the rule set
- **Description** - Purpose and scope
- **Rules** - List of policy rules

## Creating Policies

### 1. Create a Policy Rule

1. Navigate to **Policies** → **Rules**
2. Click **Create New Rule**
3. Configure:
   - Test ID (e.g., `FILE-7524`)
   - Operator (equals, not equals, greater than, etc.)
   - Expected value
   - Severity level
4. Save the rule

### 2. Create a Policy Rule Set

1. Navigate to **Policies** → **Rule Sets**
2. Click **Create New Rule Set**
3. Enter name and description
4. Select rules to include
5. Save the rule set

### 3. Apply to Devices

1. Navigate to **Devices**
2. Select a device
3. Go to **Policy Rulesets**
4. Assign rule sets to the device

## Common Policy Examples

### File Permissions

Ensure critical files have correct permissions:

- Test ID: `FILE-7524`
- Operator: equals
- Value: `640`
- Severity: Warning

### SSH Configuration

Require SSH key authentication:

- Test ID: `SSH-7408`
- Operator: equals
- Value: `yes`
- Severity: Error

### System Updates

Ensure system is up to date:

- Test ID: `PKGS-7390`
- Operator: less than
- Value: `7` (days since last update)
- Severity: Warning

## Compliance Tracking

### Viewing Compliance

1. Navigate to a device
2. Click **Compliance**
3. See compliance status for each rule
4. Review failed rules and recommendations

### Compliance Reports

- Overall compliance percentage
- Per-rule compliance status
- Historical compliance trends
- Recommendations for improvement

## Best Practices

- **Start Simple** - Begin with a few critical rules
- **Test First** - Test policies on non-production devices
- **Document** - Document why each rule is important
- **Review Regularly** - Review and update policies regularly
- **Organize** - Group related rules into rule sets

## Next Steps

- [Reports](reports.md) - Understand audit reports
- [API Reference](../api/index.md) - Manage policies via API

