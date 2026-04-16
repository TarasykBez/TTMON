from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Список завдань
    path('', views.task_list, name='task_list'),

    # Створення ТЗ
    path('create/', views.create_task, name='create_task'),

    # НОВИЙ МАРШРУТ: Деталі ТЗ (саме його шукав Django!)
    path('<int:pk>/', views.task_detail, name='task_detail'),

    # Редагування ТЗ
    path('edit/<int:pk>/', views.edit_task, name='edit_task'),

    # Видалення ТЗ
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
]