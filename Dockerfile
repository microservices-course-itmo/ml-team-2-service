FROM python:3.7.9

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1

RUN apt update
RUN apt install -y python3-pip python3-scipy
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT bash -c "python3 src/server/manage.py migrate && python3 src/server/manage.py createsuperuser --email admin@example.com --username admin --noinput ; python3 src/server/manage.py runserver 0.0.0.0:80"