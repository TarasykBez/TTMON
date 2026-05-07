from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Campaign, AdCreative, TikTokAdAccount
from users.models import Team, CustomUser
from tasks.models import Task


def home_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'creative':
            return redirect('/tasks/')
        return redirect('analytics:dashboard')
    return render(request, 'index.html')

@login_required
def dashboard(request):
    user = request.user
    kiev_now = timezone.now() + timedelta(hours=3)
    today_kiev = kiev_now.date()

    # 1. ОБМЕЖЕННЯ СПИСКУ БАЄРІВ ДЛЯ ФІЛЬТРУ (RBAC)
    if user.is_superuser:
        available_buyers = CustomUser.objects.filter(role='media_buyer')
    elif user.is_team_lead:
        # Тімлід бачить тільки баєрів своєї команди
        available_buyers = CustomUser.objects.filter(team=user.team, role='media_buyer')
    else:
        # Баєр бачить тільки себе
        available_buyers = CustomUser.objects.filter(id=user.id)

    # 2. ПОЧАТКОВИЙ QUERYSET КАМПАНІЙ
    queryset = Campaign.objects.all().prefetch_related('creatives')
    if not user.is_superuser:
        if user.is_team_lead:
            queryset = queryset.filter(owner__team=user.team)
        else:
            queryset = queryset.filter(owner=user)

    # 3. ФІЛЬТРАЦІЯ ДАТ
    date_range = request.GET.get('date_range')
    if date_range:
        if " to " in date_range:
            start_str, end_str = date_range.split(" to ")
            queryset = queryset.filter(created_at__date__range=[start_str, end_str])
        else:
            queryset = queryset.filter(created_at__date=date_range)
    else:
        queryset = queryset.filter(
            Q(status='ACTIVE') |
            Q(status='PAUSED', pause_date=today_kiev) |
            Q(status='COMPLETED', end_date=today_kiev)
        )
        date_range = today_kiev.strftime('%Y-%m-%d')

    # 4. МУЛЬТИ-ФІЛЬТРАЦІЯ
    selected_geos = request.GET.getlist('geos')
    selected_buyers = request.GET.getlist('buyers')
    selected_teams = request.GET.getlist('teams')

    if selected_geos: queryset = queryset.filter(geo__in=selected_geos)
    if selected_buyers: queryset = queryset.filter(owner_id__in=selected_buyers)
    if selected_teams and user.is_superuser: queryset = queryset.filter(owner__team_id__in=selected_teams)

    # 5. СТАТИСТИКА (6 ВІДЖЕТІВ)
    selected_campaign_ids = request.GET.getlist('selected_campaigns')
    stats_queryset = queryset.filter(id__in=selected_campaign_ids) if selected_campaign_ids else queryset

    stats = {
        'total_spend': stats_queryset.aggregate(Sum('spend'))['spend__sum'] or 0,
        'active_campaigns': stats_queryset.filter(status='ACTIVE').count(),
        'burning_campaigns': AdCreative.objects.filter(campaign__in=stats_queryset, is_burning_out=True).values('campaign').distinct().count(),
        'top_creative': AdCreative.objects.filter(campaign__in=stats_queryset).order_by('-roi').first(),
        'top_buyer': CustomUser.objects.filter(id__in=stats_queryset.values('owner')).annotate(total_conv=Sum('campaigns__conversions')).order_by('-total_conv').first(),
        'avg_roi': AdCreative.objects.filter(campaign__in=stats_queryset).aggregate(Avg('roi'))['roi__avg'] or 0
    }

    context = {
        'stats': stats,
        'campaigns': queryset.order_by('-created_at'),
        'teams': Team.objects.all() if user.is_superuser else None,
        'team_members': available_buyers, # Тільки дозволені баєри
        'geo_choices': [c[0] for c in Task.GEO_CHOICES],
        'selected_ids': [int(i) for i in selected_campaign_ids],
        'selected_geos': selected_geos,
        'selected_buyers': selected_buyers,
        'selected_teams': selected_teams,
        'current_date_range': date_range
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    if not request.user.is_superuser and campaign.owner != request.user:
        if not (request.user.is_team_lead and campaign.owner.team == request.user.team):
            return redirect('analytics:dashboard')
    return render(request, 'analytics/campaign_detail.html', {'campaign': campaign})