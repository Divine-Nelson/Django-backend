from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # email is now unique, but not the primary key
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, default="Unknown")
    last_name = models.CharField(max_length=100, default="Unknown")
    password = models.CharField(max_length=100)

    # Avoid clashes with auth.User's related names
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set",  # Updated related_name for clarity
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
