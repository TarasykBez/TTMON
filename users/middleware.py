from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Перевіряємо: чи авторизований, чи НЕ адмін, і чи НЕ змінював пароль
        if user.is_authenticated and not user.is_superuser:
            if not user.has_changed_password:
                # Використовуємо правильну назву маршруту з урахуванням namespace 'users'
                change_password_url = reverse('users:first_time_password_change')
                logout_url = reverse('logout')

                # Дозволяємо доступ тільки до сторінки зміни пароля та сторінки виходу
                allowed_paths = [change_password_url, logout_url]

                if request.path not in allowed_paths:
                    return redirect(change_password_url)

        return self.get_response(request)