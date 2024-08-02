from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.http.request import QueryDict
from .serializers import (
    LoginSerializer,
    JWTSerializer,
    SignupSerializer,
    UserDetailsSerailizer,
    UserPhotoSerializer,
    UserCredentialsSerializer,
)
from utils.models import to_model_dict

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        "password",
        "old_password",
        "new_password1",
        "new_password2",
    ),
)


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def create_token(self):
        self.token = JWTSerializer.get_token(self.user)

    def login(self):
        self.user = self.serializer.validated_data["user"]
        self.create_token()

    def get_response(self):
        data = {"user": self.user, "token": str(self.token)}
        serializer = JWTSerializer(instance=data, context={"request": self.request})

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def get(self, request, *args, **kwargs):
        return Response({"version": request.version}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()


login_view = LoginView.as_view()


class SignupView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer
    parser_classes = (MultiPartParser, FormParser)

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response({"version": request.version}, status=status.HTTP_200_OK)

    def save_user(self, *args, **kwargs):
        self.user = self.serializer.save(*args, **kwargs)
        user_detail = UserDetailsSerailizer(
            instance=self.user, context={"request": self.request}
        )
        return user_detail.data

    def get_response(self):
        user_detail = self.save_user()
        return Response(data=user_detail, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        # print(request.FILES)
        print(request.data)
        self.serializer = self.get_serializer(
            data=request.data, context={"request": self.request}
        )
        self.serializer.is_valid(raise_exception=True)
        return self.get_response()


signup_view = SignupView.as_view()


class UserCredentailsView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserCredentialsSerializer

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_response(self):
        return Response(data=self.serializer.data, status=status.HTTP_202_ACCEPTED)

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(
            data=request.data, context={"request": self.request}
        )
        self.serializer.is_valid(raise_exception=True)
        return self.get_response()
    
user_credentails_view = UserCredentailsView.as_view()

class CheckUserFieldsView(GenericAPIView):
    permission_classes = (AllowAny,)

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_response(self):
        user_detail = self.save_user()
        return Response(data=user_detail, status=status.HTTP_202_ACCEPTED)

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(
            data=request.data, context={"request": self.request}
        )
        self.serializer.is_valid(raise_exception=True)
        return self.get_response()


class UserPhotoView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserPhotoSerializer

    def get(self, request, *args, **kwargs):
        print(request.query_params, kwargs)
        return Response(data={"hello": "world"}, status=status.HTTP_202_ACCEPTED)

    def post(self, request, id, *args, **kwargs):
        request.data["id"] = id
        data = {
            "id": request.data.get("id", None),
            "photo": {"img_file": request.data.get("photo", None)},
        }
        self.serializer = self.get_serializer(data=data)
        self.serializer.is_valid(raise_exception=True)
        data_img = self.serializer.save()
        return Response(data=data_img, status=status.HTTP_202_ACCEPTED)


upload_image_view = UserPhotoView.as_view()
