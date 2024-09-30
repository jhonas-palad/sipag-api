from .utils import send_expo_notifcation
from celery import shared_task
from .models import PushToken
from django.contrib.auth import get_user_model


User = get_user_model()


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
@shared_task(name="send_push_message")
def send_push_message(to, message, extra=None):
    user = User.objects.get(pk=to)
    user_push_token = PushToken.objects.filter(user=user, active=True).values_list(
        "token", flat=True
    )
    if user_push_token.exists():
        send_expo_notifcation(user_push_token, message, extra=extra)


@shared_task(name="send_push_messages")
def send_push_messages(message, extra=None):
    all_push_token = PushToken.objects.filter(active=True).values_list(
        "token", flat=True
    )
    if all_push_token.exists():
        send_expo_notifcation(all_push_token, message, extra=extra)


# send_push_message("ExponentPushToken[J3MmyWB--IFUU5ZIMYY3uV]", "HELLOOOO")
