from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


def default_modules():
    return ['workout']


class User(AbstractUser):
    """Custom user retained from Phase 1; usernames and emails identify accounts."""

    class Meta(AbstractUser.Meta):
        abstract = False
        constraints = [
            models.UniqueConstraint(Lower('username'), name='monarch_username_ci_unique'),
            models.UniqueConstraint(Lower('email'), condition=~Q(email=''), name='monarch_email_ci_unique'),
        ]


class PlayerPaths(models.Model):
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, related_name='player_paths')
    modules = models.JSONField(default=default_modules)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Paths for {self.user_id}'


class SocialIdentity(models.Model):
    provider = models.CharField(max_length=24)
    subject = models.CharField(max_length=255)
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='social_identities')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['provider', 'subject'], name='monarch_social_unique_subject'),
            models.UniqueConstraint(fields=['user', 'provider'], name='monarch_social_one_provider'),
        ]

    def __str__(self):
        return f'{self.provider} login for user {self.user_id}'


class PlayerProfile(models.Model):
    """Non-sensitive onboarding progress and accessibility preferences."""
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, related_name='onboarding_profile')
    display_name = models.CharField(max_length=48, blank=True)
    timezone = models.CharField(max_length=64, default='Asia/Kolkata')
    language = models.CharField(max_length=8, default='en')
    reduced_motion = models.BooleanField(default=False)
    high_contrast = models.BooleanField(default=False)
    current_step = models.PositiveSmallIntegerField(default=1)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Onboarding for {self.user_id}'


class ModulePreference(models.Model):
    """A player's goal and starting level in a particular selected path."""
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='module_preferences')
    module = models.CharField(max_length=12)
    goal = models.CharField(max_length=160, blank=True)
    experience = models.CharField(max_length=16, default='beginner')
    equipment = models.JSONField(default=list, blank=True)
    topics = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'module'], name='monarch_module_pref_unique')]

    def __str__(self):
        return f'{self.module} preferences for {self.user_id}'


class WeeklyAvailability(models.Model):
    """Per-user, per-module weekly time budget; no artificial progress data."""
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='weekly_availability')
    module = models.CharField(max_length=12)
    weekday = models.PositiveSmallIntegerField()  # Monday=0, Sunday=6
    minutes = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'module', 'weekday'], name='monarch_schedule_unique')]


class PrivatePhysique(models.Model):
    """Optional, separately stored physique inputs; never included in public/profile APIs."""
    user = models.OneToOneField('core.User', on_delete=models.CASCADE, related_name='private_physique')
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Private measurements for {self.user_id}'
