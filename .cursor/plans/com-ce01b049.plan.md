<!-- ce01b049-d6be-4414-af6e-073951f6bd3d 6136888e-9e49-41a4-8252-58cbb2ad05a8 -->
# Compleasy: Pre-Feature Security & Structure Improvements

## Critical Security Issues (MUST FIX)

### 1. Open Redirect Vulnerability

**Location**: `src/frontend/views.py` lines 109, 300, 313
**Issue**: Using `request.META.get('HTTP_REFERER')` directly in redirects allows attackers to redirect users to malicious sites.
**Fix**: Validate referer against safe URLs or use `next` parameter with whitelist validation.

### 2. Weak Default Credentials

**Location**: `docker-compose.yml` line 12
**Issue**: Hardcoded default password `COMPLEASY_ADMIN_PASSWORD=compleasy` in version control.
**Fix**: Remove default password, require it in `.env` file, update README with strong password requirements. Keep "compleasy" password by default, but in `.env.example` and well commented.

### 3. Overly Permissive ALLOWED_HOSTS

**Location**: `src/compleasy/settings.py` line 54
**Issue**: `ALLOWED_HOSTS = ['*']` allows any host header, enabling host header injection attacks.
**Fix**: Require explicit configuration via environment variable. Add wildcard by default in envar in ``.env.example` but well documented.`

### 4. DEBUG Logging in Production

**Location**: `src/compleasy/settings.py` lines 17-29
**Issue**: Root logger set to `DEBUG` level exposes sensitive information.
**Fix**: Make logging level configurable via environment variable, default to INFO.

### 5. Missing Security Headers

**Location**: `src/compleasy/settings.py`
**Issue**: No HSTS, X-Content-Type-Options, X-Frame-Options (already has ClickjackingMiddleware), CSP headers.
**Fix**: Add Django security settings for production deployment.

### 6. Unvalidated Input in Views

**Location**: `src/frontend/views.py` lines 141-151, 163-177
**Issue**: License keys from URL parameters used without validation in `enroll_sh()` and `download_lynis_custom_profile()`.
**Fix**: Validate license key format and existence before using in templates.

### 7. No Rate Limiting

**Location**: `src/api/views.py` (upload_report, check_license)
**Issue**: No protection against brute force attacks on license key validation or API flooding.
**Fix**: Implement Django rate limiting (django-ratelimit or similar) on authentication and API endpoints.

### 8. Outdated Python Version

**Location**: `Dockerfile` line 1
**Issue**: Python 3.8 reached EOL in October 2024, no longer receives security updates.
**Fix**: Update to Python 3.11 or 3.12.

### 9. Unpinned Dependencies

**Location**: `src/requirements.txt`
**Issue**: Using version ranges (`>=`) allows automatic installation of potentially vulnerable versions.
**Fix**: Pin exact versions, add `requirements-dev.txt`, document update process.

### 10. SQLite for Production

**Location**: `src/compleasy/settings.py` lines 109-114
**Issue**: SQLite not suitable for production (no concurrent writes, backup complexity, performance).
**Fix**: Add PostgreSQL support with environment-based database configuration.

## Code Structure Issues

### 11. Utils Package Location

**Location**: `src/utils/`
**Issue**: Utils folder at project root, not within an app. Breaks Django conventions.
**Fix**: Move to `src/api/utils/` or create separate `core` app for shared utilities.

### 12. No Environment-Based Settings

**Location**: `src/compleasy/settings.py`
**Issue**: Single settings file for all environments (dev/staging/prod).
**Fix**: Split into `settings/base.py`, `settings/development.py`, `settings/production.py`.

### 13. Missing STATIC_ROOT Configuration

**Location**: `src/compleasy/settings.py`
**Issue**: `STATIC_ROOT` not configured, required for `collectstatic` in production.
**Fix**: Add `STATIC_ROOT = BASE_DIR / 'staticfiles'` and document deployment process.

### 14. Mixed Concerns in Models

**Location**: `src/api/models.py` lines 34-41
**Issue**: `FullReport.save()` handles cleanup logic (deleting old reports), violates SRP.
**Fix**: Move to signal handler or celery task for better separation.

### 15. No API Versioning

**Location**: `src/api/urls.py`
**Issue**: API endpoints lack versioning (`/api/lynis/upload/` should be `/api/v1/lynis/upload/`).
**Fix**: Add version namespace while maintaining backward compatibility alias for Lynis.

### 16. Empty Test Files

**Location**: `src/api/tests.py`, `src/frontend/tests.py`
**Issue**: No test coverage for critical functionality.
**Fix**: Add basic tests for authentication, API endpoints, policy evaluation.

### 17. No Input Validation on Forms

