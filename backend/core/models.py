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
