from django.urls import path
from core.views import health, system_info
from core import auth_api, onboarding_api, workout_api

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
    path('api/workout/library/', workout_api.library),
    path('api/workout/plan/', workout_api.current_plan),
    path('api/workout/plan/generate/', workout_api.generate_plan),
    path('api/workout/items/<int:item_id>/alternatives/', workout_api.alternatives),
    path('api/workout/items/<int:item_id>/substitute/', workout_api.substitute),
    path('api/workout/items/<int:item_id>/adjust/', workout_api.adjust_item),
    path('api/workout/items/<int:item_id>/move/', workout_api.move_item),
]
# Public URLs intentionally do NOT contain /admin/.
