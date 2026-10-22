from django.urls import path
from core.views import health, system_info
urlpatterns = [path('api/health/', health), path('api/system/', system_info)]
# No admin routes on this listener. A separate local admin service arrives in Phase 2.
