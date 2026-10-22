from django.db import connection, DatabaseError
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.conf import settings
@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({'status': 'degraded', 'api': 'online', 'database': 'unavailable', 'version': '0.3.0'}, status=503)
    response = JsonResponse({'status': 'ok', 'api': 'online', 'database': 'connected', 'version': '0.3.0'})
    response['Cache-Control'] = 'no-store'
    return response
@require_GET
def system_info(request):
    return JsonResponse({'name': 'Monarch System', 'version': '0.3.0', 'phase': 3, 'modules': ['workout', 'study', 'learning'], 'authentication_available': True, 'onboarding_available': True, 'public_access_ready': False, 'google_login_configured': bool(settings.GOOGLE_CLIENT_ID), 'google_client_id': settings.GOOGLE_CLIENT_ID})
