from django.core.mail import send_mail
from django.conf import settings

def send_task_completion_email(task):
    recipients = [emp.user.email for emp in task.assigned_to.all() if emp.user.email]
    if not recipients:
        return

    subject = f'Task Completed: {task.title}'
    message = f'The task "{task.title}" has been completed.\n\nDescription:\n{task.description}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients)
