import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView
from analytics.views import home_view  # Імпортуємо нашу нову розумну функцію

urlpatterns = [
    path('admin/', admin.site.urls),

    # Авторизація
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Модулі системи
    path('analytics/', include('analytics.urls')),
    path('tasks/', include('tasks.urls')),
    path('users/', include('users.urls')),

    # Юридичні сторінки
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('policy/', TemplateView.as_view(template_name='pages/policy.html'), name='policy'),

    # Головна сторінка: Розумний редірект (Лендинг або Робоча зона)
    path('', home_view, name='landing'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += static('/images/', document_root=os.path.join(settings.BASE_DIR, 'images'))