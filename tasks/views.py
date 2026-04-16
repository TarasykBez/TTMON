from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404

from users.models import CustomUser
from .models import Task, TaskFile, TaskResultFile


@login_required
def task_list(request):
    user = request.user

    # ЛОГІКА ДОСТУПУ
    if user.is_superuser:
        # 1. Адмін бачить АБСОЛЮТНО ВСІ завдання
        tasks = Task.objects.all()
    elif user.role == 'media_buyer':
        # 2. Баєр бачить свої
        tasks = Task.objects.filter(author=user)
    else:
        # 3. Креативник бачить ТЗ свого супервізора (баєра) або ті, де він виконавець
        tasks = Task.objects.filter(models.Q(author=user.supervisor) | models.Q(assignee=user))

    return render(request, 'tasks/task_list.html', {'tasks': tasks})


# Спільна функція для збереження даних (Create / Edit)
def _save_task_data(request, task=None):
    title = request.POST.get('title')
    deadline = request.POST.get('deadline')
    geo = request.POST.get('geo')
    duration = request.POST.get('duration')
    complexity = request.POST.get('complexity')
    description = request.POST.get('description')
    hook = request.POST.get('hook')
    main_part = request.POST.get('main_part')
    cta = request.POST.get('cta')
    reference_links = request.POST.get('reference_links')
    assignee_id = request.POST.get('assignee')

    needs_vo = request.POST.get('needs_voiceover') == 'on'
    vo_text = request.POST.get('voiceover_text') if needs_vo else ''
    vo_lang = request.POST.get('vo_language') if needs_vo else ''
    vo_voice = request.POST.get('vo_voice') if needs_vo else ''

    assignee = CustomUser.objects.filter(id=assignee_id).first() if assignee_id else None

    if not task:
        task = Task(author=request.user)

    task.title = title
    task.deadline = deadline if deadline else None
    task.geo = geo
    task.duration = duration
    task.complexity = complexity
    task.description = description
    task.hook = hook
    task.main_part = main_part
    task.cta = cta
    task.reference_links = reference_links
    task.needs_voiceover = needs_vo
    task.voiceover_text = vo_text
    task.vo_language = vo_lang
    task.vo_voice = vo_voice
    task.assignee = assignee

    if task.status == 'DRAFT' and assignee:
        task.status = 'SENT'
    elif not assignee and task.status == 'SENT':
        task.status = 'DRAFT'

    task.save()

    # 1. Видалення існуючих файлів, які баєр видалив з форми
    deleted_files_str = request.POST.get('deleted_existing_files', '')
    if deleted_files_str and task.id:
        deleted_ids = [int(i) for i in deleted_files_str.split(',') if i.isdigit()]
        TaskFile.objects.filter(id__in=deleted_ids, task=task).delete()

    # 2. Обробка нових доданих файлів (ліміт: 10 в сумі)
    files = request.FILES.getlist('reference_files')
    current_files_count = task.files.count() if task.id else 0
    allowed_new_files = 10 - current_files_count

    for f in files[:allowed_new_files]:
        TaskFile.objects.create(task=task, file=f)

    return task


@login_required
def create_task(request):
    if request.user.role == 'creative':
        return redirect('tasks:task_list')

    if request.method == 'POST':
        task = _save_task_data(request)
        messages.success(request, f"ТЗ '{task.title}' успішно створено!")
        return redirect('tasks:task_list')

    creatives = CustomUser.objects.filter(role='creative', supervisor=request.user)

    return render(request, 'tasks/create_task.html', {
        'creatives': creatives,
        'geo_choices': Task.GEO_CHOICES,
        'duration_choices': Task.DURATION_CHOICES,
        'complexity_choices': Task.COMPLEXITY_CHOICES,
        'vo_language_choices': Task.VO_LANGUAGE_CHOICES,
    })


@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.author != request.user and not request.user.is_superuser:
        return redirect('tasks:task_list')

    if request.method == 'POST':
        _save_task_data(request, task)
        messages.success(request, "ТЗ успішно оновлено!")
        return redirect('tasks:task_list')

    creatives = CustomUser.objects.filter(role='creative', supervisor=request.user)

    return render(request, 'tasks/create_task.html', {
        'task': task,
        'creatives': creatives,
        'geo_choices': Task.GEO_CHOICES,
        'duration_choices': Task.DURATION_CHOICES,
        'complexity_choices': Task.COMPLEXITY_CHOICES,
        'vo_language_choices': Task.VO_LANGUAGE_CHOICES,
    })


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.author == request.user or request.user.is_superuser:
        task.delete()
        messages.success(request, "ТЗ видалено.")
    return redirect('tasks:task_list')


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Перевірка доступу
    if task.author != request.user and task.assignee != request.user and task.author != request.user.supervisor and not request.user.is_superuser:
        messages.error(request, "У вас немає доступу до цього завдання.")
        return redirect('tasks:task_list')

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. КРЕАТИВНИК ЗДАЄ РОБОТУ
        if action == 'submit_result':
            task.creative_comment = request.POST.get('creative_comment')
            task.status = 'REVIEW'
            task.save()

            files = request.FILES.getlist('result_files')
            for f in files:
                TaskResultFile.objects.create(task=task, file=f)
            messages.success(request, "Результат успішно відправлено на перевірку баєру!")

        # 2. БАЄР ПЕРЕВІРЯЄ РОБОТУ
        elif action == 'review_result':
            decision = request.POST.get('decision')
            if decision == 'approve':
                task.status = 'COMPLETED'
                task.buyer_feedback = ''  # Очищаємо правки, якщо все ок
                task.save()
                messages.success(request, "ТЗ успішно прийнято! Воно переведено в статус 'Готово'.")
            elif decision == 'reject':
                task.status = 'IN_PROGRESS'
                task.buyer_feedback = request.POST.get('buyer_feedback')
                task.save()
                messages.warning(request, "ТЗ повернуто на доопрацювання з правками.")

        # 3. ПРОСТА ЗМІНА СТАТУСУ (вручну)
        elif action == 'change_status':
            new_status = request.POST.get('status')
            if new_status in dict(Task.STATUS_CHOICES).keys():
                task.status = new_status
                task.save()
                messages.success(request, f"Статус змінено на '{task.get_status_display()}'")

        return redirect('tasks:task_detail', pk=task.id)

    return render(request, 'tasks/task_detail.html', {'task': task})