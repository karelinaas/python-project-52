from django.contrib import admin
from django.urls import include, path

from task_manager import views
from users import views as user_views

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path("login/", user_views.LoginView.as_view(), name="login"),
    path("users/", include("users.urls")),
    path("statuses/", include("statuses.urls")),
    path("labels/", include("labels.urls")),
    path("tasks/", include("tasks.urls")),
]
