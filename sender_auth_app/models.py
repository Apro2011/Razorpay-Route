from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Sender(AbstractUser):
    # Add related_name to resolve reverse accessor clash
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="Groups",
        blank=True,
        related_name="sender_groups",
        related_query_name="sender_group",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="User permissions",
        blank=True,
        related_name="sender_user_permissions",
        related_query_name="sender_user_permission",
    )
