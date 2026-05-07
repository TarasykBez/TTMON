from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Порожній шлях '' означає, що це буде головна сторінка додатку
    path('', views.dashboard, name='dashboard'),
    path('campaign/<int:pk>/', views.campaign_detail, name='campaign_detail'),
]