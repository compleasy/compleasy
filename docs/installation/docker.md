# Docker Installation

Docker is the recommended way to install Compleasy. This guide will walk you through the setup process.

## Prerequisites

Before starting, you need to set up the required environment variables:

### 1. Copy the Example Environment File

```bash
cp .env.example .env
```

### 2. Generate a Secure SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Configure Environment Variables

Edit the `.env` file and replace `GENERATE_THIS_SECRET_KEY_AS_EXPLAINED_ABOVE` with your newly generated key.

### 4. Optional Configuration

For development environments only, you can enable DEBUG mode:

```bash
DJANGO_DEBUG=True
```

!!! danger "Security Warning"
    **NEVER** set `DJANGO_DEBUG=True` in production environments. Running with DEBUG enabled exposes sensitive information including stack traces, environment variables, and database queries to potential attackers.

For production, set allowed hosts:

```bash
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/compleasy/compleasy.git
cd compleasy
```

### 2. Start Compleasy

```bash
docker compose up
```

This will:

- Build the Compleasy Docker image
- Start the web server
- Initialize the database
- Create default admin user

### 3. Access Compleasy

Once started, access Compleasy at:

```
http://localhost:3000
```

Default credentials:
- **Username:** `admin`
- **Password:** `compleasy`

!!! warning "Change Default Password"
    Never use default admin credentials in production. Set `COMPLEASY_ADMIN_PASSWORD` in your `.env` file.

## Production Deployment

### Collect Static Files

Before deploying to production, collect static files:

```bash
docker compose -f docker-compose.yml run --rm compleasy python manage.py collectstatic --no-input
```

### Enable HTTPS Security Headers

Add to your `.env` file:

```bash
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### PostgreSQL Setup

For production, PostgreSQL is strongly recommended. See the [PostgreSQL Setup Guide](postgresql.md) for detailed instructions.

## Next Steps

- [Configure Client](client-setup.md) - Set up Lynis clients
- [Configuration Guide](../configuration/index.md) - Advanced configuration options

