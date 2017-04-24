FROM python:2.7.13
MAINTAINER David Carboni

WORKDIR /oauth2server
ADD oauth2server ./oauth2server
ADD requirements.txt ./

RUN pip install -r requirements.txt
RUN cd oauth2server
RUN python oauth2server/manage.py migrate
RUN cp -f oauth2server/django_oauth2_server .

ENTRYPOINT python oauth2server/manage.py runserver 0.0.0.0:8040
