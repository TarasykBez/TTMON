from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Робимо наш дашборд головною сторінкою всього сайту:
    path('', include('analytics.urls')), 
]