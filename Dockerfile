FROM jupyter/scipy-notebook:latest

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT bash -c "python src/server/manage.py migrate && python src/server/manage.py createsuperuser --email admin@example.com --username admin --noinput ; python src/server/manage.py runserver 0.0.0.0:80"