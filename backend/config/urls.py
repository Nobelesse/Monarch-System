from django.urls import path
from core.views import health, system_info
from core import auth_api, onboarding_api

urlpatterns = [
    path('api/health/', health), path('api/system/', system_info),
    path('api/auth/csrf/', auth_api.csrf),
    path('api/auth/register/', auth_api.register),
    path('api/auth/login/', auth_api.sign_in),
    path('api/auth/logout/', auth_api.sign_out),
    path('api/auth/me/', auth_api.me),
    path('api/auth/google/', auth_api.google_sign_in),
    path('api/auth/google/link/', auth_api.google_link),
    path('api/paths/', auth_api.paths),
    path('api/onboarding/', onboarding_api.onboarding),
]
# Public URLs intentionally do NOT contain /admin/.
