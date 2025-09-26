from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import OrderItem, Order, Product

@receiver(post_save, sender=OrderItem)
def update_order_total_on_save(sender, instance, created, **kwargs):
    # If created or updated, recalc total
    instance.order.recalc_total()

@receiver(post_delete, sender=OrderItem)
def update_order_total_on_delete(sender, instance, **kwargs):
    instance.order.recalc_total()
