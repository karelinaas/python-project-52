from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from labels.models import Label
from statuses.models import Status
from tasks.models import Task

User = get_user_model()


class LabelCRUDTest(TestCase):
    USERNAME = "testuser"
    PASSWORD = "testpass123"
    TEST_LABEL_NAME = "Test Label"

    def setUp(self):
        self.user = User.objects.create(username=self.USERNAME)
        self.user.set_password(self.PASSWORD)
        self.user.save()
        self.label = Label.objects.create(name=self.TEST_LABEL_NAME)
        
    def test_label_list_view_get(self):
        """Тест GET /labels/ - страница со списком всех меток"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse("labels:list"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.TEST_LABEL_NAME)
        self.assertTemplateUsed(response, "labels/list.html")
        
    def test_label_list_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут получить доступ
        к списку меток
        """
        response = self.client.get(reverse("labels:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_label_create_view_get(self):
        """Тест GET /labels/create/ - страница создания метки"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse("labels:create"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/create.html")
        self.assertContains(response, _("Name"))
        
    def test_label_create_view_post_success(self):
        """Тест POST /labels/create/ - успешное создание метки"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        new_label_name = "New Label"
        response = self.client.post(
            reverse("labels:create"),
            {"name": new_label_name},
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("labels:list"))
        
        # Проверка, что метка была создана
        self.assertTrue(Label.objects.filter(name=new_label_name).exists())
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Label created successfully"))
        
    def test_label_create_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут
        создавать метки
        """
        response = self.client.post(
            reverse("labels:create"),
            {"name": "New Label"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_label_create_duplicate_name(self):
        """Тест создания метки с дублирующимся именем"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.post(
            reverse("labels:create"),
            {"name": self.TEST_LABEL_NAME},
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("already exists"))
        
    def test_label_update_view_get(self):
        """Тест GET /labels/<int:pk>/update/ - страница обновления метки"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(
            reverse("labels:update", kwargs={"pk": self.label.pk}),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/update.html")
        self.assertContains(response, self.TEST_LABEL_NAME)
        
    def test_label_update_view_post_success(self):
        """
        Тест POST /labels/<int:pk>/update/
        - успешное обновление метки
        """
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        new_label_name = "Updated Label"
        response = self.client.post(
            reverse("labels:update", kwargs={"pk": self.label.pk}),
            {"name": new_label_name},
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("labels:list"))
        
        # Проверка, что метка была обновлена
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, new_label_name)
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Label updated successfully"))
        
    def test_label_update_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут обновлять метки
        """
        response = self.client.post(
            reverse("labels:update", kwargs={"pk": self.label.pk}),
            {"name": "Updated Label"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_label_delete_view_get(self):
        """Тест GET /labels/<int:pk>/delete/ - страница удаления метки"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(
            reverse("labels:delete", kwargs={"pk": self.label.pk}),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/delete.html")
        self.assertContains(response, self.TEST_LABEL_NAME)
        self.assertContains(response, _("Yes, delete"))
        
    def test_label_delete_view_post_success(self):
        """Тест POST /labels/<int:pk>/delete/ - успешное удаление метки"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.post(
            reverse("labels:delete", kwargs={"pk": self.label.pk}),
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("labels:list"))
        
        # Проверка, что метка была удалена
        self.assertFalse(Label.objects.filter(pk=self.label.pk).exists())
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Label deleted successfully"))
        
    def test_label_delete_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут удалять метки
        """
        response = self.client.post(
            reverse("labels:delete", kwargs={"pk": self.label.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_label_delete_protected_when_linked_to_task(self):
        """Тест того, что метку нельзя удалить, если она связана с задачей"""
        # Создаем статус и задачу, связанную с меткой
        status = Status.objects.create(name="Test Status")
        task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            status=status,
            author=self.user,
        )
        task.labels.add(self.label)
        
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.post(
            reverse("labels:delete", kwargs={"pk": self.label.pk}),
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("labels:list"))
        
        # Проверка, что метка не была удалена
        self.assertTrue(Label.objects.filter(pk=self.label.pk).exists())
        
        # Проверка flash-сообщения об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            _("Cannot delete label because it is in use"),
        )
