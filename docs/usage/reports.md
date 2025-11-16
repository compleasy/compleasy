# Report Analysis

Learn how to view and analyze audit reports in Compleasy.

## Viewing Reports

### Device Reports

1. Navigate to **Devices**
2. Click on a device
3. View the latest report and compliance status

### Report Details

Each report includes:

- **Audit Date** - When the audit was performed
- **Compliance Status** - Overall compliance percentage
- **Warnings** - Security warnings found
- **Suggestions** - Recommendations for improvement
- **Test Results** - Individual test results

## Report Components

### Compliance Status

Overall compliance percentage based on:
- Applied policy rules
- Test results
- Severity levels

### Warnings

Security warnings that need attention:
- **High Priority** - Critical security issues
- **Medium Priority** - Important recommendations
- **Low Priority** - Best practice suggestions

### Suggestions

Actionable recommendations:
- Configuration changes
- Package installations
- System hardening steps

## Analyzing Reports

### Compare Reports

Compare reports over time to:
- Track compliance trends
- Identify regressions
- Measure improvement

### Filter and Search

- Filter by test category
- Search for specific tests
- Focus on failed tests

### Export Reports

Compleasy supports exporting device reports to PDF format for documentation, compliance audits, and sharing with teams.

**To export a device report to PDF:**

1. Navigate to **Devices**
2. Click on the device you want to export
3. Click the **Actions** dropdown menu (top-right corner of the Overview section)
4. Select **Export to PDF**

The PDF report includes:
- Device overview (hostname, IP address, OS, enrollment details)
- Audit information (Lynis version, hardening index, test results)
- Compliance status with detailed ruleset evaluations
- Security feedback (warnings and suggestions)

The PDF file is automatically named with the device hostname and timestamp (e.g., `device-hostname-20251116_073000.pdf`).

## Understanding Test Results

### Test Categories

Lynis organizes tests into categories:

- **Authentication** - Login and access controls
- **Boot Services** - System startup services
- **File Systems** - File permissions and security
- **Firewall** - Network security
- **Kernel** - System kernel settings
- **Networking** - Network configuration
- **Processes** - Running processes
- **Storage** - Disk and storage security

### Test Severity

- **Error** - Critical issues requiring immediate attention
- **Warning** - Important recommendations
- **Suggestion** - Best practice improvements

## Best Practices

- **Review Regularly** - Check reports after each audit
- **Address Warnings** - Prioritize high-severity warnings
- **Track Trends** - Monitor compliance over time
- **Document Actions** - Document remediation steps
- **Share Findings** - Share reports with relevant teams

## Next Steps

- [Policies](policies.md) - Create policies to track compliance
- [API Reference](../api/index.md) - Access reports programmatically

