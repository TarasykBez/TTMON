import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.conf import settings

from .models import CustomUser, TikTokIntegration
from .forms import UserCreationFormCustom


# ==========================================
# ЛОГІКА КЕРУВАННЯ КОРИСТУВАЧАМИ (АДМІН)
# ==========================================
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

        # ЛОГІКА ВИДАЛЕННЯ КОРИСТУВАЧА
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

    # Відфільтровуємо суперкористувачів (is_superuser=False)
    all_users = CustomUser.objects.filter(is_superuser=False).order_by('-date_joined')

    context = {'form': form, 'users_list': all_users}
    return render(request, 'users/manage_users.html', context)


# Запит на відновлення пароля (для гостей)
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
            update_session_auth_hash(request, user)

            user.has_changed_password = True
            user.temporary_password = ''
            user.save()

            messages.success(request, 'Пароль успішно змінено! Тепер ви можете працювати в системі.')
            return redirect('/')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})


# ==========================================
# ЛОГІКА ІНТЕГРАЦІЇ З TIKTOK API
# ==========================================

@login_required
def buyer_integrations(request):
    """Відображає сторінку з підключеними інтеграціями баєра"""
    tiktok_account = getattr(request.user, 'tiktok_account', None)
    return render(request, 'users/buyer_integrations.html', {
        'tiktok_account': tiktok_account
    })


@login_required
def tiktok_login(request):
    """Формує URL для авторизації і перенаправляє на TikTok"""
    request.session['tiktok_state'] = 'random_string_for_security_123'

    url = "https://www.tiktok.com/v2/auth/authorize/"
    params = {
        'client_key': settings.TIKTOK_CLIENT_KEY,
        'response_type': 'code',
        'scope': 'user.info.basic,video.upload,video.publish,ads.management,ads.stats',
        'redirect_uri': settings.TIKTOK_REDIRECT_URI,
        'state': request.session['tiktok_state'],
    }

    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return redirect(f"{url}?{query_string}")


@login_required
def tiktok_callback(request):
    """Обробляє повернення юзера з TikTok і отримує токен"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')

    if error:
        messages.error(request, f"Помилка авторизації TikTok: {error}")
        return redirect('buyer_integrations')

    if state != request.session.get('tiktok_state'):
        messages.error(request, "Помилка безпеки: недійсний state.")
        return redirect('buyer_integrations')

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_key': settings.TIKTOK_CLIENT_KEY,
        'client_secret': settings.TIKTOK_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.TIKTOK_REDIRECT_URI,
    }

    response = requests.post(token_url, headers=headers, data=data)
    token_data = response.json()

    if 'access_token' in token_data:
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        open_id = token_data['open_id']

        user_info_url = "https://open.tiktokapis.com/v2/user/info/?fields=open_id,display_name,avatar_url"
        info_headers = {'Authorization': f"Bearer {access_token}"}
        info_response = requests.get(user_info_url, headers=info_headers).json()

        display_name = ''
        avatar_url = ''
        if 'data' in info_response and 'user' in info_response['data']:
            user_data = info_response['data']['user']
            display_name = user_data.get('display_name', '')
            avatar_url = user_data.get('avatar_url', '')

        TikTokIntegration.objects.update_or_create(
            user=request.user,
            defaults={
                'open_id': open_id,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'display_name': display_name,
                'avatar_url': avatar_url
            }
        )
        messages.success(request, f"Акаунт TikTok '{display_name}' успішно підключено!")
    else:
        messages.error(request, "Не вдалося отримати токен від TikTok.")

    return redirect('users:buyer_integrations')


@login_required
def tiktok_disconnect(request):
    """Видаляє прив'язку TikTok акаунта"""
    if request.method == 'POST':
        integration = get_object_or_404(TikTokIntegration, user=request.user)
        integration.delete()
        messages.success(request, "Акаунт TikTok успішно відключено.")
    return redirect('users:buyer_integrations')