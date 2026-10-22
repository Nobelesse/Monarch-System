from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PlayerPaths, SocialIdentity, PlayerProfile, ModulePreference, WeeklyAvailability, PrivatePhysique

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
