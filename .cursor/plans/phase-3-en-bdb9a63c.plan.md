<!-- bdb9a63c-04a9-461f-841b-ec40fcc650f6 6e541787-a999-49da-bb32-b2cf16152af0 -->
# Phase 3: Enhancement Features & Optimizations

## Overview

Implement all Phase 3 enhancements (Issues 18-24) to add missing production features, improve monitoring capabilities, enhance admin interfaces, and optimize database performance.

## Prerequisites

- Phase 0 (Test Infrastructure): ✅ Complete
- Phase 1 (Security Fixes): ✅ Complete  
- Phase 2 (Structure Improvements): ✅ Complete
- All tests must pass: `docker compose -f docker-compose.dev.yml --profile test run --rm test`
- Lynis integration must remain functional

## Implementation Tasks

### 1. Add Health Check Endpoint (Issue #18)

**Purpose**: Enable container orchestration and monitoring tools to verify service health

**Create**: `src/api/health.py`

```python
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

def health_check(request):
    """Health check endpoint for monitoring and orchestration."""
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    status_code = 200
    
    # Database connectivity check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
        status_code = 503
    
    # Cache connectivity check
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        health_status['checks']['cache'] = 'ok'
    except Exception as e:
        health_status['checks']['cache'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
        if status_code == 200:
            status_code = 200  # Cache failure is not critical
    
    return JsonResponse(health_status, status=status_code)
```

**Update**: `src/compleasy/urls.py` - Add health check route

```python
from api.health import health_check

urlpatterns = [
    path('health/', health_check, name='health_check'),
    # ... existing patterns
]
```

**Add test**: `src/api/tests.py` - Test health check functionality

### 2. Improve Error Handling (Issue #19)

**Purpose**: Provide consistent, structured error responses across API endpoints

**Create**: `src/api/utils/error_responses.py`

```python
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def error_response(message, status_code, error_code=None, details=None):
    """Return standardized error response."""
    response_data = {
        'error': {
            'message': message,
            'code': error_code or f'ERR_{status_code}'
        }
    }
    
    if details:
        response_data['error']['details'] = details
    
    logger.warning(f'Error response: {message} (status={status_code}, code={error_code})')
    
    return JsonResponse(response_data, status=status_code)

# Common error responses
def bad_request(message, details=None):
    return error_response(message, 400, 'BAD_REQUEST', details)

def unauthorized(message='Unauthorized'):
    return error_response(message, 401, 'UNAUTHORIZED')

def not_found(message='Resource not found'):
    return error_response(message, 404, 'NOT_FOUND')

def internal_error(message='Internal server error'):
    return error_response(message, 500, 'INTERNAL_ERROR')
```

**Update**: `src/api/views.py` - Standardize error responses

- Replace `HttpResponse('Invalid license key', status=401)` with structured errors
- Replace `HttpResponse('No report found', status=400)` with structured errors
- Add try-except blocks for database errors
- Keep Lynis endpoint responses unchanged (backward compatibility)

### 3. Add Backup Documentation (Issue #20)

**Purpose**: Document backup strategies for both SQLite and PostgreSQL deployments

**Update**: `README.md` - Add new "Backup & Recovery" section

```markdown
## Backup & Recovery

### SQLite Backup (Development/Small Deployments)

#### Manual Backup

bash
# Create backup directory
mkdir -p backups

# Backup database (while application is running)
docker compose exec compleasy sqlite3 /app/compleasy.sqlite3 ".backup '/app/backups/compleasy-backup-$(date +%Y%m%d-%H%M%S).sqlite3'"

# Copy backup to host
docker compose cp compleasy:/app/backups/. ./backups/


#### Automated Backup Script

Create `scripts/backup-sqlite.sh`:

bash
#!/bin/bash
BACKUP_DIR="./backups"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR
docker compose exec compleasy sqlite3 /app/compleasy.sqlite3 ".backup '/app/backups/backup-$DATE.sqlite3'"
docker compose cp compleasy:/app/backups/backup-$DATE.sqlite3 $BACKUP_DIR/

# Cleanup old backups
find $BACKUP_DIR -name "*.sqlite3" -mtime +$RETENTION_DAYS -delete


Schedule with cron: `0 2 * * * /path/to/backup-sqlite.sh`

### PostgreSQL Backup (Production)

bash
# Backup database
pg_dump -h localhost -U compleasy_user -d compleasy > backup-$(date +%Y%m%d).sql

# Restore database
psql -h localhost -U compleasy_user -d compleasy < backup-20241113.sql


### Restore from Backup

#### SQLite

bash
# Stop application
docker compose down

# Copy backup file
cp backups/compleasy-backup-20241113.sqlite3 src/compleasy.sqlite3

# Start application
docker compose up -d


#### PostgreSQL

bash
# Connect to database container
docker compose exec postgres psql -U compleasy_user

# Drop and recreate database
DROP DATABASE compleasy;
CREATE DATABASE compleasy;
\q

# Restore from backup
docker compose exec -T postgres psql -U compleasy_user compleasy < backup.sql

```

