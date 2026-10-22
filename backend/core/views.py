from django.db import connection, DatabaseError
from django.http import JsonResponse
from django.views.decorators.http import require_GET
@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({'status': 'degraded', 'api': 'online', 'database': 'unavailable', 'version': '0.1.0'}, status=503)
    response = JsonResponse({'status': 'ok', 'api': 'online', 'database': 'connected', 'version': '0.1.0'})
    response['Cache-Control'] = 'no-store'
    return response
@require_GET
def system_info(request):
    return JsonResponse({'name': 'Monarch System', 'version': '0.1.0', 'phase': 1, 'modules': ['workout', 'study', 'learning'], 'authentication_available': False, 'public_access_ready': False})
