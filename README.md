# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


## Авторы
Разработка курса и заданий Яндекс.Практикум
Иполнитель: Антон Краснокутский

## Описание
Проект разрабатывался на курсе Python-разработчик Яндекс.Практикум. Является учебным проектом по изучению Django framework.
Проект предоставляет возможности:
- Ресгистрация/авторизация ползователей
- Создание постов
- Коментирование постов
- Просмотр постов и коментариев

## Технология
- Django 2.2.16

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/AntonKrasnokutsky/hw05_final-blog-.git
```

```
cd hw05_final-blog-/
```

Создать виртуальное окружение

```
python3.7 -m venv venv
```

Активировать виртуальное окружение и установить зависимости

```
. venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Выполнить миграции
```
cd yatube
python manage.py migrate
```

Создать суперпользователя
```
python manage.py createsuperuser
```

Запустить проект
```
python manage.py runserver
```

После запуска проект будет доступен по адресу `localhost:8000`