from typing import Dict, Any

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password

from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework import exceptions, serializers

from rest_framework_simplejwt.serializers import PasswordField
from rest_framework_simplejwt.tokens import AccessToken, AuthUser, Token

from api.models import Image
from api.serializers import ImageSerializer

UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    email = serializers.CharField(required=False, allow_blank=True)
    password = PasswordField()

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def _validate_username_email(self, phone_number, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif phone_number and password:
            try:
                user = self.authenticate(phone_number=phone_number, password=password)
            except ValueError:
                raise exceptions.ValidationError("Phone number is invalid")
        else:
            msg = _("Must include either Phone number or Email.")
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        phone_number = attrs.get("phone_number", None)
        email = attrs.get("email", None)
        password = attrs.get("password", None)

        if not phone_number and not email:
            msg = _("Must include either Phone number or Email.")
            raise exceptions.ValidationError(msg)

        user = self._validate_username_email(phone_number, email, password)
        if not user:
            raise exceptions.AuthenticationFailed()
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    photo = photo = ImageSerializer()
    phone_number = PhoneNumberField(
        region="PH", required=False, allow_blank=True, default=""
    )

    class Meta:
        model = UserModel
        exclude = ["password"]


class UserDetailsSerailizer(serializers.Serializer):
    id = serializers.IntegerField()
    phone_number = PhoneNumberField(
        region="PH", required=False, allow_blank=True, default=""
    )
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    is_verified = serializers.BooleanField()
    photo = ImageSerializer()


class UserCredentialsSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region="PH", required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = PasswordField(validators=[validate_password])

    def validate_phone_number(self, phone_number):

        if UserModel._default_manager.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Phone number has already been used.")
        return phone_number

    def validate_email(self, email):
        if UserModel._default_manager.filter(email=email).exists():
            raise serializers.ValidationError("Email has already been used.”")
        return email


class JWTSerializer(serializers.Serializer):
    token_class = AccessToken

    user = serializers.SerializerMethodField()
    token = serializers.CharField()

    @classmethod
    def get_token(cls, user: AuthUser) -> Token:
        update_last_login(None, user)
        return cls.token_class.for_user(user)

    def get_user(self, obj):
        user_data = UserSerializer(obj["user"], context=self.context).data
        return user_data


class SignupSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region="PH", allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, required=False)
    password = PasswordField()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    photo = serializers.ImageField()

    class Meta:
        model = UserModel

    def create(self, validated_data):

        user_photo = Image(img_file=validated_data["photo"])
        user_photo.upload_to = "users"
        user_photo.save()
        new_user_kwargs = {
            "first_name": validated_data.get("first_name", ""),
            "last_name": validated_data.get("last_name", ""),
            "password": validated_data["password"],
            "email": validated_data.get("email", ""),
            "phone_number": validated_data.get("phone_number", None),
            "photo": user_photo,
        }
        new_user = UserModel.objects.create_user(**new_user_kwargs)

        return new_user

    def validate_password(self, password):
        validate_password(password)
        return password

    def validate_phone_number(self, phone_number):
        if phone_number == "":
            return None
        if self.Meta.model._default_manager.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Phone number has already been used.")
        return phone_number

    def validate_email(self, email):
        if email == "":
            return None
        if self.Meta.model._default_manager.filter(email=email).exists():
            raise serializers.ValidationError("Email has already been used.”")
        return email

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        email = attrs.get("email")
        if not phone_number and not email:
            raise serializers.ValidationError(
                "Please provide a phone number or email address"
            )

        return attrs


class UserPhotoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    photo = ImageSerializer()

    def create(self, validated_data):
        user = UserModel.objects.get(id=validated_data.get("id"))
        user_photo = Image(**validated_data["photo"])
        user_photo.upload_to = "users"
        user_photo.save()
        user.photo = user_photo
        user.save()
        return {
            "id": user.id,
            "photo": ImageSerializer(instance=user_photo, context=self.context).data,
        }

    def validate(self, attrs):
        return attrs
