# TrikuSec Documentation

Welcome to the TrikuSec documentation!

**TrikuSec** is a centralized Linux server auditing and compliance management platform built on [Lynis](https://cisofy.com/lynis/). It collects, stores, and analyzes security audit reports from multiple Linux servers in one place, enabling centralized monitoring and policy compliance management across your infrastructure.

## Use Cases

TrikuSec is ideal for:

- **Security Compliance Monitoring**: Ensure servers meet security policies and regulatory requirements
- **Infrastructure Auditing**: Track security posture across multiple servers from a single dashboard
- **Change Tracking**: Monitor changes between audit runs to identify security drift
- **Policy Enforcement**: Automatically evaluate compliance against organizational policies
- **Centralized Reporting**: Single point of visibility for all server audits across your infrastructure

## Security Philosophy

TrikuSec is designed with security as the top priority. We believe that security monitoring tools should never compromise the security of the systems they monitor.

**Key Principles:**

- **Read-Only:** TrikuSec only receives data—no commands are sent or run on your servers.
- **No Agents:** Only [Lynis](https://cisofy.com/lynis/) is needed on servers; no extra daemons or proprietary software.
- **Server Independence:** TrikuSec does not control or alter your systems.

This approach improves monitoring without added risk.

## Features

### Core Capabilities

- **Centralized Audit Collection**: Receives audit reports from multiple Linux servers via Lynis clients, storing full reports and generating diff reports to track changes over time
- **Device Management**: Tracks all monitored servers with metadata including hostname, OS, distribution, version, and compliance status
- **Policy & Compliance Management**: Define custom compliance rules using a query language and automatically evaluate devices against assigned policies
- **Report Analysis**: View complete audit reports, track changes between audits, and analyze historical compliance trends
- **Web Dashboard**: User-friendly interface for viewing devices, compliance status, policies, and reports
- **API Integration**: Lynis-compatible API endpoints for seamless integration with existing Lynis installations

## Quick Start

1. **[Install TrikuSec](installation/index.md)** - Get started with Docker installation
2. **[Configure Client](installation/client-setup.md)** - Set up Lynis clients to send reports
3. **[Start Using](usage/getting-started.md)** - Learn how to use the dashboard and manage your servers

## Documentation Structure

- **[Installation](installation/index.md)** - Installation guides for server and clients
- **[Configuration](configuration/index.md)** - Environment variables, security settings, and advanced configuration
- **[Usage](usage/index.md)** - User guides for dashboard, policies, and reports
- **[API Reference](api/index.md)** - API endpoints and integration guides
- **[Development](development/index.md)** - Contributing, testing, and development setup
- **[License](license.md)** - License information (GPL-3.0)

## Status

!!! warning "Development Status"
    This project is still in development and should **NOT** be used in production.

## Acknowledgments

TrikuSec is built on [Lynis](https://cisofy.com/lynis/), an excellent open-source security auditing tool. We are grateful to the Lynis project and its community for providing such a robust foundation.

### Important Note

**TrikuSec is not a professional product.** This is an open-source project in active development. If you are looking for a robust, production-ready security solution with professional support, service level agreements, and enterprise features, we recommend considering [Lynis Enterprise](https://cisofy.com/pricing/) by CISOfy.

!!! note "No Affiliation"
    We have no relationship, affiliation, or partnership with CISOfy. This recommendation is made solely to help users find appropriate solutions for their needs.

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/trikusec/trikusec/issues)
- **Repository:** [GitHub Repository](https://github.com/trikusec/trikusec)

