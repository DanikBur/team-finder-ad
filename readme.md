# TeamFinder

Django-приложение для поиска тиммейтов на pet-проекты:
автор публикует идею, остальные пользователи могут добавить
её в избранное и присоединиться к разработке.

Реализован **Вариант 1** задания: избранное + фильтрация
пользователей по 4 критериям.

## Стек

- Python 3.11
- Django 5.2.4
- PostgreSQL 16
- Pillow (генерация дефолтных аватарок)
- python-decouple (конфигурация через `.env`)
- Docker / docker-compose (для подъёма БД)

## Структура

```
team-finder-ad/
├── team_finder/                # Django-настройки и общий urls.py
├── users/                      # модель User, авторизация, профили, фильтр
├── projects/                   # модель Project, CRUD, избранное, AJAX
├── templates_var1/             # HTML-шаблоны (вариант 1)
├── static/                     # CSS, JS, шрифты, картинки
├── docker-compose.yml          # контейнер с PostgreSQL
├── .env_example                # шаблон переменных окружения
└── requirements.txt
```

## Локальный запуск

1. Клонировать и зайти в каталог:
   ```bash
   git clone https://github.com/DanikBur/team-finder-ad.git
   cd team-finder-ad
   ```

2. Создать виртуальное окружение и поставить зависимости:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Скопировать `.env_example` → `.env` и заполнить:
   ```bash
   cp .env_example .env
   ```

4. Запустить PostgreSQL:
   ```bash
   docker compose up -d
   ```

5. Применить миграции и засеять демо-данные:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

6. Поднять dev-сервер:
   ```bash
   python manage.py runserver
   ```

   Сайт будет доступен на `http://localhost:8000`.

## Переменные `.env`

| Переменная             | Назначение                                         |
|------------------------|----------------------------------------------------|
| `DJANGO_SECRET_KEY`    | секретный ключ Django                              |
| `DJANGO_DEBUG`         | `True` для разработки                              |
| `DJANGO_ALLOWED_HOSTS` | список хостов через запятую                        |
| `POSTGRES_DB`          | имя БД                                             |
| `POSTGRES_USER`        | пользователь БД                                    |
| `POSTGRES_PASSWORD`    | пароль БД                                          |
| `POSTGRES_HOST`        | хост БД                                            |
| `POSTGRES_PORT`        | порт БД                                            |

## Тестовые аккаунты

| Email                   | Пароль       | Роль          |
|-------------------------|--------------|---------------|
| `admin@example.com`     | `admin12345` | администратор |
| `dmitry@yandex.ru`      | `qwerty12345`| пользователь  |
| `polina@example.com`    | `qwerty12345`| пользователь  |
| `sergey@example.com`    | `qwerty12345`| пользователь  |
| `yulia@example.com`     | `qwerty12345`| пользователь  |

## Что реализовано

- Кастомная модель `User` с email вместо username.
- Автогенерация аватарки (буква на цветном фоне) при создании
  пользователя без загруженной картинки.
- Нормализация телефона: формат `8XXXXXXXXXX` приводится к `+7XXXXXXXXXX`.
- Валидация ссылки на GitHub: только домен `github.com`.
- Пагинация по 12 элементов на списках проектов и пользователей.
- Избранное: AJAX-эндпоинт `POST /projects/<id>/toggle-favorite/`.
- Участие в проекте: AJAX `POST /projects/<id>/toggle-participate/`.
- Завершение проекта владельцем: AJAX `POST /projects/<id>/complete/`.
- Страница «Избранное» (`/projects/favorites/`) только для владельца.
- 4 фильтра пользователей на `/users/list/?filter=...`.

## Запуск тестов

```bash
python manage.py test users projects
```

## Линтер

В `setup.cfg` настроен flake8 (max-line-length = 100):

```bash
pip install flake8
flake8 users projects team_finder
```

## Автор

- GitHub: [DanikBur](https://github.com/DanikBur)
