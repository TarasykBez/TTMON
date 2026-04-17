from django.urls import path
from . import views

# Вказуємо простір імен для цього додатку
app_name = 'users'

urlpatterns = [
    # Твої основні маршрути
    path('manage/', views.manage_users, name='manage_users'),
    path('password/first-time/', views.first_time_password_change, name='first_time_password_change'),
    path('password/reset/', views.request_password_reset, name='request_password_reset'),

    # МАРШРУТИ ДЛЯ TIKTOK
    path('integrations/', views.buyer_integrations, name='buyer_integrations'),
    path('tiktok/login/', views.tiktok_login, name='tiktok_login'),
    path('tiktok/callback/', views.tiktok_callback, name='tiktok_callback'),
    path('tiktok/disconnect/', views.tiktok_disconnect, name='tiktok_disconnect'),
]