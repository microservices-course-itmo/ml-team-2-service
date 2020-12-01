WineUp Recommendations
==============================

Recommendation service for wineup app

Команды для запуска dev сервера:
```shell script
docker-compose build
docker-compose up
```
Подождите, пока выведется сообщение об успешном запуске сервера.

Админка доступна по адресу http://127.0.0.1:80/admin/login/.

Логин для входа: admin

Пароль: задается в переменной окружения DJANGO_SUPERUSER_PASSWORD и по-умолчанию находится в файле .env.dev
