from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Campaign, TikTokAdAccount
from users.models import TikTokIntegration


@login_required
def dashboard(request):
    # 0. ПЕРЕВІРКА НА ПЕРШИЙ ВХІД (Зміна пароля)
    if not request.user.has_changed_password and not request.user.is_superuser:
        return redirect('users:first_time_password_change')

    # 1. Обмеження для креативника
    if request.user.role == 'creative':
        messages.warning(request, "У вас немає доступу до розділу аналітики.")
        return redirect('/tasks/')

    user = request.user

    # 2. Фільтрація кампаній залежно від ролі (ПОВЕРНУТО БЕЗПЕЧНУ ЛОГІКУ)
    if user.is_superuser:
        # Суперюзер бачить абсолютно всі кампанії
        campaigns = Campaign.objects.all().order_by('-created_at')

    elif user.is_team_lead and user.team:
        # Тімлід бачить кампанії всіх учасників своєї команди
        campaigns = Campaign.objects.filter(owner__team=user.team).order_by('-created_at')

    else:
        # Звичайний баєр бачить тільки свої кампанії
        campaigns = Campaign.objects.filter(owner=user).order_by('-created_at')

    # 3. Додаткова статистика для контексту
    context = {
        'campaigns': campaigns,
        'is_team_view': user.is_team_lead or user.is_superuser,
        'team_name': user.team.name if user.team else "Особистий кабінет"
    }
    return render(request, 'analytics/dashboard.html', context)