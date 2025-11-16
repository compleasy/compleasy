# Backup & Recovery

This guide covers backup and recovery strategies for TrikuSec deployments using both SQLite and PostgreSQL databases.

## Overview

Regular backups are essential for protecting your audit data and ensuring business continuity. This guide provides:

- Manual backup procedures for SQLite and PostgreSQL
- Recovery procedures for both database types

## SQLite Backup (Development/Small Deployments)

SQLite is the default database for TrikuSec and is suitable for small deployments or development environments.

### Manual Backup

#### Create Backup Directory

```bash
mkdir -p backups
```

#### Backup Database (While Application is Running)

SQLite's `.backup` command creates a consistent backup even while the application is running:

```bash
# Backup database (while application is running)
docker compose exec trikusec sqlite3 /app/trikusec.sqlite3 ".backup '/app/backups/trikusec-backup-$(date +%Y%m%d-%H%M%S).sqlite3'"

# Copy backup to host
docker compose cp trikusec:/app/backups/. ./backups/
```

#### Verify Backup

```bash
# Check backup file exists and has reasonable size
ls -lh backups/trikusec-backup-*.sqlite3
```

### Restore from SQLite Backup

#### Stop Application

```bash
docker compose down
```

#### Copy Backup File

```bash
# Copy backup file to source directory
cp backups/trikusec-backup-20241113-020000.sqlite3 src/trikusec.sqlite3
```

#### Start Application

```bash
docker compose up -d
```

#### Verify Restoration

```bash
# Check application is running
docker compose ps

# Verify data in admin interface
# Navigate to http://localhost:8000/admin/
```

## PostgreSQL Backup (Production)

PostgreSQL is recommended for production deployments due to better performance and concurrency handling.

### Manual Backup

#### Backup Database

```bash
# Backup database using pg_dump
docker compose exec postgres pg_dump -U trikusec_user -d trikusec > backup-$(date +%Y%m%d-%H%M%S).sql

# Or backup directly from host (if PostgreSQL is accessible)
pg_dump -h localhost -U trikusec_user -d trikusec > backup-$(date +%Y%m%d-%H%M%S).sql
```

#### Backup with Compression

For large databases, use compression to reduce backup size:

```bash
docker compose exec postgres pg_dump -U trikusec_user -d trikusec | gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz
```

#### Backup Only Schema

To backup only the database structure (without data):

```bash
docker compose exec postgres pg_dump -U trikusec_user -d trikusec --schema-only > schema-backup-$(date +%Y%m%d-%H%M%S).sql
```

#### Backup Only Data

To backup only the data (without schema):

```bash
docker compose exec postgres pg_dump -U trikusec_user -d trikusec --data-only > data-backup-$(date +%Y%m%d-%H%M%S).sql
```

### Restore from PostgreSQL Backup

#### Stop Application

```bash
docker compose down
```

#### Connect to Database Container

```bash
docker compose exec postgres psql -U trikusec_user
```

#### Drop and Recreate Database

```sql
-- Drop existing database
DROP DATABASE trikusec;

-- Create new database
CREATE DATABASE trikusec;

-- Exit psql
\q
```

#### Restore from Backup

```bash
# Restore from uncompressed backup
docker compose exec -T postgres psql -U trikusec_user trikusec < backup-20241113-020000.sql

# Restore from compressed backup
gunzip < backup-20241113-020000.sql.gz | docker compose exec -T postgres psql -U trikusec_user trikusec
```

#### Start Application

```bash
docker compose up -d
```

#### Verify Restoration

```bash
# Check application is running
docker compose ps

# Verify data in admin interface
# Navigate to http://localhost:8000/admin/
```

## Backup Best Practices

### Frequency

- **Development**: Weekly backups or before major changes
- **Production**: Daily backups at minimum
- **High-traffic production**: Multiple backups per day

### Retention

- **Development**: 7-14 days
- **Production**: 30-90 days
- **Compliance requirements**: Follow your organization's data retention policies

### Storage

- Store backups in a separate location from the production database
- Use off-site storage for critical production backups
- Encrypt backups containing sensitive data
- Test restore procedures regularly

### Verification

- Regularly verify backup file integrity
- Test restore procedures in a non-production environment
- Document your backup and recovery procedures
- Keep backup logs for audit purposes

## Troubleshooting

### SQLite Backup Issues

**Problem**: Permission denied when creating backup

```bash
# Solution: Ensure backup directory exists in container
docker compose exec trikusec mkdir -p /app/backups
```

**Problem**: Backup file is empty or corrupted

```bash
# Solution: Verify database file exists and is accessible
docker compose exec trikusec ls -lh /app/trikusec.sqlite3
```

### PostgreSQL Backup Issues

**Problem**: Authentication failed

```bash
# Solution: Verify database credentials
docker compose exec postgres psql -U trikusec_user -d trikusec -c "SELECT 1;"
```

**Problem**: Backup file is too large

```bash
# Solution: Use compression
docker compose exec postgres pg_dump -U trikusec_user -d trikusec | gzip > backup.sql.gz
```

## Related Documentation

- [Docker Installation](docker.md) - Setting up TrikuSec with Docker
- [PostgreSQL Setup](postgresql.md) - Configuring PostgreSQL for production
- [Configuration](../configuration/index.md) - Environment variables and settings

