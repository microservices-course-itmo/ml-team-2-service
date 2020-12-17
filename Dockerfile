FROM python:3.7.9

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1

RUN apt update
RUN apt install -y python3-pip python3-scipy
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

RUN \
  apt install -y software-properties-common && \
  add-apt-repository -y ppa:nginx/stable && \
  apt install -y nginx && \
  rm -rf /var/lib/apt/lists/* && \
  echo "\ndaemon off;" >> /etc/nginx/nginx.conf && \
  chown -R www-data:www-data /var/lib/nginx && \
  ln -s /usr/src/app/nginx/service.conf /etc/nginx/sites-enabled/service.conf && \
  rm /etc/nginx/sites-enabled/default



ENTRYPOINT bash -c "python3 src/server/manage.py migrate && \
                    python3 src/server/manage.py createsuperuser --email admin@example.com --username admin --noinput ; \
                    python3 src/server/manage.py runserver localhost:8081 & \
                    python3 swagger/server.py & \
                    nginx"

EXPOSE 80