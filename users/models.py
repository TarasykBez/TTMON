from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Визначаємо доступні ролі
    ROLE_CHOICES = (
        ('media_buyer', 'Медіабайєр'),
        ('creative', 'Креативник'),
    )

    # Робимо email унікальним обов'язковим полем
    email = models.EmailField('email address', unique=True)

    # Додаємо поле ролі
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='media_buyer',
        verbose_name='Роль користувача'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"