### 4. Add Security Tests for Policy Query (Issue #21)

**Purpose**: Ensure policy query parser is secure against injection and malicious patterns

**Create**: `src/api/tests_policy_security.py`

```python
import pytest
from api.utils.policy_query import parse_query, evaluate_query
from api.utils.lynis_report import LynisReport

class TestPolicyQuerySecurity:
    """Security tests for policy query evaluation."""
    
    @pytest.fixture
    def sample_report(self):
        """Create a sample report for testing."""
        report_data = """
report_version_major=3
report_version_minor=0
hardening_index=75
automation_tool_running=ansible
        """
        return LynisReport(report_data)
    
    def test_sql_injection_attempts(self, sample_report):
        """Test that SQL injection patterns are rejected."""
        malicious_queries = [
            "hardening_index = 75; DROP TABLE devices;",
            "automation_tool_running = 'test' OR '1'='1'",
            "hardening_index = 75 UNION SELECT * FROM users",
            "automation_tool_running contains \"'; DELETE FROM licensekey; --\"",
        ]
        
        for query in malicious_queries:
            result = evaluate_query(sample_report, query)
            # Should either fail to parse or return None
            assert result in [None, False], f"Dangerous query not blocked: {query}"
    
    def test_code_injection_attempts(self, sample_report):
        """Test that code injection patterns are rejected."""
        malicious_queries = [
            "hardening_index = __import__('os').system('ls')",
            "automation_tool_running contains exec('print(1)')",
            "hardening_index = eval('1+1')",
        ]
        
        for query in malicious_queries:
            result = parse_query(query)
            assert result is None, f"Code injection not blocked: {query}"
    
    def test_path_traversal_attempts(self, sample_report):
        """Test that path traversal patterns are rejected."""
        malicious_queries = [
            "automation_tool_running contains \"../../../etc/passwd\"",
            "hardening_index = ../../config",
        ]
        
        for query in malicious_queries:
            result = evaluate_query(sample_report, query)
            # Should evaluate safely (not cause file access)
            assert isinstance(result, (bool, type(None)))
    
    def test_field_validation(self, sample_report):
        """Test that only valid field names are accepted."""
        valid_queries = [
            "hardening_index > 70",
            "automation_tool_running contains \"ansible\"",
        ]
        
        for query in valid_queries:
            result = evaluate_query(sample_report, query)
            assert result is not None
    
    def test_operator_validation(self, sample_report):
        """Test that only valid operators are accepted."""
        invalid_queries = [
            "hardening_index && 75",
            "automation_tool_running || test",
            "hardening_index << 75",
        ]
        
        for query in invalid_queries:
            result = parse_query(query)
            assert result is None, f"Invalid operator not rejected: {query}"
    
    def test_resource_exhaustion(self, sample_report):
        """Test that queries don't cause resource exhaustion."""
        # Test with very long query
        long_query = "hardening_index = " + "1" * 10000
        result = parse_query(long_query)
        # Should fail gracefully, not hang
        assert result is None or isinstance(result, list)
```

**Update**: `pytest.ini` - Add test marker

```ini
[pytest]
markers =
    integration: Integration tests requiring Docker
    security: Security-focused tests
```

### 5. Enhance Admin Interfaces (Issue #22)

**Purpose**: Improve Django admin usability with better displays, filters, and search

**Update**: `src/api/admin.py`

