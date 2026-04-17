from django.contrib import admin
from .models import TikTokAdAccount, Campaign, AdCreative

# Реєстрація через декоратор (це перший раз)
@admin.register(TikTokAdAccount)
class TikTokAdAccountAdmin(admin.ModelAdmin):
    list_display = ('advertiser_name', 'advertiser_id', 'buyer', 'status')
    list_editable = ('buyer',)
    search_fields = ('advertiser_name', 'advertiser_id')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'budget', 'spend', 'ctr')
    list_filter = ('status', 'owner')

@admin.register(AdCreative)
class AdCreativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign', 'spend', 'roi')