from django.shortcuts import render
from .models import Task


def task_list(request):
    # Отримуємо всі ТЗ, сортуючи від найновіших до найстаріших
    tasks = Task.objects.all().order_by('-created_at')

    context = {
        'tasks': tasks
    }
    return render(request, 'tasks/task_list.html', context)