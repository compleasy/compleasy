# Installation

This section covers installing and setting up TrikuSec.

## Overview

TrikuSec consists of two main components:

1. **TrikuSec Server** - The central server that receives and manages audit reports
2. **Lynis Client** - The auditing tool installed on each server you want to monitor

!!! tip "Security-First Design"
    TrikuSec uses a **read-only architecture** - it only receives data from your servers and never pushes changes or executes commands. The only requirement on monitored servers is [Lynis](https://cisofy.com/lynis/), a well-established open-source tool available in standard Linux repositories.

## Installation Options

- **[Docker Installation](docker.md)** - Recommended for most users (quick setup)
- **[PostgreSQL Setup](postgresql.md)** - Database configuration for production
- **[Client Setup](client-setup.md)** - Configuring Lynis clients to send reports
- **[Backup & Recovery](backup-recovery.md)** - Backup strategies and recovery procedures

## Prerequisites

Before installing TrikuSec, ensure you have:

- Docker and Docker Compose installed
- A secure `SECRET_KEY` generated for Django
- (Optional) PostgreSQL for production deployments

## Next Steps

After installation, proceed to:

- [Configuration](../configuration/index.md) - Configure environment variables and security settings
- [Getting Started](../usage/getting-started.md) - Learn how to use TrikuSec

