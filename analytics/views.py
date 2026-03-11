from django.shortcuts import render
from .models import Campaign


def dashboard(request):
    # Дістаємо всі кампанії з бази даних
    # Пізніше ми налаштуємо так, щоб кожен бачив лише СВОЇ кампанії
    campaigns = Campaign.objects.all().order_by('-created_at')

    context = {
        'campaigns': campaigns
    }
    return render(request, 'analytics/dashboard.html', context)