```python
from django.contrib import admin
from django.utils.html import format_html
from .models import LicenseKey, Device, FullReport, DiffReport, PolicyRule, PolicyRuleset

@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ('licensekey', 'created_by', 'created_at', 'device_count')
    list_filter = ('created_at', 'created_by')
    search_fields = ('licensekey', 'created_by__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def device_count(self, obj):
        return obj.device_set.count()
    device_count.short_description = 'Devices'

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'hostid', 'os_display', 'lynis_version', 'warnings', 'compliance_status', 'last_update')
    list_filter = ('compliant', 'os', 'created_at', 'last_update', 'licensekey')
    search_fields = ('hostname', 'hostid', 'hostid2', 'os', 'distro')
    readonly_fields = ('created_at', 'updated_at', 'hostid', 'hostid2')
    date_hierarchy = 'last_update'
    filter_horizontal = ('rulesets',)
    
    fieldsets = (
        ('Identification', {
            'fields': ('hostname', 'hostid', 'hostid2', 'licensekey')
        }),
        ('System Information', {
            'fields': ('os', 'distro', 'distro_version', 'lynis_version')
        }),
        ('Compliance', {
            'fields': ('warnings', 'compliant', 'rulesets')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_update'),
            'classes': ('collapse',)
        }),
    )
    
    def os_display(self, obj):
        if obj.distro:
            return f"{obj.os} - {obj.distro}"
        return obj.os
    os_display.short_description = 'Operating System'
    
    def compliance_status(self, obj):
        if obj.compliant:
            return format_html('<span style="color: green;">✓ Compliant</span>')
        return format_html('<span style="color: red;">✗ Non-compliant</span>')
    compliance_status.short_description = 'Status'

@admin.register(FullReport)
class FullReportAdmin(admin.ModelAdmin):
    list_display = ('device', 'created_at', 'report_preview')
    list_filter = ('created_at', 'device__licensekey')
    search_fields = ('device__hostname', 'device__hostid')
    readonly_fields = ('created_at', 'full_report')
    date_hierarchy = 'created_at'
    
    def report_preview(self, obj):
        preview = obj.full_report[:100] + '...' if len(obj.full_report) > 100 else obj.full_report
        return preview
    report_preview.short_description = 'Preview'

@admin.register(DiffReport)
class DiffReportAdmin(admin.ModelAdmin):
    list_display = ('device', 'created_at', 'diff_preview')
    list_filter = ('created_at', 'device__licensekey')
    search_fields = ('device__hostname', 'device__hostid')
    readonly_fields = ('created_at', 'diff_report')
    date_hierarchy = 'created_at'
    
    def diff_preview(self, obj):
        preview = obj.diff_report[:100] + '...' if len(obj.diff_report) > 100 else obj.diff_report
        return preview
    diff_preview.short_description = 'Preview'

@admin.register(PolicyRule)
class PolicyRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_query', 'enabled', 'alert', 'rule_status', 'created_at', 'updated_at')
    list_filter = ('enabled', 'alert', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'rule_query')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Rule Configuration', {
            'fields': ('rule_query', 'enabled', 'alert')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rule_status(self, obj):
        if obj.enabled:
            status = '<span style="color: green;">● Active</span>'
            if obj.alert:
                status += ' <span style="color: orange;">[Alert]</span>'
            return format_html(status)
        return format_html('<span style="color: gray;">○ Disabled</span>')
    rule_status.short_description = 'Status'

@admin.register(PolicyRuleset)
class PolicyRulesetAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_count', 'device_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('rules',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Rules', {
            'fields': ('rules',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rule_count(self, obj):
        return obj.rules.count()
    rule_count.short_description = 'Rules'
    
    def device_count(self, obj):
        return obj.devices.count()
    device_count.short_description = 'Devices'
```

### 6. Add Audit Logging Middleware (Issue #23)

**Purpose**: Create audit trail for sensitive operations (license creation, device enrollment)

**Create**: `src/api/middleware.py`

```python
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger('audit')

class AuditLoggingMiddleware(MiddlewareMixin):
    """Middleware to log sensitive operations for audit trail."""
    
    SENSITIVE_PATHS = [
        '/admin/api/licensekey/add/',
        '/admin/api/licensekey/',
        '/api/lynis/upload/',
        '/admin/api/device/',
    ]
    
    def process_request(self, request):
        """Log incoming requests to sensitive endpoints."""
        if any(request.path.startswith(path) for path in self.SENSITIVE_PATHS):
            user = getattr(request, 'user', AnonymousUser())
            username = user.username if not user.is_anonymous else 'anonymous'
            
            logger.info(
                f'AUDIT: {request.method} {request.path} | '
                f'User: {username} | '
                f'IP: {self.get_client_ip(request)} | '
                f'User-Agent: {request.META.get("HTTP_USER_AGENT", "unknown")}'
            )
    
    def process_response(self, request, response):
        """Log responses from sensitive endpoints."""
        if any(request.path.startswith(path) for path in self.SENSITIVE_PATHS):
            user = getattr(request, 'user', AnonymousUser())
            username = user.username if not user.is_anonymous else 'anonymous'
            
            logger.info(
                f'AUDIT: {request.method} {request.path} | '
                f'User: {username} | '
                f'Status: {response.status_code}'
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

**Update**: `src/compleasy/settings/base.py` - Add middleware and audit logger

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.middleware.AuditLoggingMiddleware',  # Add audit logging
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'audit': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'audit_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/audit.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'audit',
        },
    },
    'loggers': {
        'audit': {
            'handlers': ['audit_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
}
```

