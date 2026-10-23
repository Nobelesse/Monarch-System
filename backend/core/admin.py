from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PlayerPaths, SocialIdentity, PlayerProfile, ModulePreference, WeeklyAvailability, PrivatePhysique, WorkoutExercise, WorkoutPlan, WorkoutSession, WorkoutPlanItem

admin.site.register(User, UserAdmin)

@admin.register(PlayerPaths)
class PlayerPathsAdmin(admin.ModelAdmin):
    list_display = ('user', 'modules', 'updated_at')
    search_fields = ('user__username', 'user__email')

@admin.register(SocialIdentity)
class SocialIdentityAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('provider', 'subject', 'user', 'created_at')

    def has_add_permission(self, request):
        return False

# Admin access is available ONLY from the separate 127.0.0.1:8001 listener.
@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'current_step', 'completed_at')
    search_fields = ('user__username',)

@admin.register(ModulePreference)
class ModulePreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'experience', 'updated_at')
    search_fields = ('user__username',)

@admin.register(WeeklyAvailability)
class WeeklyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'weekday', 'minutes')
    search_fields = ('user__username',)

# Optional body measurements are purposefully excluded from the admin UI.


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'movement', 'equipment', 'minimum_level', 'active')
    list_filter = ('movement', 'equipment', 'minimum_level', 'active')
    search_fields = ('name', 'slug')

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_snapshot', 'generated_at')
    search_fields = ('user__username',)
    readonly_fields = ('source_signature', 'goal_snapshot', 'experience_snapshot',
                       'equipment_snapshot', 'avoid_tags', 'focus_mode', 'pace', 'generated_at')

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ('plan', 'weekday', 'focus', 'theme', 'planned_minutes')
    readonly_fields = ('plan', 'weekday', 'focus', 'theme', 'available_minutes', 'planned_minutes')

@admin.register(WorkoutPlanItem)
class WorkoutPlanItemAdmin(admin.ModelAdmin):
    list_display = ('session', 'position', 'exercise')
    readonly_fields = ('session', 'position', 'exercise', 'sets', 'reps', 'rest_seconds')
