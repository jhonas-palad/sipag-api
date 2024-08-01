from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest
from django.db.models.query import Q

UserModel = get_user_model()


class ModelBackend(BaseBackend):

    def authenticate(
        self, request, phone_number=None, email=None, password=None, **kwargs
    ):
        if (phone_number is None and email is None) or password is None:
            return

        try:
            user = UserModel._default_manager.get(
                Q(phone_number=phone_number) | Q(email=email)
            )
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        return getattr(user, "is_active", True)
