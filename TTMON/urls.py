from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analytics.urls')), # Наш дашборд (головна сторінка)
    path('tasks/', include('tasks.urls')), # Додаємо маршрут для ТЗ
]