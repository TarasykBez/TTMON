from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Team, TikTokIntegration


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'created_at')
    search_fields = ('name',)


class CustomUserAdmin(UserAdmin):
    # Додаємо нові поля до списку користувачів
    list_display = ('username', 'email', 'role', 'team', 'is_team_lead', 'is_staff')
    list_filter = ('role', 'team', 'is_team_lead', 'is_staff')

    # Додаємо поля до форми редагування існуючого юзера
    fieldsets = UserAdmin.fieldsets + (
        ('Командна структура', {'fields': ('role', 'team', 'is_team_lead')}),
        ('Безпека (Тимчасові дані)', {'fields': ('temporary_password', 'has_changed_password', 'reset_requested')}),
    )

    # Додаємо поля до форми створення нового юзера
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Додаткова інформація', {'fields': ('role', 'team', 'is_team_lead', 'email')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(TikTokIntegration)