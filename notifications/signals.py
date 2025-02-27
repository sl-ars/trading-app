from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from trading.models import Order, Transaction
from sales.models import Payment, Invoice
from notifications.models import Notification

channel_layer = get_channel_layer()

def send_ws_notification(user_id, message):
    """ Sends WebSocket notification to a user group """
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
def notify_customer_on_approval(sender, instance, **kwargs):
    if instance.status == "approved":
        message = f"Your order {instance.id} has been approved by the seller."
        Notification.objects.create(user=instance.user, message=message)
        send_ws_notification(instance.user.id, message)

@receiver(post_save, sender=Order)
def notify_customer_on_rejection(sender, instance, **kwargs):
    if instance.status == "rejected":
        message = f"Your order {instance.id} has been rejected by the seller."
        Notification.objects.create(user=instance.user, message=message)
        send_ws_notification(instance.user.id, message)

@receiver(post_save, sender=Payment)
def notify_trader_on_payment(sender, instance, **kwargs):
    if instance.status == "paid":
        message = f"{instance.sales_order.order.user.username} completed payment for order {instance.sales_order.order.id}."
        Notification.objects.create(user=instance.sales_order.order.product.user, message=message)
        send_ws_notification(instance.sales_order.order.product.user.id, message)

@receiver(post_save, sender=Order)
def notify_customer_on_shipment(sender, instance, **kwargs):
    if instance.status == "shipped":
        message = f"Your order {instance.id} has been shipped."
        Notification.objects.create(user=instance.user, message=message)
        send_ws_notification(instance.user.id, message)

@receiver(post_save, sender=Invoice)
def notify_customer_on_invoice(sender, instance, **kwargs):
    if instance.pdf_file:
        message = f"Invoice for your order {instance.sales_order.order.id} is now available."
        Notification.objects.create(user=instance.sales_order.order.user, message=message)
        send_ws_notification(instance.sales_order.order.user.id, message)

@receiver(pre_delete, sender=Order)
def notify_trader_on_cancellation(sender, instance, **kwargs):
    if instance.status in ["pending", "approved"]:
        message = f"Order {instance.id} has been cancelled by {instance.user.username}."
        Notification.objects.create(user=instance.product.user, message=message)
        send_ws_notification(instance.product.user.id, message)

@receiver(post_save, sender=Transaction)
def notify_customer_on_trader_cancellation(sender, instance, **kwargs):
    if instance.status_to == "canceled" and instance.order.product.user == instance.user:
        message = f"Your order {instance.order.id} has been cancelled by the trader."
        Notification.objects.create(user=instance.order.user, message=message)
        send_ws_notification(instance.order.user.id, message)