Handle Notification Signal
==========================

**Signal Name:** `handle_notification_save`

**Description:**

This signal is triggered whenever a `Notification` instance is saved. It is responsible for sending the notification asynchronously and marking the notification as sent if it is relevant and not related to reassignment.

**Actions:**

- Sends the notification using the `send_notification_task` Celery task.
- Marks the notification as sent if it is relevant, meaning it is accepted and not related to reassignment.

**Parameters:**

- `sender` (`Model`): The model class that sent the signal (in this case, `Notification`).

- `instance` (`Notification`): The instance of the model that triggered the signal.

- `**kwargs` (`dict`): Additional keyword arguments.

**Detailed Behavior:**

1. **Asynchronous Notification:**
   - The signal sends the notification asynchronously by calling `send_notification_task.delay()` with the `user.id` and `message` from the notification instance.

2. **Marking as Sent:**
   - If the notification is marked as relevant (`instance.relevant` is `True`) and does not contain "reassign" in its message, it is marked as sent (`Notification.objects.filter(id=instance.id).update(sent=True)`).
   
   - The logic differentiates between notifications intended for vendors and customers, ensuring only relevant notifications are marked as sent.
