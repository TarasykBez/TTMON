from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'assignee', 'status', 'created_at')
    list_filter = ('status', 'author', 'assignee')
    search_fields = ('title', 'concept')

    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'author', 'assignee', 'source_creative', 'status')
        }),
        ('Структура ТЗ', {
            'fields': ('concept', 'hook', 'main_part', 'cta')
        }),
    )