**Location**: `src/api/forms.py`
**Issue**: `ReportUploadForm` has no field validators (max length, format validation).
**Fix**: Add validators for license key format, hostid format, reasonable data size limits.

## Additional Improvements

### 18. Missing Health Check Endpoint

**Issue**: No endpoint for container orchestration health checks.
**Fix**: Add `/health/` endpoint returning database connectivity status.

### 19. Inadequate Error Handling

**Location**: Multiple views return generic error responses
**Issue**: Inconsistent error responses, no structured error format.
**Fix**: Create consistent error response format, proper HTTP status codes.

### 20. Missing Backup Documentation

**Issue**: No documented backup strategy for SQLite database.
**Fix**: Add backup instructions to README, consider automatic backup script.

### 21. SQL Injection Risk in Policy Query

**Location**: `src/api/utils/policy_query.py`
**Issue**: While using pyparsing (safe), the evaluation logic needs security review.
**Assessment**: Current implementation appears safe but needs explicit testing.
**Fix**: Add comprehensive tests for malicious query patterns.

## Django Best Practices

### 22. Missing Admin Configuration

**Location**: `src/api/admin.py`, `src/frontend/admin.py`
**Issue**: Models not registered in Django admin or basic registration only.
**Fix**: Add comprehensive admin interfaces with proper list_display, filters, search.

### 23. No Middleware for Security Logging

**Issue**: No audit trail for sensitive operations (license key creation, device enrollment).
**Fix**: Add custom middleware or use django-auditlog.

### 24. Missing Index Optimization

**Location**: `src/api/models.py`
**Issue**: No database indexes on frequently queried fields (hostid, licensekey).
**Fix**: Add `db_index=True` to appropriate fields, create migrations.

## Lynis Integration (DO NOT BREAK)

**Critical**: The following endpoints MUST remain unchanged to maintain compatibility:

- `/api/lynis/upload/` - Used by Lynis for report upload
- `/api/lynis/license/` - Used by Lynis for license validation
- Both endpoints require `@csrf_exempt` (correct for external API)
- Request/response format must not change

## Recommended Implementation Order

1. **Phase 0 - Test Infrastructure** (NEW): Set up testing environment and basic tests BEFORE making any changes

- Create `docker-compose.dev.yml` for development with isolated testing
- Add Lynis client service for integration testing
- Write basic tests for existing functionality (especially Lynis API endpoints)
- Ensure tests pass with current codebase

2. **Phase 1 - Critical Security** (Issues 1-10): Fix immediate security vulnerabilities
3. **Phase 2 - Structure** (Issues 11-17): Improve code organization and maintainability  
4. **Phase 3 - Enhancement** (Issues 18-24): Add missing features and optimizations

## Files Requiring Changes

**Critical**:

- `src/compleasy/settings.py` - Security headers, logging, database config
- `src/frontend/views.py` - Fix open redirects, add input validation
- `docker-compose.yml` - Remove default password
- `Dockerfile` - Update Python version
- `src/requirements.txt` - Pin dependencies
- `.env.example` - Add comprehensive configuration template

**Important**:

- `src/api/models.py` - Add indexes, move cleanup logic
- `src/api/forms.py` - Add validators
- `src/api/urls.py` - Add versioning with backward compatibility
- Create `src/compleasy/settings/` directory structure

**Nice to Have**:

- `src/api/tests.py` - Add test coverage
- `src/api/admin.py` - Improve admin interface
- Add `src/api/health.py` - Health check endpoint

### To-dos

- [ ] Fix open redirect vulnerability in frontend views (validate HTTP_REFERER)
- [ ] Remove hardcoded credentials from docker-compose.yml, create .env.example
- [ ] Fix ALLOWED_HOSTS to require explicit configuration
- [ ] Add security headers and HSTS configuration to settings.py
- [ ] Make logging level configurable via environment variable
- [ ] Implement rate limiting on API and auth endpoints
- [ ] Add license key validation in enroll and profile download views
- [ ] Update Dockerfile to Python 3.11 or 3.12
- [ ] Pin exact dependency versions in requirements.txt
- [ ] Add PostgreSQL configuration for production environments
- [ ] Reorganize utils folder into proper Django app structure
- [ ] Split settings into base/development/production files
- [ ] Add STATIC_ROOT and document collectstatic process
- [ ] Move report cleanup logic from model save to signals
- [ ] Add API versioning with backward compatibility for Lynis
- [ ] Add comprehensive validators to ReportUploadForm
- [ ] Add database indexes to frequently queried fields
- [ ] Create health check endpoint for monitoring
- [ ] Add basic test coverage for critical functionality
- [ ] Enhance Django admin interfaces with proper displays and filters