FROM python:2.7.13

WORKDIR /oauth2server
COPY . /oauth2server
EXPOSE 8040
ENV OAUTH2_SUPER_USER="admin"
ENV OAUTH2_SUPER_USER_PASSWORD="admin2017"
ENV OAUTH2_SUPER_USER_EMAIL="admin@email.com"

RUN pip install -r requirements.txt
RUN python oauth2server/manage.py migrate
RUN python oauth2server/manage.py loaddata oauth2server/apps/credentials/fixtures/ons_credentials.json
RUN ./init_db.sh
RUN cp -f oauth2server/django_oauth2_server .

ENTRYPOINT python oauth2server/manage.py runserver 0.0.0.0:8040
