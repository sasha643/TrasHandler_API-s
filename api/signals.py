from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from .models import Notification
from .tasks import send_notification_task

# @receiver(post_save, sender=Notification)
# def handle_notification_save(sender, instance, **kwargs):
#     async_to_sync(notify_user)(instance)

#     # Mark the notification as read if it is relevant and not for reassignment
#     if instance.relevant:
#         if instance.recipient_type == 'vendor' and 'reassign' not in instance.message.lower():
#             Notification.objects.filter(id=instance.id).update(sent=True)
#         elif instance.recipient_type == 'customer' and 'reassign' not in instance.message.lower():
#             Notification.objects.filter(id=instance.id).update(sent=True)

# async def notify_user(notification):
#     await send_notification(notification.user.id, notification.message)

# @receiver(post_save, sender=Notification)
# def handle_notification_save(sender, instance, **kwargs):
#     # Notify the user when a Notification instance is saved
#     notify_user(instance)

#     # Mark the notification as sent if it is relevant and not for reassignment
#     if instance.relevant:
#         if instance.recipient_type == 'vendor' and 'reassign' not in instance.message.lower():
#             Notification.objects.filter(id=instance.id).update(sent=True)
#         elif instance.recipient_type == 'customer' and 'reassign' not in instance.message.lower():
#             Notification.objects.filter(id=instance.id).update(sent=True)

# def notify_user(notification):
#     send_notification.delay(notification.user.id, notification.message)

@receiver(post_save, sender=Notification)
def handle_notification_save(sender, instance, **kwargs):
    send_notification_task.delay(instance.user.id, instance.message)

    # Mark the notification as read if it is relevant and not for reassignment
    if instance.relevant:
        if instance.recipient_type == 'vendor' and 'reassign' not in instance.message.lower():
            Notification.objects.filter(id=instance.id).update(sent=True)
        elif instance.recipient_type == 'customer' and 'reassign' not in instance.message.lower():
            Notification.objects.filter(id=instance.id).update(sent=True)