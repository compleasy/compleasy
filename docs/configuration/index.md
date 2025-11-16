# Configuration

This section covers all configuration options for TrikuSec.

## Configuration Areas

- **[Environment Variables](environment-variables.md)** - All available environment variables
- **[Security Settings](security.md)** - Security hardening and best practices
- **[Advanced Configuration](advanced.md)** - Advanced settings and customization

## Quick Reference

### Essential Variables

```bash
# Required
SECRET_KEY=your-secret-key-here

# Production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com
```

### Optional Variables

```bash
# Admin credentials
TRIKUSEC_ADMIN_USERNAME=admin
TRIKUSEC_ADMIN_PASSWORD=secure-password

# Database (optional, defaults to SQLite)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# HTTPS Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

## Configuration Files

TrikuSec uses environment variables for configuration. These can be set via:

1. `.env` file (recommended for local development)
2. Docker Compose environment variables
3. System environment variables

## Next Steps

- Review [Environment Variables](environment-variables.md) for complete list
- Configure [Security Settings](security.md) for production
- Check [Advanced Configuration](advanced.md) for customization options