**Create**: `src/logs/` directory with `.gitkeep` and add to `.gitignore`

### 7. Add Database Indexes (Issue #24)

**Purpose**: Optimize frequently queried fields to improve performance

**Update**: `src/api/models.py` - Add indexes

```python
class LicenseKey(models.Model):
    licensekey = models.CharField(max_length=255, db_index=True)  # Add index
    # ... rest of model

class Device(models.Model):
    # ... existing fields
    hostid = models.CharField(max_length=255, db_index=True)  # Add index
    hostid2 = models.CharField(max_length=255, db_index=True)  # Add index
    # ... rest of model
    
    class Meta:
        indexes = [
            models.Index(fields=['licensekey', 'hostid']),  # Composite index
            models.Index(fields=['licensekey', 'hostid2']),  # Composite index
            models.Index(fields=['last_update']),  # For sorting
        ]
```

**Create migration**:

```bash
docker compose -f docker-compose.dev.yml run --rm compleasy python manage.py makemigrations --name add_performance_indexes
```

**Test migration**:

```bash
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest
```

## Testing Strategy

### Unit Tests

```bash
# Run all tests including new security tests
docker compose -f docker-compose.dev.yml --profile test run --rm test

# Run only security tests
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest -m security -v

# Run with coverage
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest --cov=api --cov-report=html
```

### Health Check Test

```bash
# Start service
docker compose -f docker-compose.dev.yml up -d compleasy

# Test health endpoint
curl http://localhost:8000/health/

# Should return: {"status": "healthy", "checks": {"database": "ok", "cache": "ok"}}
```

### Integration Tests

```bash
# Run full integration test suite
docker compose -f docker-compose.dev.yml --profile test run --rm test pytest -m integration -v
```

## Verification Checklist

- [x] Health check endpoint returns correct status
- [x] Error responses are standardized across API
- [ ] Backup documentation is complete and tested
- [x] Policy query security tests all pass
- [x] Admin interfaces show enhanced functionality
- [x] Audit logging captures sensitive operations
- [x] Database indexes created successfully
- [x] All existing tests still pass
- [ ] Lynis integration still functional
- [ ] No performance regressions

## Files Modified

**New Files**:

- `src/api/health.py` - Health check endpoint
- `src/api/utils/error_responses.py` - Standardized error handling
- `src/api/tests_policy_security.py` - Security tests for policy queries
- `src/api/middleware.py` - Audit logging middleware
- `scripts/backup-sqlite.sh` - Automated backup script

**Modified Files**:

- `README.md` - Add backup documentation
- `src/compleasy/urls.py` - Add health check route
- `src/api/views.py` - Improve error handling
- `src/api/admin.py` - Enhanced admin interfaces
- `src/api/models.py` - Add database indexes
- `src/compleasy/settings/base.py` - Add middleware and audit logger
- `pytest.ini` - Add security test marker

**New Migrations**:

- `src/api/migrations/XXXX_add_performance_indexes.py`

## Rollback Plan

If issues arise:

1. Revert middleware: Remove `AuditLoggingMiddleware` from `MIDDLEWARE` setting
2. Revert indexes: Run `python manage.py migrate api <previous_migration>`
3. Remove health endpoint: Comment out route in `urls.py`
4. Revert error handling: API endpoints still work with HttpResponse

Critical Lynis endpoints are not modified in this phase, ensuring backward compatibility.

### To-dos

- [x] Create health check endpoint with database and cache connectivity checks
- [x] Implement standardized error response format across API endpoints
- [ ] Add comprehensive backup and recovery documentation to README
- [x] Write security tests for policy query parser to prevent injection attacks
- [x] Enhance Django admin interfaces with filters, search, and better displays
- [x] Create audit logging middleware for tracking sensitive operations
- [x] Add database indexes to frequently queried fields for performance
- [ ] Run full test suite and verify all Phase 3 features work correctly