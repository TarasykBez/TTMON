from django.db import models
from django.conf import settings
from users.models import TikTokIntegration # Імпортуємо для зв'язку

class TikTokAdAccount(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_ad_accounts',
        verbose_name="Баєр"
    )
    advertiser_id = models.CharField(max_length=100, unique=True, verbose_name="Advertiser ID")
    advertiser_name = models.CharField(max_length=255, verbose_name="Назва кабінету")
    timezone = models.CharField(max_length=50, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=50, default="ENABLE")
    main_integration = models.ForeignKey(
        TikTokIntegration,
        on_delete=models.CASCADE,
        related_name='managed_ad_accounts'
    )

    class Meta:
        verbose_name = "Рекламний акаунт TikTok"
        verbose_name_plural = "Рекламні акаунти TikTok"

    def __str__(self):
        return f"{self.advertiser_name} ({self.advertiser_id})"

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Активна'),
        ('PAUSED', 'На паузі'),
        ('COMPLETED', 'Завершена'),
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns', verbose_name="Власник (Медіабайєр)")
    name = models.CharField(max_length=255, verbose_name="Назва кампанії")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name="Статус")
    budget = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Бюджет ($)")
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Витрачено ($)")
    impressions = models.IntegerField(default=0, verbose_name="Покази")
    clicks = models.IntegerField(default=0, verbose_name="Кліки")
    conversions = models.IntegerField(default=0, verbose_name="Конверсії")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Рекламна кампанія"
        verbose_name_plural = "Рекламні кампанії"

    def __str__(self):
        return self.name

    @property
    def ctr(self):
        if self.impressions > 0:
            return round((self.clicks / self.impressions) * 100, 2)
        return 0

class AdCreative(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='creatives', verbose_name="Кампанія")
    title = models.CharField(max_length=255, verbose_name="Назва креативу")
    duration = models.IntegerField(verbose_name="Тривалість (сек)")
    hook = models.CharField(max_length=255, blank=True, null=True, verbose_name="Хук")
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Витрачено на креатив ($)")
    roi = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="ROI (%)")
    is_burning_out = models.BooleanField(default=False, verbose_name="Ознаки вигорання")

    class Meta:
        verbose_name = "Креатив"
        verbose_name_plural = "Креативи"