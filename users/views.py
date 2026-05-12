from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView as BaseLoginView,
    LogoutView as BaseLogoutView,
)
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from tasks.models import Task
from users.forms import UserLoginForm, UserRegisterForm, UserUpdateForm
from users.models import User


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:login")
    
    def form_valid(self, form: UserRegisterForm) -> HttpResponse:
        messages.success(
            self.request,
            _("The user was registered successfully"),
        )
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")
    
    def dispatch(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponseBase:
        user = self.get_object()
        if request.user != user:
            messages.error(
                self.request,
                _("You have no rights to change entity"),
            )
            return redirect("users:list")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form: UserUpdateForm) -> HttpResponse:
        messages.success(self.request, _("User changed successfully"))
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("users:list")
    
    def dispatch(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponseBase:
        user = self.get_object()
        if request.user != user:
            messages.error(
                self.request,
                _("You have no rights to change entity"),
            )
            return redirect("users:list")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form: BaseForm) -> HttpResponse:
        user = self.get_object()
        
        if Task.objects.filter(author=user).exists() or (
            Task.objects.filter(executor=user).exists()
        ):
            messages.error(
                self.request,
                _("Cannot delete user while they have associated tasks"),
            )
            return redirect("users:list")
        
        messages.success(self.request, _("User deleted successfully"))
        return super().form_valid(form)


class LoginView(BaseLoginView):
    form_class = UserLoginForm
    template_name = "users/login.html"
    
    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        messages.success(self.request, _("You are logged in"))
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse_lazy("home")


class LogoutView(BaseLogoutView):
    def dispatch(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponseBase:
        messages.success(request, _("You are logged out"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy("home")
