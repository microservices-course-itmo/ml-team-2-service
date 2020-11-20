WineUp Recommendations
==============================

Recommendation service for wineup app

Команда для запуска dev сервера:
```shell script
docker-compose up -d
```
После первого запуска для создания супер пользователя (пароль находится в файле .env.dev) необходимо запустить:
```shell script
docker-compose exec web python src/server/manage.py createsuperuser --email admin@example.com --username admin --noinput
```

Админка доступна по адресу http://127.0.0.1:8000/admin/login/.