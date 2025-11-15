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

Individual rules that define specific requirements using query expressions:

- **Name** - Descriptive name for the rule
- **Rule Query** - Query expression that evaluates against Lynis report data
- **Description** - Purpose and explanation of the rule
- **Enabled** - Whether the rule is active
- **Alert** - Whether to generate alerts when rule fails

### Policy Rule Sets

Collections of rules that can be applied to devices:

- **Name** - Descriptive name for the rule set
- **Description** - Purpose and scope
- **Rules** - List of policy rules

## Rule Query Syntax
Rule queries use [JMESPath](https://jmespath.org/) expressions to evaluate device reports. JMESPath is a query language for JSON that provides powerful and safe expression evaluation.

### Basic Syntax

**Field Access**: Access fields from the Lynis report using their names

- Examples: `os`, `hardening_index`, `firewall_active`, `vulnerable_packages_found`
- Field names are case-sensitive

**Comparison Operators**:

- `==` - Equals
- `!=` - Not equals
- `>` - Greater than
- `>=` - Greater than or equal
- `<` - Less than
- `<=` - Less than or equal

**Literals**:

- **Strings**: Use single quotes, e.g., `'Linux'`, `'Ubuntu'`
- **Numbers**: Use backticks for numeric literals, e.g., `` `70` ``, `` `0` ``, `` `1` ``

**Functions**:

- `contains(field, 'value')` - Check if string or list contains value

**Boolean Logic** (NEW!):

- `&&` - AND operator
- `||` - OR operator
- `!` - NOT operator

### Query Examples

**String equality:**
```
os == 'Linux'
os_name == 'Ubuntu'
hostname == 'web-server-01'
```

**Numeric comparisons:**
```
hardening_index > `70`
hardening_index >= `60`
hardening_index < `80`
vulnerable_packages_found == `0`
```

**Contains function (for strings or lists):**
```
contains(automation_tool_running, 'ansible')
contains(vulnerable_package, 'libc6')
```

**Not equals:**
```
os != 'Windows'
firewall_active != `0`
```

**Complex boolean expressions:**
```
os == 'Linux' && hardening_index > `70`
hardening_index < `50` || vulnerable_packages_found > `0`
!(firewall_active == `1`)
os == 'Linux' && (hardening_index > `70` || vulnerable_packages_found == `0`)
```

!!! tip "JMESPath Documentation"
    For advanced query syntax and more examples, see the [JMESPath Tutorial](https://jmespath.org/tutorial.html) and [JMESPath Examples](https://jmespath.org/examples.html).

### Available Report Fields

Common fields available in Lynis reports include:

**System Information:**

- `os` - Operating system (e.g., "Linux")
- `os_name` - OS distribution name (e.g., "Ubuntu")
- `os_version` - OS version (e.g., "22.04")
- `hostname` - System hostname
- `lynis_version` - Lynis version used

**Security Metrics:**

- `hardening_index` - Overall hardening score (0-100)
- `vulnerable_packages_found` - Number of vulnerable packages (0 or 1)
- `firewall_active` - Firewall status (0 or 1)
- `firewall_installed` - Firewall installed (0 or 1)
- `ssh_daemon_running` - SSH daemon status (0 or 1)
- `openssh_daemon_running` - OpenSSH daemon status (0 or 1)

**Package Management:**

- `installed_packages` - Number of installed packages
- `vulnerable_package` - List of vulnerable packages (use `contains()` function)

**Network:**

- `ipv6_mode` - IPv6 mode (e.g., "auto")
- `dhcp_client_running` - DHCP client status (0 or 1)

**Services:**

- `automation_tool_running` - Automation tool name (if any)
- `ntp_daemon_running` - NTP daemon status (0 or 1)
- `linux_auditd_running` - Audit daemon status (0 or 1)

!!! tip "Finding Available Fields"
    To see all available fields for a device and discover new fields for rule queries:
    
    1. Navigate to **Devices** → Select a device
    2. View the **Device Detail** page
    3. Access the **full report** which shows all available fields from the Lynis audit
    
    The full report displays all key-value pairs from the device's latest audit, making it easy to identify field names and their values for creating specific rule queries. Fields are extracted directly from the Lynis report data.

## Creating Policies

### 1. Create a Policy Rule

1. Navigate to **Policies** → **Rules**
2. Click **Create New Rule** (or use the edit panel)
3. Configure:
   - **Name**: Descriptive name (e.g., "Linux OS Check")
   - **Rule Query**: JMESPath query expression (e.g., `os == 'Linux'`)
   - **Description**: Explanation of what the rule checks
   - **Enabled**: Check to activate the rule
   - **Alert**: Check to generate alerts on failure
4. Save the rule

### 2. Create a Policy Rule Set

1. Navigate to **Policies** → **Rule Sets**
2. Click **Create New Rule Set**
3. Enter name and description
4. Select rules to include from the list
5. Save the rule set

### 3. Apply to Devices

1. Navigate to **Devices**
2. Select a device
3. Go to **Policy Rulesets** tab
4. Assign rule sets to the device

## Common Policy Examples

### Operating System Check

Ensure device is running Linux:

**Query:**
```
os == 'Linux'
```

**Description:** Verifies that the operating system is Linux.

### Hardening Index Threshold

Require minimum hardening score:

**Query:**
```
hardening_index >= `70`
```

**Description:** Ensures the system has a hardening index of at least 70.

### No Vulnerable Packages

Ensure no vulnerable packages are found:

**Query:**
```
vulnerable_packages_found == `0`
```

**Description:** Checks that no vulnerable packages were detected in the system.

### Firewall Active

Require firewall to be active:

**Query:**
```
firewall_active == `1`
```

**Description:** Verifies that the firewall is active and running.

### Specific OS Distribution

Require Ubuntu 22.04:

**Query:**
```
os_name == 'Ubuntu' && os_version == '22.04'
```

**Description:** Ensures the system is running Ubuntu 22.04 LTS. This example shows how to combine multiple conditions using the `&&` (AND) operator.

### Automation Tool Check

Check if Ansible is running:

**Query:**
```
contains(automation_tool_running, 'ansible')
```

**Description:** Verifies that Ansible automation tool is present.

### SSH Service Running

Require SSH daemon to be running:

**Query:**
```
openssh_daemon_running == `1`
```

**Description:** Ensures OpenSSH daemon is active for remote access.

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

