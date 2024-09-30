from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
import os
import requests
from django.conf import settings
from requests.exceptions import ConnectionError, HTTPError
from .models import PushToken

# Optionally providing an access token within a session if you have enabled push security
session = requests.Session()

session.headers.update(
    {
        "Authorization": f"Bearer {settings.EXPO_TOKEN}",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)


def send_expo_notifcation(tokens, message, extra=None):
    if tokens and (not hasattr(tokens, "__iter__")):
        tokens = [tokens]

    try:
        push_messages = []
        for token in tokens:
            push_messages.append(PushMessage(to=token, body=message, data=extra))

        responses = PushClient(session=session).publish_multiple(push_messages)
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        # rollbar.report_exc_info(
        #     extra_data={
        #         'token': token,
        #         'message': message,
        #         'extra': extra,
        #         'errors': exc.errors,
        #         'response_data': exc.response_data,
        #     })
        print(exc.errors)
        raise
        ...
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        # rollbar.report_exc_info(
        #     extra_data={'token': token, 'message': message, 'extra': extra})
        # raise self.retry(exc=exc)
        raise
    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        [r.validate_response() for r in responses]
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        # from notifications.models import PushToken
        PushToken.objects.filter(token__in=tokens).update(active=False)

    except PushTicketError as exc:
        # Encountered some other per-notification error.
        raise
