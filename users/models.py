from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('media_buyer', 'Медіабайєр'),
        ('creative', 'Креативник'),
    )
    email = models.EmailField('email address', unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='media_buyer')
    supervisor = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'media_buyer'}, related_name='team_members',
        verbose_name="Прив'язаний баєр"
    )
    temporary_password = models.CharField(max_length=50, blank=True, null=True)
    has_changed_password = models.BooleanField(default=False)
    reset_requested = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class TikTokIntegration(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tiktok_account')
    open_id = models.CharField(max_length=255, unique=True, verbose_name="TikTok OpenID")
    access_token = models.TextField()
    refresh_token = models.TextField()
    display_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ім'я в TikTok")
    avatar_url = models.URLField(max_length=1000, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TikTok Account: {self.display_name} (User: {self.user.username})"