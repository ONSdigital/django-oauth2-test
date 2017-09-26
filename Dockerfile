FROM python:2.7.13

WORKDIR /oauth2server
COPY . /oauth2server

RUN pip install -r requirements.txt
RUN python oauth2server/manage.py migrate
RUN cp -f oauth2server/django_oauth2_server .

ENTRYPOINT python oauth2server/manage.py runserver 0.0.0.0:8040
