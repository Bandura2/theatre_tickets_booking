from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True)


class Client(User):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    class Meta: verbose_name = "Client"


class Admin(User):
    department = models.CharField(max_length=50, default="Management")

    class Meta: verbose_name = "Administrator"
