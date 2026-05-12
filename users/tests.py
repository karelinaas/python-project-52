from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserCRUDTest(TestCase):
    fixtures = ["users.json"]

    def setUp(self):
        self.client = Client()
        self.user = User.objects.get(pk=1)

    def test_user_list_view(self):
        """Тест отображения списка пользователей"""
        response = self.client.get(reverse("users:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser1")
        self.assertContains(response, "testuser2")
        self.assertContains(response, "Иван")
        self.assertContains(response, "Петр")

    def test_user_create_view_get(self):
        """Тест страницы создания пользователя (GET)"""
        response = self.client.get(reverse("users:create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Username"))
        self.assertContains(response, _("Password"))
        self.assertContains(response, _("Password Confirmation"))

    def test_user_create_view_post(self):
        """Тест создания пользователя (POST)"""
        user_data = {
            "username": "newuser",
            "first_name": "Новый",
            "last_name": "Пользователь",
            "password1": "testpass123",
            "password2": "testpass123"
        }
        response = self.client.post(reverse("users:create"), data=user_data)
        
        # Проверяем редирект на страницу входа
        self.assertRedirects(response, reverse("users:login"))
        
        # Проверяем, что пользователь создан
        self.assertTrue(
            User.objects.filter(username=user_data["username"]).exists()
        )
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            _("The user was registered successfully"),
        )

    def test_user_create_duplicate_username(self):
        """Тест создания пользователя с дублирующимся username"""
        user_data = {
            "username": "testuser1",
            "first_name": "Дубликат",
            "last_name": "Пользователь",
            "password1": "testpass123",
            "password2": "testpass123"
        }
        response = self.client.post(reverse("users:create"), data=user_data)
        
        # Страница должна остаться на форме создания из-за ошибки
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что пользователь не создан
        self.assertEqual(
            User.objects.filter(username=user_data["username"]).count(),
            1,
        )

    def test_user_login_view_get(self):
        """Тест страницы входа (GET)"""
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Username"))
        self.assertContains(response, _("Password"))

    def test_user_login_view_post(self):
        """Тест входа пользователя (POST)"""
        # Установим пароль для пользователя из фикстуры
        password = "testpass123"
        self.user.set_password(password)
        self.user.save()

        response = self.client.post(
            reverse("users:login"),
            data={
                "username": "testuser1",
                "password": password,
            },
        )
        
        # Проверяем редирект на главную страницу
        self.assertRedirects(response, reverse("home"))
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("You are logged in"))

    def test_user_logout(self):
        """Тест выхода пользователя"""
        # Сначала логинимся
        password = "testpass123"
        self.user.set_password(password)
        self.user.save()
        self.client.login(username="testuser1", password=password)
        
        # Выходим
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("You are logged out"))

    def test_user_update_view_get_unauthorized(self):
        """Тест страницы редактирования пользователя без авторизации"""
        response = self.client.get(reverse("users:update", kwargs={"pk": 1}))
        
        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

    def test_user_update_view_get_authorized(self):
        """Тест страницы редактирования пользователя с авторизацией"""
        # Логинимся как пользователь
        password = "testpass123"
        self.user.set_password(password)
        self.user.save()
        self.client.login(username="testuser1", password=password)
        
        response = self.client.get(reverse("users:update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Username"))
        self.assertContains(response, "Иван")

    def test_user_update_view_post(self):
        """Тест обновления пользователя"""
        # Логинимся как пользователь
        password = "testpass123"
        self.user.set_password(password)
        self.user.save()
        self.client.login(username="testuser1", password=password)
        
        update_data = {
            "username": "testuser1",
            "first_name": "Измененное",
            "last_name": "Имя"
        }
        response = self.client.post(
            reverse("users:update", kwargs={"pk": 1}),
            data=update_data,
        )
        
        # Проверяем редирект на список пользователей
        self.assertRedirects(response, reverse("users:list"))
        
        # Проверяем, что данные изменены
        updated_user = User.objects.get(pk=1)
        self.assertEqual(updated_user.first_name, update_data["first_name"])
        self.assertEqual(updated_user.last_name, update_data["last_name"])
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("User changed successfully"))

    def test_user_update_other_user_forbidden(self):
        """Тест попытки редактирования другого пользователя"""
        # Логинимся как пользователь 1
        password = "testpass123"
        self.user.set_password(password)
        self.user.save()
        self.client.login(username="testuser1", password=password)
        
        # Пытаемся редактировать пользователя 2
        response = self.client.get(reverse("users:update", kwargs={"pk": 2}))
        
        # Должен быть редирект на список пользователей с сообщением об ошибке
        self.assertRedirects(response, reverse("users:list"))
        
        # Проверяем flash-сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            _("You have no rights to change entity"),
        )

    def test_user_delete_view_get_unauthorized(self):
        """Тест страницы удаления пользователя без авторизации"""
        response = self.client.get(reverse("users:delete", kwargs={"pk": 1}))
        
        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

    def test_user_delete_view_get_authorized(self):
        """Тест страницы удаления пользователя с авторизацией"""
        # Логинимся как пользователь
        password = "testpass123"
        self.user.set_password(password)
        self.user.save()
        self.client.login(username="testuser1", password=password)
        
        response = self.client.get(reverse("users:delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            _("Are you sure you want to delete user "),
        )

    def test_user_delete_view_post(self):
        """Тест удаления пользователя"""
        # Логинимся как пользователь
        password = "testpass123"
        self.user.set_password(password)
        self.user.save()
        self.client.login(username="testuser1", password=password)
        
        response = self.client.post(reverse("users:delete", kwargs={"pk": 1}))
        
        # Проверяем редирект на список пользователей
        self.assertRedirects(response, reverse("users:list"))
        
        # Проверяем, что пользователь удален
        self.assertFalse(User.objects.filter(pk=1).exists())
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("User deleted successfully"))

    def test_user_delete_other_user_forbidden(self):
        """Тест попытки удаления другого пользователя"""
        # Логинимся как пользователь 1
        password = "testpass123"
        self.user.set_password(password)
        self.user.save()
        self.client.login(username="testuser1", password=password)
        
        # Пытаемся удалить пользователя 2
        response = self.client.post(reverse("users:delete", kwargs={"pk": 2}))
        
        # Должен быть редирект на список пользователей с сообщением об ошибке
        self.assertRedirects(response, reverse("users:list"))
        
        # Проверяем, что пользователь 2 не удален
        self.assertTrue(User.objects.filter(pk=2).exists())
        
        # Проверяем flash-сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            _("You have no rights to change entity"),
        )
