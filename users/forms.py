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
    password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")
        labels = {
            "username": _("Username"),
            "first_name": _("Name"),
            "last_name": _("Last Name"),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password1 != password2:
            raise forms.ValidationError(_("Passwords do not match"))

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={"autofocus": True}),
    )
