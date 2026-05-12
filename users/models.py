from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = models.CharField(max_length=150, verbose_name=_("Name"))
    last_name = models.CharField(max_length=150, verbose_name=_("Last Name"))
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
