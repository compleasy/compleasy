# Advanced Configuration

Advanced configuration options and customization for Compleasy.

## Custom Settings

### Logging Configuration

Customize logging levels and handlers in Django settings.

### Static Files

Configure static file serving:

```bash
# Collect static files
docker compose run --rm compleasy python manage.py collectstatic --no-input
```

### Media Files

Configure media file storage and serving.

## API Configuration

### API Versioning

Compleasy supports API versioning:

- **Versioned API**: `/api/v1/lynis/upload/`, `/api/v1/lynis/license/`
- **Legacy API**: `/api/lynis/upload/`, `/api/lynis/license/`

Both endpoints route to the same views for backward compatibility.

### Rate Limiting

Customize rate limits per endpoint in Django settings.

## Database Optimization

### Connection Pooling

For PostgreSQL, configure connection pooling:

```python
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # Persistent connections
    }
}
```

### Indexes

Compleasy includes performance indexes on frequently queried fields. See migrations for details.

## Custom Policies

### Policy Rules

Define custom policy rules through the web interface or API.

### Policy Rule Sets

Create rule sets to apply multiple policies to devices.

## Integration

### Webhooks

Configure webhooks for events (coming soon).

### API Integration

Integrate Compleasy with other tools using the REST API.

## Performance Tuning

### Caching

Configure caching for better performance:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Database Queries

Monitor and optimize database queries:

```bash
# Enable query logging
DJANGO_DEBUG=True  # Development only
```

## Customization

### Branding

Customize logos and branding in templates.

### Themes

Modify CSS and templates for custom appearance.

## Troubleshooting

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```bash
DJANGO_DEBUG=True
```

!!! warning "Development Only"
    Never enable debug mode in production.

### Database Shell

Access database directly:

```bash
docker compose exec compleasy python manage.py dbshell
```

### Django Shell

Interactive Python shell:

```bash
docker compose exec compleasy python manage.py shell
```

## Additional Resources

- [Django Settings Reference](https://docs.djangoproject.com/en/stable/ref/settings/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

