from channels.middleware import BaseMiddleware

from rest_framework import HTTP_HEADER_ENCODING
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.utils import get_md5_hash_password
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPE_BYTES
from rest_framework_simplejwt.exceptions import (
    AuthenticationFailed,
    InvalidToken,
    TokenError,
)

from rest_framework_simplejwt.settings import api_settings
from channels.db import database_sync_to_async

from django.utils.translation import gettext_lazy as _


class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        from django.contrib.auth import get_user_model

        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def get_validated_token(self, raw_token: bytes):
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )

        raise InvalidToken(
            {
                "detail": _("Given token not valid for any token type"),
                "messages": messages,
            }
        )

    @database_sync_to_async
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(_("User is inactive"), code="user_inactive")

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(
                api_settings.REVOKE_TOKEN_CLAIM
            ) != get_md5_hash_password(user.password):
                raise AuthenticationFailed(
                    _("The user's password has been changed."), code="password_changed"
                )

        return user

    async def __call__(self, scope, receive, send):

        token = self.get_token_from_scope(scope)
        print(token)
        # if token != None:
        validated_token = self.get_validated_token(token)
        user = self.get_user(validated_token)

        if user:
            scope["user"] = user
        # user_id = await self.get_user_from_token(token)
        # if user_id:
        #     scope["user_id"] = user_id

        # else:
        #     scope["error"] = "Invalid token"

        # if token == None:
        #     scope["error"] = "provide an auth token"

        return await super().__call__(scope, receive, send)

    def get_token_from_scope(self, scope):
        headers = dict(scope.get("headers", []))

        auth_header = headers.get(b"authorization", b"")

        if isinstance(auth_header, str):
            # Work around django test client oddness
            auth_header = auth_header.encode(HTTP_HEADER_ENCODING)

        parts = auth_header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _("Authorization header must contain two space-delimited values"),
                code="bad_authorization_header",
            )

        return parts[1]

    # def get_user_from_token(self, token):
    #     try:
    #         access_token = AccessToken(token)
    #         return access_token["user_id"]
    #     except:
    #         return None
