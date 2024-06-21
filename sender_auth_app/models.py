from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField


# Create your models here.
class Sender(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=16)
    password2 = models.CharField(max_length=16)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    photo = models.ImageField(upload_to="", null=True, blank=True)
    photo_url = models.CharField(max_length=5000, null=True, blank=True)

    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "password", "password2"]
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
