from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва команди")
    leader = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_team',
        verbose_name="Тімлід"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('media_buyer', 'Медіабайєр'),
        ('creative', 'Креативник'),
    )
    email = models.EmailField('email address', unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='media_buyer')

    # Many-to-Many зв'язок: один баєр може мати багато креативників, і навпаки
    assigned_creatives = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='assigned_buyers',
        limit_choices_to={'role': 'creative'},
        blank=True,
        verbose_name="Призначені креативники"
    )

    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members',
                             verbose_name="Команда")
    is_team_lead = models.BooleanField(default=False, verbose_name="Статус Тімліда")

    temporary_password = models.CharField(max_length=50, blank=True, null=True)
    has_changed_password = models.BooleanField(default=False)
    reset_requested = models.BooleanField(default=False)

    def __str__(self):
        prefix = "[TL] " if self.is_team_lead else ""
        return f"{prefix}{self.username} ({self.get_role_display()})"

class TikTokIntegration(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tiktok_account')
    # Хто саме (крім власника) може бачити дані цього БЦ
    allowed_buyers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='shared_bc_integrations',
        verbose_name="Дозволені баєри"
    )
    open_id = models.CharField(max_length=255, unique=True, verbose_name="TikTok OpenID")
    access_token = models.TextField()
    refresh_token = models.TextField()
    display_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ім'я в TikTok")
    avatar_url = models.URLField(max_length=1000, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TikTok Account: {self.display_name} (User: {self.user.username})"