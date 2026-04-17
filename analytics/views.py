from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Campaign, TikTokAdAccount
from users.models import TikTokIntegration

@login_required
def dashboard(request):
    # Обмеження для креативника
    if request.user.role == 'creative':
        messages.warning(request, "У вас немає доступу до розділу аналітики.")
        return redirect('/tasks/')

    # Відображаємо кампанії конкретного користувача (баєра)
    # Якщо адмін - показуємо все, якщо баєр - тільки його
    if request.user.is_superuser:
        campaigns = Campaign.objects.all().order_by('-created_at')
    else:
        campaigns = Campaign.objects.filter(owner=request.user).order_by('-created_at')

    context = {
        'campaigns': campaigns
    }
    return render(request, 'analytics/dashboard.html', context)