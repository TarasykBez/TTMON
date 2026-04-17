from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Додаємо поле 'role' до відображення в адмінці
    list_display = ('username', 'email', 'role', 'is_staff')

    # Додаємо поле 'role' до форми редагування
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Додаткова інформація', {'fields': ('role', 'email')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)

