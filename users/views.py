import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.crypto import get_random_string
from django.conf import settings
from django.db import models

from .forms import UserCreationFormCustom
from .models import CustomUser, Team, TikTokIntegration
from analytics.models import TikTokAdAccount


def is_admin(user):
    return user.is_superuser


# ==========================================
# КЕРУВАННЯ КОМАНДОЮ ТА КОРИСТУВАЧАМИ
# ==========================================

@user_passes_test(is_admin, login_url='/login/')
def manage_users(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_user':
            form = UserCreationFormCustom(request.POST)
            if form.is_valid():
                # Правильна розпаковка:
                new_user_data, _ = form.save(commit=False)
                team = new_user_data.team

                if new_user_data.is_team_lead and team.leader:
                    messages.error(request, f"У команди {team.name} вже є тімлід.")
                    all_teams = Team.objects.all().prefetch_related('members')
                    return render(request, 'users/manage_users.html', {'form': form, 'teams': all_teams})

                # Зберігаємо і отримуємо пароль
                user, raw_password = form.save()

                if user.is_team_lead:
                    team.leader = user
                    team.save()

                messages.success(request, f"Користувача {user.username} створено!")
                return redirect('users:manage_users')

        elif action == 'reset_password':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(CustomUser, id=user_id)
            new_password = get_random_string(length=12)
            user.set_password(new_password)
            user.temporary_password = new_password
            user.has_changed_password = False
            user.reset_requested = False
            user.save()
            messages.success(request, f"Пароль для {user.username} оновлено!")
            return redirect('users:manage_users')

        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            user_to_delete = get_object_or_404(CustomUser, id=user_id)
            if user_to_delete.is_team_lead and user_to_delete.team:
                team = user_to_delete.team
                team.leader = None
                team.save()
            user_to_delete.delete()
            messages.success(request, "Користувача видалено.")
            return redirect('users:manage_users')

    form = UserCreationFormCustom()
    all_teams = Team.objects.all().prefetch_related('members', 'members__assigned_creatives')
    context = {'form': form, 'teams': all_teams}
    return render(request, 'users/manage_users.html', context)


@user_passes_test(is_admin)
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        new_is_team_lead = 'is_team_lead' in request.POST
        team_id = request.POST.get('team')
        new_team = Team.objects.get(id=team_id) if team_id else None

        if new_is_team_lead and new_team and new_team.leader and new_team.leader != user_to_edit:
            messages.error(request, f"У команди {new_team.name} вже є тімлід.")
            return redirect('users:manage_users')

        user_to_edit.username = request.POST.get('username')
        user_to_edit.email = request.POST.get('email')
        user_to_edit.role = request.POST.get('role')
        user_to_edit.team = new_team
        user_to_edit.is_team_lead = new_is_team_lead

        # Оновлення зв'язків ManyToMany
        creatives_ids = request.POST.getlist('assigned_creatives')
        if user_to_edit.role == 'media_buyer':
            user_to_edit.assigned_creatives.set(creatives_ids)
        else:
            # Якщо роль змінена на креативника — очищуємо його зв'язки
            user_to_edit.assigned_creatives.clear()

        user_to_edit.save()

        if new_team:
            if user_to_edit.is_team_lead:
                new_team.leader = user_to_edit
            elif new_team.leader == user_to_edit:
                new_team.leader = None
            new_team.save()

        messages.success(request, f"Дані {user_to_edit.username} оновлено.")
    return redirect('users:manage_users')


@user_passes_test(is_admin)
def manage_teams(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_team':
            name = request.POST.get('team_name')
            if name:
                Team.objects.create(name=name)
                messages.success(request, f"Команду '{name}' успішно створено.")
        elif action == 'edit_team':
            team_id = request.POST.get('team_id')
            team = get_object_or_404(Team, id=team_id)
            team.name = request.POST.get('team_name')
            team.save()
            messages.success(request, "Команду оновлено.")
    return redirect('users:manage_users')

# ==========================================
# БЕЗПЕКА ТА ПАРОЛІ
# ==========================================

@login_required
def first_time_password_change(request):
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
            messages.success(request, 'Пароль успішно змінено!')
            return redirect('/')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def request_password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            user.reset_requested = True
            user.save()
            messages.success(request, "Запит надіслано адміністратору.")
            return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, "Користувача не знайдено.")
    return render(request, 'users/request_reset.html')


# ==========================================
# ІНТЕГРАЦІЯ TIKTOK
# ==========================================

@login_required
def buyer_integrations(request):
    # Креативникам тут робити нічого
    if request.user.role == 'creative':
        messages.warning(request, "У вас немає доступу до інтеграцій.")
        return redirect('/tasks/')

    user = request.user

    if user.is_superuser:
        # Адмін керує всім
        main_integrations = TikTokIntegration.objects.all()
        assigned_accounts = TikTokAdAccount.objects.all().select_related('buyer', 'main_integration')
        all_buyers = CustomUser.objects.filter(is_superuser=False, role='media_buyer')
    else:
        # Баєр бачить БЦ, де він власник АБО де він є у списку allowed_buyers
        main_integrations = TikTokIntegration.objects.filter(
            models.Q(user=user) |
            models.Q(allowed_buyers=user)
        ).distinct()

        # Баєр бачить кабінети, які закріплені особисто за ним АБО належать БЦ, до якого є доступ
        assigned_accounts = TikTokAdAccount.objects.filter(
            models.Q(buyer=user) |
            models.Q(main_integration__allowed_buyers=user)
        ).distinct()

        all_buyers = None

    context = {
        'main_integrations': main_integrations,
        'assigned_accounts': assigned_accounts,
        'all_buyers': all_buyers,
        'is_admin': user.is_superuser
    }
    return render(request, 'users/buyer_integrations.html', context)


@user_passes_test(is_admin)
def assign_ad_account(request):
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        buyer_id = request.POST.get('buyer_id')
        account = get_object_or_404(TikTokAdAccount, id=account_id)
        account.buyer = get_object_or_404(CustomUser, id=buyer_id) if buyer_id else None
        account.save()
        messages.success(request, "Баєра призначено.")
    return redirect('users:buyer_integrations')


@login_required
def tiktok_login(request):
    state = get_random_string(16)
    request.session['tiktok_state'] = state
    url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={settings.TIKTOK_CLIENT_KEY}&scope=user.info.basic,video.upload,video.publish,ads.management,ads.stats&response_type=code&redirect_uri={settings.TIKTOK_REDIRECT_URI}&state={state}"
    return redirect(url)


@login_required
def tiktok_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    if state != request.session.get('tiktok_state'):
        messages.error(request, "Security error: invalid state.")
        return redirect('users:buyer_integrations')

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    data = {
        'client_key': settings.TIKTOK_CLIENT_KEY,
        'client_secret': settings.TIKTOK_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.TIKTOK_REDIRECT_URI,
    }
    response = requests.post(token_url, data=data).json()

    if 'access_token' in response:
        TikTokIntegration.objects.update_or_create(
            user=request.user,
            defaults={
                'open_id': response['open_id'],
                'access_token': response['access_token'],
                'refresh_token': response.get('refresh_token', ''),
                'display_name': 'TikTok Account'
            }
        )
        messages.success(request, "TikTok підключено!")
    else:
        messages.error(request, "Помилка отримання токена.")
    return redirect('users:buyer_integrations')


@login_required
def tiktok_disconnect(request):
    if request.method == 'POST':
        integration = get_object_or_404(TikTokIntegration, user=request.user)
        integration.delete()
        messages.success(request, "TikTok відключено.")
    return redirect('users:buyer_integrations')


@user_passes_test(is_admin)
def update_bc_access(request, integration_id):
    if request.method == 'POST':
        integration = get_object_or_404(TikTokIntegration, id=integration_id)
        buyer_ids = request.POST.getlist('buyer_ids')

        # Оновлюємо список дозволених баєрів
        integration.allowed_buyers.set(buyer_ids)
        messages.success(request, f"Доступ до БЦ '{integration.display_name}' оновлено.")

    return redirect('users:buyer_integrations')