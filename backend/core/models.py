from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    """Custom user established before initial migrations; login arrives in Phase 2."""
    pass
