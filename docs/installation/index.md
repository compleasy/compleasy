# Installation

This section covers installing and setting up Compleasy.

## Overview

Compleasy consists of two main components:

1. **Compleasy Server** - The central server that receives and manages audit reports
2. **Lynis Client** - The auditing tool installed on each server you want to monitor

## Installation Options

- **[Docker Installation](docker.md)** - Recommended for most users (quick setup)
- **[PostgreSQL Setup](postgresql.md)** - Database configuration for production
- **[Client Setup](client-setup.md)** - Configuring Lynis clients to send reports

## Prerequisites

Before installing Compleasy, ensure you have:

- Docker and Docker Compose installed
- A secure `SECRET_KEY` generated for Django
- (Optional) PostgreSQL for production deployments

## Next Steps

After installation, proceed to:

- [Configuration](../configuration/index.md) - Configure environment variables and security settings
- [Getting Started](../usage/getting-started.md) - Learn how to use Compleasy

