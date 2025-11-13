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

