from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('manage/', views.manage_users, name='manage_users'),
    path('request-reset/', views.request_password_reset, name='request_reset'),
    # Додаємо маршрут для зміни пароля:
    path('change-password/', views.first_time_password_change, name='change_password'),
]