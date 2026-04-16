from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('media_buyer', 'Медіабайєр'),
        ('creative', 'Креативник'),
    )

    email = models.EmailField('email address', unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='media_buyer')


    # Ось це поле має обов'язково бути тут:
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'media_buyer'},
        related_name='team_members',
        verbose_name="Прив'язаний баєр"
    )

    temporary_password = models.CharField(max_length=50, blank=True, null=True, verbose_name="Тимчасовий пароль")
    has_changed_password = models.BooleanField(default=False, verbose_name="Пароль змінено")
    reset_requested = models.BooleanField(default=False, verbose_name="Запит на скидання пароля")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"