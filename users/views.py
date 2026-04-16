from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import CustomUser
from .forms import UserCreationFormCustom
from django.utils.crypto import get_random_string
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin, login_url='/login/')
def manage_users(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        # ЛОГІКА СТВОРЕННЯ КОРИСТУВАЧА
        if action == 'create_user':
            form = UserCreationFormCustom(request.POST)
            if form.is_valid():
                new_user, raw_password = form.save()
                messages.success(request, f"Користувача {new_user.email} успішно створено!")
                return redirect('users:manage_users')
            else:
                messages.error(request, "Помилка при створенні користувача.")

        # ЛОГІКА СКИДАННЯ ПАРОЛЯ АДМІНОМ
        elif action == 'reset_password':
            user_id = request.POST.get('user_id')
            user = CustomUser.objects.get(id=user_id)
            new_password = get_random_string(length=12)

            user.set_password(new_password)
            user.temporary_password = new_password
            user.has_changed_password = False
            user.reset_requested = False
            user.save()

            messages.success(request, f"Новий тимчасовий пароль для {user.username} згенеровано!")
            return redirect('users:manage_users')

        # НОВА ЛОГІКА: ВИДАЛЕННЯ КОРИСТУВАЧА
        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            try:
                user_to_delete = CustomUser.objects.get(id=user_id)
                username_deleted = user_to_delete.username
                user_to_delete.delete()
                messages.success(request, f"Користувача {username_deleted} успішно видалено з системи.")
            except CustomUser.DoesNotExist:
                messages.error(request, "Помилка: Користувача не знайдено.")
            return redirect('users:manage_users')

    else:
        form = UserCreationFormCustom()

    # ЗМІНЕНО: Відфільтровуємо суперкористувачів (is_superuser=False), щоб адмін не світився в таблиці
    all_users = CustomUser.objects.filter(is_superuser=False).order_by('-date_joined')

    context = {'form': form, 'users_list': all_users}
    return render(request, 'users/manage_users.html', context)


# НОВА ФУНКЦІЯ: Запит на відновлення пароля (для гостей)
def request_password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            user.reset_requested = True
            user.save()
            messages.success(request, "Запит успішно надіслано адміністратору. Зачекайте на новий пароль.")
            return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, "Користувача з таким логіном не знайдено.")

    return render(request, 'users/request_reset.html')


@login_required
def first_time_password_change(request):
    # Якщо пароль вже змінено, пускаємо на головну
    if request.user.has_changed_password and not request.user.is_superuser:
        return redirect('/')

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Важливо: оновлюємо сесію, щоб користувача не "викинуло" після зміни пароля
            update_session_auth_hash(request, user)

            # Оновлюємо статуси
            user.has_changed_password = True
            user.temporary_password = ''  # Затираємо тимчасовий пароль з бази
            user.save()

            messages.success(request, 'Пароль успішно змінено! Тепер ви можете працювати в системі.')
            return redirect('/')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})