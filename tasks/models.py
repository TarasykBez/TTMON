from django.db import models
from django.conf import settings
from analytics.models import AdCreative


class Task(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Чернетка'), ('SENT', 'Відправлено'), ('IN_PROGRESS', 'В роботі'),
        ('REVIEW', 'На перевірці'), ('COMPLETED', 'Готово'),
    )

    DURATION_CHOICES = (
        ('UP_TO_10', 'до 10 сек'), ('10_15', '10-15 сек'), ('15_30', '15-30 сек'),
    )

    COMPLEXITY_CHOICES = (
        ('EASY', '🟢 Легка'), ('MEDIUM', '🟡 Середня'), ('HARD', '🔴 Складна'),
    )

    VOICE_CHOICES = (
        ('MALE', 'Чоловічий'), ('FEMALE', 'Жіночий'),
    )

    # Новий словник для мов озвучки
    VO_LANGUAGE_CHOICES = (
        ('UK', 'Українська'), ('EN_US', 'English (US)'), ('EN_UK', 'English (UK)'),
        ('PL', 'Polish'), ('DE', 'German'), ('ES', 'Spanish'), ('FR', 'French'),
        ('IT', 'Italian'), ('PT', 'Portuguese'),
    )

    GEO_CHOICES = (
        ('US', 'United States (ENG)'), ('GB', 'United Kingdom'), ('CA', 'Canada'),
        ('AU', 'Australia'), ('DE', 'Germany'), ('FR', 'France'), ('IT', 'Italy'),
        ('ES', 'Spain'), ('UA', 'Ukraine'), ('PL', 'Poland'), ('BR', 'Brazil'),
        ('MX', 'Mexico'), ('ID', 'Indonesia'), ('TH', 'Thailand'), ('VN', 'Vietnam'),
        ('MY', 'Malaysia'), ('PH', 'Philippines'), ('SA', 'Saudi Arabia'), ('AE', 'UAE'),
    )

    title = models.CharField(max_length=255, verbose_name="Назва ТЗ")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_tasks')
    source_creative = models.ForeignKey(AdCreative, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    deadline = models.DateField(verbose_name="Дедлайн", null=True, blank=True)
    complexity = models.CharField(max_length=10, choices=COMPLEXITY_CHOICES, default='MEDIUM')
    geo = models.CharField(max_length=5, choices=GEO_CHOICES, default='US')
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='15_30')

    description = models.TextField(blank=True, null=True)
    hook = models.TextField(blank=True, null=True)
    main_part = models.TextField(blank=True, null=True)
    cta = models.TextField(blank=True, null=True)

    needs_voiceover = models.BooleanField(default=False)
    voiceover_text = models.TextField(blank=True, null=True)
    # Змінено на CharField з choices
    vo_language = models.CharField(max_length=10, choices=VO_LANGUAGE_CHOICES, blank=True, null=True)
    vo_voice = models.CharField(max_length=10, choices=VOICE_CHOICES, blank=True, null=True)

    reference_links = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creative_comment = models.TextField(verbose_name="Коментар креативника (до результату)", blank=True, null=True)
    buyer_feedback = models.TextField(verbose_name="Правки від баєра", blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} {self.title}"


class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='task_references/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class TaskResultFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='result_files')
    file = models.FileField(upload_to='task_results/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Файл результату"
        verbose_name_plural = "Файли результатів"