from django.contrib import admin
from django.urls import path

from task_manager import views

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
]
