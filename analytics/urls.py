from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Порожній шлях '' означає, що це буде головна сторінка додатку
    path('', views.dashboard, name='dashboard'),
]