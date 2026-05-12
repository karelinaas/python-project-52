from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from labels.models import Label
from statuses.models import Status
from tasks.filters import TaskFilter
from tasks.models import Task

User = get_user_model()


class TaskCRUDTest(TestCase):
    USERNAME = "testuser"
    PASSWORD = "testpass123"
    TEST_TASK_NAME = "Test Task"
    TEST_TASK_DESCRIPTION = "Test task description"

    def setUp(self):
        self.user = User.objects.create(username=self.USERNAME)
        self.user.set_password(self.PASSWORD)
        self.user.save()
        
        self.other_user = User.objects.create(username="otheruser")
        self.other_user.set_password("otherpass123")
        self.other_user.save()
        
        self.status = Status.objects.create(name="Test Status")
        self.label = Label.objects.create(name="Test Label")
        self.task = Task.objects.create(
            name=self.TEST_TASK_NAME,
            description=self.TEST_TASK_DESCRIPTION,
            status=self.status,
            author=self.user,
            executor=self.other_user,
        )
        self.task.labels.add(self.label)

    def test_task_list_view_get(self):
        """Тест GET /tasks/ - страница со списком всех задач"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse("tasks:list"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.TEST_TASK_NAME)
        self.assertTemplateUsed(response, "tasks/list.html")
        
    def test_task_list_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут получить доступ
        к списку задач
        """
        response = self.client.get(reverse("tasks:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_task_create_view_get(self):
        """Тест GET /tasks/create/ - страница создания задачи"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse("tasks:create"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/create.html")
        self.assertContains(response, _("Name"))
        self.assertContains(response, _("Description"))
        self.assertContains(response, _("Status"))
        self.assertContains(response, _("Executor"))
        self.assertContains(response, _("Labels"))
        
    def test_task_create_view_post_success(self):
        """Тест POST /tasks/create/ - успешное создание задачи"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        new_task_name = "New Task"
        new_task_description = "New task description"
        response = self.client.post(
            reverse("tasks:create"),
            {
                "name": new_task_name,
                "description": new_task_description,
                "status": self.status.pk,
                "executor": self.other_user.pk,
            },
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:list"))
        
        # Проверка, что задача была создана
        new_task = Task.objects.get(name=new_task_name)
        self.assertEqual(new_task.name, new_task_name)
        self.assertEqual(new_task.description, new_task_description)
        self.assertEqual(new_task.status, self.status)
        self.assertEqual(new_task.author, self.user)
        self.assertEqual(new_task.executor, self.other_user)
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Task created successfully"))
        
    def test_task_create_with_labels(self):
        """Тест создания задачи с метками"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        
        # Создаем дополнительные метки для теста
        label1 = Label.objects.create(name="Bug")
        label2 = Label.objects.create(name="Feature")
        
        new_task_name = "Task with Labels"
        new_task_description = "Task description with labels"
        response = self.client.post(
            reverse("tasks:create"),
            {
                "name": new_task_name,
                "description": new_task_description,
                "status": self.status.pk,
                "executor": self.other_user.pk,
                "labels": [label1.pk, label2.pk],
            },
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:list"))
        
        # Проверка, что задача была создана с метками
        new_task = Task.objects.get(name=new_task_name)
        self.assertEqual(new_task.name, new_task_name)
        self.assertEqual(new_task.description, new_task_description)
        self.assertEqual(new_task.status, self.status)
        self.assertEqual(new_task.author, self.user)
        self.assertEqual(new_task.executor, self.other_user)
        
        # Проверка, что метки были добавлены
        labels = new_task.labels.all()
        self.assertEqual(labels.count(), 2)
        self.assertIn(label1, labels)
        self.assertIn(label2, labels)
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Task created successfully"))
        
    def test_task_create_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут
        создавать задачи
        """
        response = self.client.post(
            reverse("tasks:create"),
            {
                "name": "New Task",
                "description": "New task description",
                "status": self.status.pk,
                "executor": self.other_user.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_task_create_duplicate_name(self):
        """Тест создания задачи с дублирующимся именем"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.post(
            reverse("tasks:create"),
            {
                "name": self.TEST_TASK_NAME,
                "description": "Duplicate task description",
                "status": self.status.pk,
                "executor": self.other_user.pk,
            },
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("already exists"))
        
    def test_task_detail_view_get(self):
        """Тест GET /tasks/<int:pk>/ - страница просмотра задачи"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(
            reverse("tasks:detail", kwargs={"pk": self.task.pk}),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/detail.html")
        self.assertContains(response, self.TEST_TASK_NAME)
        self.assertContains(response, self.TEST_TASK_DESCRIPTION)
        
    def test_task_detail_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи
        не могут просматривать задачи
        """
        response = self.client.get(
            reverse("tasks:detail", kwargs={"pk": self.task.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_task_update_view_get(self):
        """Тест GET /tasks/<int:pk>/update/ - страница обновления задачи"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(
            reverse("tasks:update", kwargs={"pk": self.task.pk}),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/update.html")
        self.assertContains(response, self.TEST_TASK_NAME)
        
    def test_task_update_view_post_success(self):
        """
        Тест POST /tasks/<int:pk>/update/
        - успешное обновление задачи
        """
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        new_task_name = "Updated Task"
        new_task_description = "Updated task description"
        response = self.client.post(
            reverse("tasks:update", kwargs={"pk": self.task.pk}),
            {
                "name": new_task_name,
                "description": new_task_description,
                "status": self.status.pk,
                "executor": self.other_user.pk,
            },
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:list"))
        
        # Проверка, что задача была обновлена
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, new_task_name)
        self.assertEqual(self.task.description, new_task_description)
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Task updated successfully"))
        
    def test_task_update_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут обновлять задачи
        """
        response = self.client.post(
            reverse("tasks:update", kwargs={"pk": self.task.pk}),
            {
                "name": "Updated Task",
                "description": "Updated task description",
                "status": self.status.pk,
                "executor": self.other_user.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        
    def test_task_delete_view_get(self):
        """Тест GET /tasks/<int:pk>/delete/ - страница удаления задачи"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(
            reverse("tasks:delete", kwargs={"pk": self.task.pk}),
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/delete.html")
        self.assertContains(response, self.TEST_TASK_NAME)
        self.assertContains(response, _("Yes, delete"))
        
    def test_task_delete_view_post_success(self):
        """Тест POST /tasks/<int:pk>/delete/ - успешное удаление задачи"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.post(
            reverse("tasks:delete", kwargs={"pk": self.task.pk}),
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:list"))
        
        # Проверка, что задача была удалена
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), _("Task deleted successfully"))
        
    def test_task_delete_view_unauthenticated(self):
        """
        Тест того, что неавторизованные пользователи не могут удалять задачи
        """
        response = self.client.post(
            reverse("tasks:delete", kwargs={"pk": self.task.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
        
    def test_task_delete_only_author_can_delete(self):
        """
        Тест того, что только автор задачи может ее удалить
        """
        self.client.login(
            username=self.other_user.username,
            password="otherpass123",
        )
        response = self.client.post(
            reverse("tasks:delete", kwargs={"pk": self.task.pk}),
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Проверка, что задача не была удалена
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
        
        # Проверка flash-сообщения
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            _("Only task author can delete task"),
        )


class TaskFilterTest(TestCase):
    USERNAME = "testuser"
    PASSWORD = "testpass123"
    OTHER_USERNAME = "otheruser"
    OTHER_PASSWORD = "otherpass123"

    TASK_NAME_1 = "Task 1"
    TASK_NAME_2 = "Qwertyuiop Asdfghjkl"
    TASK_NAME_3 = "Task Three"

    def setUp(self):
        # Создание пользователей
        self.user = User.objects.create(username=self.USERNAME)
        self.user.set_password(self.PASSWORD)
        self.user.save()
        
        self.other_user = User.objects.create(username=self.OTHER_USERNAME)
        self.other_user.set_password(self.OTHER_PASSWORD)
        self.other_user.save()
        
        # Создание статусов
        self.status1 = Status.objects.create(name="In Progress")
        self.status2 = Status.objects.create(name="Completed")
        
        # Создание меток
        self.label1 = Label.objects.create(name="Bug")
        self.label2 = Label.objects.create(name="Feature")
        
        # Создание задач
        self.task1 = Task.objects.create(
            name=self.TASK_NAME_1,
            description="Description 1",
            status=self.status1,
            author=self.user,
            executor=self.other_user,
        )
        self.task1.labels.add(self.label1)
        
        self.task2 = Task.objects.create(
            name=self.TASK_NAME_2,
            description="Description 2",
            status=self.status2,
            author=self.other_user,
            executor=self.user,
        )
        self.task2.labels.add(self.label2)
        
        self.task3 = Task.objects.create(
            name=self.TASK_NAME_3,
            description="Description 3",
            status=self.status1,
            author=self.user,
            executor=None,
        )

    def test_filter_by_status(self):
        """Тест фильтрации задач по статусу"""
        queryset = Task.objects.all()
        filter_data = {"status": self.status1.pk}
        task_filter = TaskFilter(filter_data, queryset=queryset)
        
        filtered_tasks = task_filter.qs
        self.assertEqual(filtered_tasks.count(), 2)
        self.assertIn(self.task1, filtered_tasks)
        self.assertIn(self.task3, filtered_tasks)
        self.assertNotIn(self.task2, filtered_tasks)

    def test_filter_by_executor(self):
        """Тест фильтрации задач по исполнителю"""
        queryset = Task.objects.all()
        filter_data = {"executor": self.user.pk}
        task_filter = TaskFilter(filter_data, queryset=queryset)
        
        filtered_tasks = task_filter.qs
        self.assertEqual(filtered_tasks.count(), 1)
        self.assertIn(self.task2, filtered_tasks)
        self.assertNotIn(self.task1, filtered_tasks)
        self.assertNotIn(self.task3, filtered_tasks)

    def test_filter_by_label(self):
        """Тест фильтрации задач по метке"""
        queryset = Task.objects.all()
        filter_data = {"labels": self.label1.pk}
        task_filter = TaskFilter(filter_data, queryset=queryset)
        
        filtered_tasks = task_filter.qs
        self.assertEqual(filtered_tasks.count(), 1)
        self.assertIn(self.task1, filtered_tasks)
        self.assertNotIn(self.task2, filtered_tasks)
        self.assertNotIn(self.task3, filtered_tasks)

    def test_filter_own_tasks_true(self):
        """Тест фильтрации 'Только свои задачи' - включено"""
        queryset = Task.objects.all()
        filter_data = {"own_tasks": True}
        
        # Создание мок-запроса с пользователем
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        task_filter = TaskFilter(
            filter_data,
            queryset=queryset,
            request=request,
        )
        
        filtered_tasks = task_filter.qs
        self.assertEqual(filtered_tasks.count(), 2)
        self.assertIn(self.task1, filtered_tasks)
        self.assertIn(self.task3, filtered_tasks)
        self.assertNotIn(self.task2, filtered_tasks)

    def test_filter_own_tasks_false(self):
        """Тест фильтрации 'Только свои задачи' - выключено"""
        queryset = Task.objects.all()
        filter_data = {"own_tasks": False}
        task_filter = TaskFilter(filter_data, queryset=queryset)
        
        filtered_tasks = task_filter.qs
        self.assertEqual(filtered_tasks.count(), 3)
        self.assertIn(self.task1, filtered_tasks)
        self.assertIn(self.task2, filtered_tasks)
        self.assertIn(self.task3, filtered_tasks)

    def test_filter_combined(self):
        """Тест комбинированной фильтрации"""
        queryset = Task.objects.all()
        filter_data = {
            "status": self.status1.pk,
            "executor": self.other_user.pk,
        }
        task_filter = TaskFilter(filter_data, queryset=queryset)
        
        filtered_tasks = task_filter.qs
        self.assertEqual(filtered_tasks.count(), 1)
        self.assertIn(self.task1, filtered_tasks)
        self.assertNotIn(self.task2, filtered_tasks)
        self.assertNotIn(self.task3, filtered_tasks)

    def test_filter_no_filters(self):
        """Тест без фильтров - должны вернуться все задачи"""
        queryset = Task.objects.all()
        filter_data = {}
        task_filter = TaskFilter(filter_data, queryset=queryset)
        
        filtered_tasks = task_filter.qs
        self.assertEqual(filtered_tasks.count(), 3)
        self.assertIn(self.task1, filtered_tasks)
        self.assertIn(self.task2, filtered_tasks)
        self.assertIn(self.task3, filtered_tasks)

    def test_task_list_view_with_filters(self):
        """Тест представления списка задач с фильтрами"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        
        # Тест фильтрации по статусу
        response = self.client.get(
            reverse("tasks:list"),
            {"status": self.status1.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.TASK_NAME_1)
        self.assertContains(response, self.TASK_NAME_3)
        self.assertNotContains(response, self.TASK_NAME_2)
        
        # Тест фильтрации 'Только свои задачи'
        response = self.client.get(
            reverse("tasks:list"),
            {"own_tasks": "on"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.TASK_NAME_1)
        self.assertContains(response, self.TASK_NAME_3)
        self.assertNotContains(response, self.TASK_NAME_2)

    def test_task_list_view_filter_form_rendered(self):
        """Тест того, что форма фильтрации отображается на странице"""
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        response = self.client.get(reverse("tasks:list"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Status"))
        self.assertContains(response, _("Executor"))
        self.assertContains(response, _("Label"))
        self.assertContains(response, _("Only own tasks"))
        self.assertContains(response, _("Filter"))
        self.assertContains(response, _("Clear"))
