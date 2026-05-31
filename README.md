### Hexlet tests and linter status:
[![Actions Status](https://github.com/karelinaas/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/karelinaas/python-project-52/actions)

[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-light.svg)](https://sonarcloud.io/summary/new_code?id=karelinaas_python-project-52)

# Task Manager

Система управления задачами, разработанная на Django. Приложение позволяет создавать, отслеживать и управлять задачами с возможностью назначения статусов, меток и исполнителей.

## Описание проекта

Task Manager — это веб-приложение для управления задачами с поддержкой:
- Создания и редактирования задач
- Назначения статусов задач
- Добавления меток для классификации
- Назначения исполнителей
- Фильтрации и поиска задач
- Управления пользователями и правами доступа
- Локализации на русский язык

## Технологии

- **Python** 3.12+
- **Django** 6.0.5
- **PostgreSQL** — база данных
- **django-bootstrap5** — стилизация интерфейса
- **django-filter** — фильтрация задач
- **psycopg2-binary** — драйвер PostgreSQL
- **python-dotenv** — управление переменными окружения
- **Rollbar** — мониторинг ошибок
- **uv** — менеджер зависимостей

## Установка

### Требования

- Python 3.12 или выше
- PostgreSQL
- uv (менеджер пакетов Python)

### Шаги установки

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/karelinaas/python-project-52.git
   cd python-project-52
   ```

2. **Установите зависимости:**
   ```bash
   make install
   # или
   uv sync
   ```

3. **Создайте файл переменных окружения:**
   ```bash
   cp .env.example .env
   ```

4. **Настройте переменные окружения в файле `.env`:**
   ```
   SECRET_KEY=ваш-секретный-ключ
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=имя_базы_данных
   POSTGRES_USER=пользователь_бд
   POSTGRES_PASSWORD=пароль_бд
   DB_HOST=localhost
   DB_PORT=5432
   DEBUG=True
   ```

5. **Выполните миграции базы данных:**
   ```bash
   make migrate
   # или
   uv run manage.py migrate
   ```

6. **Соберите статические файлы (для продакшена):**
   ```bash
   make collectstatic
   # или
   uv run manage.py collectstatic
   ```

## Запуск

### Локальный запуск

Запустите сервер разработки:
```bash
make start
# или
uv run manage.py runserver
```

Приложение будет доступно по адресу: `http://localhost:8000`

### Запуск на указанном порту

```bash
make start PORT=8080
```

### Остановка сервера

```bash
make stop
```

### Перезапуск сервера

```bash
make restart
```

## Тестирование

Запуск тестов:
```bash
make test
# или
uv run manage.py test
```

Запуск тестов с покрытием:
```bash
make test-cov
# или
uv run coverage run manage.py test
```

Очистка файлов покрытия:
```bash
make test-clean
```
