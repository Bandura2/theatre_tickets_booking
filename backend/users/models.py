# backend/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Базовий клас користувача.
    Розширює стандартний AbstractUser (додає email, password, username).
    """
    is_client = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)

    # Вирішення конфліктів наслідування Django (формальність)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    def __str__(self):
        return self.username


class Client(User):
    """
    Клас Клієнта (спадкується від User).
    Має додаткові методи для бронювання (будуть у views).
    """
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = "Client"


class Admin(User):
    """
    Клас Адміністратора (спадкується від User).
    """
    department = models.CharField(max_length=50, default="Management")

    class Meta:
        verbose_name = "Administrator"
