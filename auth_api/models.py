from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.password_validation import validate_password

from api.models import Image


class CustomUserManager(UserManager):
    def _create_user(
        self,
        phone_number=None,
        email=None,
        password=None,
        **extra_fields,
    ):

        if phone_number is None and email is None:
            raise ValueError("Must provide either Phone number or email")

        if not password:
            raise ValueError("Password shoudn't be empty")

        if email:
            email = self.normalize_email(email)

        user: User = self.model(
            phone_number=phone_number, email=email, password=password, **extra_fields
        )
        user.full_clean()
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        phone_number=None,
        email=None,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(
        self, phone_number=None, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)


class User(AbstractUser):
    username = None
    phone_number = PhoneNumberField(region="PH", unique=True, null=True, blank=True)
    password = models.CharField(
        _("password"), max_length=128, validators=[validate_password]
    )
    photo = models.OneToOneField(
        to=Image, on_delete=models.DO_NOTHING, blank=True, null=True
    )
    is_verified = models.BooleanField(_("is verified"), default=False)
    # Need for auth checks, and authenticate method
    USERNAME_FIELD = "phone_number"
    objects = CustomUserManager()

    def __repr__(self):
        phone_number = (
            self.phone_number.format_as(0) if self.phone_number else "no phone number"
        )
        email = self.email if self.email else "no email"
        return (
            f"{self.__class__.__name__} <phone_number: {phone_number}, email: {email}>"
        )

    __str__ = __repr__
