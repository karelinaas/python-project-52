from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse

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
        self.assertContains(response, "Имя пользователя")
        self.assertContains(response, "Пароль")
        self.assertContains(response, "Подтверждение пароля")

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
        self.assertTrue(User.objects.filter(username="newuser").exists())
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Пользователь успешно зарегистрирован",
        )

    def test_user_create_duplicate_username(self):
        """Тест создания пользователя с дублирующимся username"""
        user_data = {
            "username": "testuser1",  # Уже существует в фикстурах
            "first_name": "Дубликат",
            "last_name": "Пользователь",
            "password1": "testpass123",
            "password2": "testpass123"
        }
        response = self.client.post(reverse("users:create"), data=user_data)
        
        # Страница должна остаться на форме создания из-за ошибки
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что пользователь не создан
        self.assertEqual(User.objects.filter(username="testuser1").count(), 1)

    def test_user_login_view_get(self):
        """Тест страницы входа (GET)"""
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Имя пользователя")
        self.assertContains(response, "Пароль")

    def test_user_login_view_post(self):
        """Тест входа пользователя (POST)"""
        # Установим пароль для пользователя из фикстуры
        self.user.set_password("testpass123")
        self.user.save()
        
        login_data = {
            "username": "testuser1",
            "password": "testpass123"
        }
        response = self.client.post(reverse("users:login"), data=login_data)
        
        # Проверяем редирект на главную страницу
        self.assertRedirects(response, reverse("home"))
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Вы залогинены")

    def test_user_logout(self):
        """Тест выхода пользователя"""
        # Сначала логинимся
        self.user.set_password("testpass123")
        self.user.save()
        self.client.login(username="testuser1", password="testpass123")
        
        # Выходим
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Вы разлогинены")

    def test_user_update_view_get_unauthorized(self):
        """Тест страницы редактирования пользователя без авторизации"""
        response = self.client.get(reverse("users:update", kwargs={"pk": 1}))
        
        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

    def test_user_update_view_get_authorized(self):
        """Тест страницы редактирования пользователя с авторизацией"""
        # Логинимся как пользователь
        self.user.set_password("testpass123")
        self.user.save()
        self.client.login(username="testuser1", password="testpass123")
        
        response = self.client.get(reverse("users:update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Имя пользователя")
        self.assertContains(response, "Иван")

    def test_user_update_view_post(self):
        """Тест обновления пользователя"""
        # Логинимся как пользователь
        self.user.set_password("testpass123")
        self.user.save()
        self.client.login(username="testuser1", password="testpass123")
        
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
        self.assertEqual(updated_user.first_name, "Измененное")
        self.assertEqual(updated_user.last_name, "Имя")
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Пользователь успешно изменен")

    def test_user_update_other_user_forbidden(self):
        """Тест попытки редактирования другого пользователя"""
        # Логинимся как пользователь 1
        self.user.set_password("testpass123")
        self.user.save()
        self.client.login(username="testuser1", password="testpass123")
        
        # Пытаемся редактировать пользователя 2
        response = self.client.get(reverse("users:update", kwargs={"pk": 2}))
        
        # Должен быть редирект на список пользователей с сообщением об ошибке
        self.assertRedirects(response, reverse("users:list"))
        
        # Проверяем flash-сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "У вас нет прав для изменения")

    def test_user_delete_view_get_unauthorized(self):
        """Тест страницы удаления пользователя без авторизации"""
        response = self.client.get(reverse("users:delete", kwargs={"pk": 1}))
        
        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

    def test_user_delete_view_get_authorized(self):
        """Тест страницы удаления пользователя с авторизацией"""
        # Логинимся как пользователь
        self.user.set_password("testpass123")
        self.user.save()
        self.client.login(username="testuser1", password="testpass123")
        
        response = self.client.get(reverse("users:delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Вы уверены, что хотите удалить пользователя",
        )

    def test_user_delete_view_post(self):
        """Тест удаления пользователя"""
        # Логинимся как пользователь
        self.user.set_password("testpass123")
        self.user.save()
        self.client.login(username="testuser1", password="testpass123")
        
        response = self.client.post(reverse("users:delete", kwargs={"pk": 1}))
        
        # Проверяем редирект на список пользователей
        self.assertRedirects(response, reverse("users:list"))
        
        # Проверяем, что пользователь удален
        self.assertFalse(User.objects.filter(pk=1).exists())
        
        # Проверяем flash-сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Пользователь успешно удален")

    def test_user_delete_other_user_forbidden(self):
        """Тест попытки удаления другого пользователя"""
        # Логинимся как пользователь 1
        self.user.set_password("testpass123")
        self.user.save()
        self.client.login(username="testuser1", password="testpass123")
        
        # Пытаемся удалить пользователя 2
        response = self.client.post(reverse("users:delete", kwargs={"pk": 2}))
        
        # Должен быть редирект на список пользователей с сообщением об ошибке
        self.assertRedirects(response, reverse("users:list"))
        
        # Проверяем, что пользователь 2 не удален
        self.assertTrue(User.objects.filter(pk=2).exists())
        
        # Проверяем flash-сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "У вас нет прав для изменения")
