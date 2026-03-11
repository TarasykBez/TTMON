from django.db import models
from django.conf import settings
from analytics.models import AdCreative


class Task(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Чернетка'),
        ('SENT', 'Відправлено кріейтору'),
        ('IN_PROGRESS', 'В роботі'),
        ('REVIEW', 'На перевірці'),
        ('COMPLETED', 'Готово'),
    )

    title = models.CharField(max_length=255, verbose_name="Назва ТЗ")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks',
                               verbose_name="Автор (Медіабайєр)")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_tasks', verbose_name="Виконавець (Кріейтор)")
    source_creative = models.ForeignKey(AdCreative, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='generated_tasks', verbose_name="Джерело (Успішний креатив)")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name="Статус")

    # Структура ТЗ
    concept = models.TextField(verbose_name="1. Загальна концепція", help_text="Опишіть основну ідею відео")
    hook = models.TextField(verbose_name="2. Хук (Гачок)", help_text="Що має зачепити увагу в перші 3 секунди?")
    main_part = models.TextField(verbose_name="3. Основна частина", help_text="Сценарій та ключові тези")
    cta = models.TextField(verbose_name="4. Call to Action (Заклик до дії)",
                           help_text="Що користувач має зробити в кінці?")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        verbose_name = "Технічне завдання (ТЗ)"
        verbose_name_plural = "Технічні завдання (ТЗ)"

    def __str__(self):
        return f"ТЗ: {self.title} [{self.get_status_display()}]"