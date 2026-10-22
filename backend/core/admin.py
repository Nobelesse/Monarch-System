from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PlayerPaths, SocialIdentity

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
