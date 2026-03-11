from django.db import models
from django.conf import settings


class Campaign(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Активна'),
        ('PAUSED', 'На паузі'),
        ('COMPLETED', 'Завершена'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns',
                              verbose_name="Власник (Медіабайєр)")
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
        """Автоматичний розрахунок Click-Through Rate"""
        if self.impressions > 0:
            return round((self.clicks / self.impressions) * 100, 2)
        return 0


class AdCreative(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='creatives', verbose_name="Кампанія")
    title = models.CharField(max_length=255, verbose_name="Назва креативу")
    duration = models.IntegerField(verbose_name="Тривалість (сек)", help_text="Наприклад: 15")
    hook = models.CharField(max_length=255, blank=True, null=True, verbose_name="Хук (гачок)")
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Витрачено на креатив ($)")
    roi = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="ROI (%)")
    is_burning_out = models.BooleanField(default=False, verbose_name="Ознаки вигорання (Ad Fatigue)")

    class Meta:
        verbose_name = "Креатив"
        verbose_name_plural = "Креативи"

    def __str__(self):
        return f"{self.title} | {self.campaign.name}"