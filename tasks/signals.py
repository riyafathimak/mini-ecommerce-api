# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from .utils import send_task_completion_email

@receiver(post_save, sender=Task)
def task_completed_email(sender, instance, **kwargs):
    if instance.status == 'completed' and not instance.email_sent:
        send_task_completion_email(instance)
        instance.email_sent = True
        instance.save()
