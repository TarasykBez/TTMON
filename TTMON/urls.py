from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('analytics.urls')),
    path('tasks/', include('tasks.urls')),
    path('users/', include('users.urls')),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('policy/', TemplateView.as_view(template_name='pages/policy.html'), name='policy'),
]


# Додаємо роздачу медіафайлів
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)