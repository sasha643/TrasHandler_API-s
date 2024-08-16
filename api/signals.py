from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from .models import Notification, CustomerAuth, VendorAuth
from .tasks import send_notification_task
import secrets





@receiver(post_save, sender=Notification)
def handle_notification_save(sender, instance, **kwargs):
    send_notification_task.delay(instance.user.id, instance.message)

    # # Mark the notification as read if it is relevant and not for reassignment
    # if instance.relevant:
    #     if instance.recipient_type == 'vendor' and 'reassign' not in instance.message.lower():
    #         Notification.objects.filter(id=instance.id).update(sent=True)
    #     elif instance.recipient_type == 'customer' and 'reassign' not in instance.message.lower():
    #         Notification.objects.filter(id=instance.id).update(sent=True)


@receiver(post_save, sender=CustomerAuth)
def generate_customer_token(sender, instance, created, **kwargs):
    if created and not instance.token:
        instance.token = secrets.token_urlsafe(32)
        instance.save()

@receiver(post_save, sender=VendorAuth)
def generate_vendor_token(sender, instance, created, **kwargs):
    if created and not instance.token:
        instance.token = secrets.token_urlsafe(32)
        instance.save()
