from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from users.models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )
        labels = {
            "username": _("Username"),
            "first_name": _("Name"),
            "last_name": _("Last Name"),
            "password1": _("Password"),
            "password2": _("Password Confirmation"),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")
        labels = {
            "username": _("Username"),
            "first_name": _("Name"),
            "last_name": _("Last Name"),
        }


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={"autofocus": True}),
    )
