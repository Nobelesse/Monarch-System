"""Prevent browsers/proxies from caching personal account responses."""
class PrivateAPICacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/api/auth/') or request.path.startswith('/api/paths/'):
            response['Cache-Control'] = 'no-store'
        return response
