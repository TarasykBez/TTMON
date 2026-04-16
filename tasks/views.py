from django.shortcuts import render
from .models import Task
from django.contrib.auth.decorators import login_required

@login_required
def task_list(request):
    # Отримуємо всі ТЗ, сортуючи від найновіших до найстаріших
    tasks = Task.objects.all().order_by('-created_at')

    context = {
        'tasks': tasks
    }
    return render(request, 'tasks/task_list.html', context)

@login_required
def task_list(request):
    user = request.user
    if user.role == 'media_buyer':
        # Баєр бачить свої ТЗ
        tasks = Task.objects.filter(author=user)
    else:
        # Креативник бачить ТЗ свого баєра або ті, де він виконавець
        tasks = Task.objects.filter(models.Q(author=user.supervisor) | models.Q(assignee=user))

    return render(request, 'tasks/task_list.html', {'tasks': tasks})