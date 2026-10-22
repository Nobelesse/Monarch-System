from django.http import HttpResponseForbidden

class LoopbackOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.META.get('REMOTE_ADDR') not in ('127.0.0.1', '::1'):
            return HttpResponseForbidden('Local administrator access only.')
        return self.get_response(request)
