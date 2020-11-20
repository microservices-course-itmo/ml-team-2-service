WineUp Recommendations
==============================

Recommendation service for wineup app

Команды для запуска dev сервера:
```shell script
docker-compose build
docker-compose up
```
Подождите, пока выведется сообщение об успешном запуске сервера.

Админка доступна по адресу http://127.0.0.1:8000/admin/login/.

После первого запуска для создания супер пользователя (пароль находится в файле .env.dev) необходимо запустить:
```shell script
docker-compose exec web python src/server/manage.py createsuperuser --email admin@example.com --username admin --noinput
```
