from django.http import HttpRequest, HttpResponse


def home(_: HttpRequest) -> HttpResponse:
    return HttpResponse("Привет! Добро пожаловать в трекер задач.")
