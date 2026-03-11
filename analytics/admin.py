from django.contrib import admin
from .models import Campaign, AdCreative

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'budget', 'spend', 'get_ctr')
    list_filter = ('status', 'owner')
    search_fields = ('name',)

    def get_ctr(self, obj):
        return f"{obj.ctr}%"
    get_ctr.short_description = 'CTR'

@admin.register(AdCreative)
class AdCreativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign', 'duration', 'spend', 'roi', 'is_burning_out')
    list_filter = ('is_burning_out', 'campaign')
    search_fields = ('title', 'hook')