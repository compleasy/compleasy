# Environment Variables

Complete reference of all environment variables used by Compleasy.

## Required Variables

### SECRET_KEY

Django secret key for cryptographic signing.

```bash
SECRET_KEY=your-secret-key-here
```

!!! danger "Security Critical"
    **NEVER** commit your actual secret key to version control. Generate a new unique key for each deployment.

**Generate a secure key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Django Settings

### DJANGO_DEBUG

Enable or disable Django debug mode.

```bash
DJANGO_DEBUG=False  # Production (default)
DJANGO_DEBUG=True   # Development only
```

!!! warning "Never Enable in Production"
    Setting `DJANGO_DEBUG=True` in production exposes sensitive information including stack traces, environment variables, and database queries.

### DJANGO_ALLOWED_HOSTS

Comma-separated list of allowed hostnames.

```bash
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

For development, you can use:
```bash
DJANGO_ALLOWED_HOSTS=*
```

!!! warning "Production Security"
    Never use `*` in production. Always specify exact hostnames.

### DJANGO_ENV

Environment type selector.

```bash
DJANGO_ENV=development   # Development settings (default)
DJANGO_ENV=production    # Production settings
DJANGO_ENV=testing       # Testing settings
```

## Database Configuration

### DATABASE_URL

Database connection URL. Defaults to SQLite if not set.

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/dbname

# SQLite (default)
# DATABASE_URL not set or empty
```

## Admin Configuration

### COMPLEASY_ADMIN_USERNAME

Default admin username.

```bash
COMPLEASY_ADMIN_USERNAME=admin
```

### COMPLEASY_ADMIN_PASSWORD

Default admin password.

```bash
COMPLEASY_ADMIN_PASSWORD=secure-password
```

!!! warning "Change Default Password"
    Always change the default admin password in production.

## HTTPS Security

### SECURE_SSL_REDIRECT

Redirect all HTTP traffic to HTTPS.

```bash
SECURE_SSL_REDIRECT=True
```

### SECURE_HSTS_SECONDS

HTTP Strict Transport Security (HSTS) duration in seconds.

```bash
SECURE_HSTS_SECONDS=31536000  # 1 year
```

### SESSION_COOKIE_SECURE

Only send session cookies over HTTPS.

```bash
SESSION_COOKIE_SECURE=True
```

### CSRF_COOKIE_SECURE

Only send CSRF cookies over HTTPS.

```bash
CSRF_COOKIE_SECURE=True
```

## Rate Limiting

### RATELIMIT_ENABLE

Enable or disable rate limiting on API endpoints.

```bash
RATELIMIT_ENABLE=True   # Enabled (default)
RATELIMIT_ENABLE=False  # Disabled
```

## Server Configuration

### COMPLEASY_URL

Compleasy server URL (used for generating links).

```bash
COMPLEASY_URL=https://yourserver.com
```

## Example .env File

```bash
# Required
SECRET_KEY=your-generated-secret-key-here

# Django
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_ENV=production

# Database
DATABASE_URL=postgresql://compleasy_user:password@postgres:5432/compleasy

# Admin
COMPLEASY_ADMIN_USERNAME=admin
COMPLEASY_ADMIN_PASSWORD=your-secure-password

# HTTPS
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Rate Limiting
RATELIMIT_ENABLE=True

# Server
COMPLEASY_URL=https://yourdomain.com
```

