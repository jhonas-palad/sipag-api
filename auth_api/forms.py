from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        exclude = []


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        exclude = []