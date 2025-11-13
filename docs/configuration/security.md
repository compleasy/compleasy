# Security Configuration

Security best practices and hardening guide for Compleasy.

## Production Security Checklist

- [ ] `DJANGO_DEBUG=False` is set
- [ ] `DJANGO_ALLOWED_HOSTS` is configured (not `*`)
- [ ] `SECRET_KEY` is unique and secure
- [ ] Default admin password is changed
- [ ] HTTPS is enabled with security headers
- [ ] Rate limiting is enabled
- [ ] PostgreSQL is used (not SQLite)
- [ ] Regular backups are configured

## Critical Security Settings

### Debug Mode

!!! danger "Critical"
    **NEVER** enable debug mode in production.

```bash
DJANGO_DEBUG=False
```

Debug mode exposes:
- Stack traces with code
- Environment variables
- Database queries
- Internal file paths

### Allowed Hosts

Always specify exact hostnames:

```bash
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Never use:
```bash
DJANGO_ALLOWED_HOSTS=*  # INSECURE
```

### Secret Key

Generate a unique, secure secret key for each deployment:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Never reuse secret keys across deployments.

## HTTPS Configuration

### Enable HTTPS Redirect

```bash
SECURE_SSL_REDIRECT=True
```

### HTTP Strict Transport Security (HSTS)

```bash
SECURE_HSTS_SECONDS=31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### Secure Cookies

```bash
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Rate Limiting

Enable rate limiting to protect against abuse:

```bash
RATELIMIT_ENABLE=True
```

Rate limits apply to:
- API endpoints (`/api/lynis/upload/`, `/api/lynis/license/`)
- Login attempts
- Registration attempts

## Database Security

### Use PostgreSQL in Production

SQLite is fine for development, but PostgreSQL provides:
- Better concurrency
- Connection pooling
- Better security features

See [PostgreSQL Setup](../installation/postgresql.md) for details.

### Database Credentials

- Use strong passwords
- Limit database user permissions
- Use connection encryption
- Regularly rotate credentials

## Authentication Security

### Change Default Credentials

Never use default admin credentials in production:

```bash
COMPLEASY_ADMIN_USERNAME=admin
COMPLEASY_ADMIN_PASSWORD=your-strong-password-here
```

### Password Requirements

Ensure strong passwords:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Not dictionary words
- Not reused from other services

## Network Security

### Firewall Configuration

Only expose necessary ports:
- `3000` (or your configured port) for HTTP/HTTPS
- Database port only to application server (if external)

### Reverse Proxy

Use a reverse proxy (Nginx, Apache) for:
- SSL/TLS termination
- Additional security headers
- Rate limiting
- DDoS protection

## Security Headers

Compleasy includes security headers, but you can add more via reverse proxy:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

## Regular Updates

- Keep Django and dependencies updated
- Monitor security advisories
- Apply security patches promptly
- Review and update regularly

## Backup and Recovery

- Regular database backups
- Test restore procedures
- Store backups securely
- Encrypt backup files

## Monitoring and Logging

- Monitor access logs
- Set up alerts for suspicious activity
- Review logs regularly
- Use centralized logging for production

## Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)

