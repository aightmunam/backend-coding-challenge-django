from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Represents a user and note creator."""

    def __str__(self):
        return self.username
