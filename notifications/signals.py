from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from trading.models import Order
from sales.models import Payment
from notifications.models import Notification

channel_layer = get_channel_layer()

def send_ws_notification(user_id, message):
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {"type": "send_notification", "message": message}
    )

@receiver(post_save, sender=Order)
def notify_trader_on_order(sender, instance, created, **kwargs):
    if created:
        message = f"New order for {instance.product.title} from {instance.user.username}."
        Notification.objects.create(user=instance.product.user, message=message)
        send_ws_notification(instance.product.user.id, message)

@receiver(post_save, sender=Order)
def notify_customer_on_confirmation(sender, instance, **kwargs):
    if instance.status == "confirmed":
        message = f"Your order {instance.id} has been confirmed by the seller."
        Notification.objects.create(user=instance.user, message=message)
        send_ws_notification(instance.user.id, message)

@receiver(post_save, sender=Payment)
def notify_trader_on_payment(sender, instance, **kwargs):
    if instance.status == "succeeded":
        message = f"{instance.sales_order.order.user.username} completed payment for order {instance.sales_order.order.id}."
        Notification.objects.create(user=instance.sales_order.order.product.user, message=message)
        send_ws_notification(instance.sales_order.order.product.user.id, message)