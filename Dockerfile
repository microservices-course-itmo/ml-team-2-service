FROM kinoooshnik/ml-team-2-service:ml-team-2-service

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./nginx .

RUN \
  ln -s /usr/src/app/nginx/service.conf /etc/nginx/sites-enabled/service.conf && \
  rm /etc/nginx/sites-enabled/default

COPY . .

#python3 src/kafka/catalog_consumer.py & \
ENTRYPOINT bash -c "python3 src/server/manage.py migrate && \
                    python3 src/server/manage.py createsuperuser --email admin@example.com --username admin --noinput ; \
                    BUILD_MATRIX=1 python3 src/server/manage.py runserver localhost:8081 & \
                    python3 src/kafka/user_consumer.py & \
                    python3 src/kafka/favourites_consumer.py & \
                    nginx"

EXPOSE 80