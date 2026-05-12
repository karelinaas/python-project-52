from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from statuses.models import Status

User = get_user_model()


class StatusCRUDTest(TestCase):
    USERNAME = "testuser"
    PASSWORD = "testpass123"
    TEST_STATUS_NAME = "Test Status"

    def setUp(self):
        self.user = User.objects.create(username=self.USERNAME)
        self.user.set_password(self.PASSWORD)
        self.user.save()
        self.status = Status.objects.create(name=self.TEST_STATUS_NAME)
        
    def test_status_list_view_get(self):
        """Тест GET /statuses/ - страница со списком всех статусов"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse("statuses:list"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.TEST_STATUS_NAME)
        self.assertTemplateUsed(response, "statuses/list.html")
        
    def test_status_list_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут получить доступ
        к списку статусов
        """
        response = self.client.get(reverse("statuses:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_status_create_view_get(self):
        """Тест GET /statuses/create/ - страница создания статуса"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse("statuses:create"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/create.html")
        self.assertContains(response, _("Name"))
        
    def test_status_create_view_post_success(self):
        """Тест POST /statuses/create/ - успешное создание статуса"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        new_status_name = "New Status"
        response = self.client.post(
            reverse("statuses:create"),
            {"name": new_status_name},
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("statuses:list"))
        
        # Проверка, что статус был создан
        self.assertTrue(Status.objects.filter(name=new_status_name).exists())
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Status created successfully"))
        
    def test_status_create_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут
        создавать статусы
        """
        response = self.client.post(
            reverse("statuses:create"),
            {"name": "New Status"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_status_create_duplicate_name(self):
        """Тест создания статуса с дублирующимся именем"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.post(
            reverse("statuses:create"),
            {"name": self.TEST_STATUS_NAME},
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("already exists"))
        
    def test_status_update_view_get(self):
        """Тест GET /statuses/<int:pk>/update/ - страница обновления статуса"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(
            reverse("statuses:update", kwargs={"pk": self.status.pk}),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/update.html")
        self.assertContains(response, self.TEST_STATUS_NAME)
        
    def test_status_update_view_post_success(self):
        """
        Тест POST /statuses/<int:pk>/update/
        - успешное обновление статуса
        """
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        new_status_name = "Updated Status"
        response = self.client.post(
            reverse("statuses:update", kwargs={"pk": self.status.pk}),
            {"name": new_status_name},
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("statuses:list"))
        
        # Проверка, что статус был обновлен
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, new_status_name)
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Status changed successfully"))
        
    def test_status_update_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут обновлять статусы
        """
        response = self.client.post(
            reverse("statuses:update", kwargs={"pk": self.status.pk}),
            {"name": "Updated Status"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_status_delete_view_get(self):
        """Тест GET /statuses/<int:pk>/delete/ - страница удаления статуса"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(
            reverse("statuses:delete", kwargs={"pk": self.status.pk}),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/delete.html")
        self.assertContains(response, self.TEST_STATUS_NAME)
        self.assertContains(response, _("Yes, delete"))
        
    def test_status_delete_view_post_success(self):
        """Тест POST /statuses/<int:pk>/delete/ - успешное удаление статуса"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.post(
            reverse("statuses:delete", kwargs={"pk": self.status.pk}),
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("statuses:list"))
        
        # Проверка, что статус был удален
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Status deleted successfully"))
        
    def test_status_delete_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут удалять статусы
        """
        response = self.client.post(
            reverse("statuses:delete", kwargs={"pk": self.status.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_status_delete_protected_when_linked_to_task(self):
        """Тест того, что статус нельзя удалить, если он связан с задачей"""
        # Этот тест будет реализован, когда модель Task будет создана
        pass
