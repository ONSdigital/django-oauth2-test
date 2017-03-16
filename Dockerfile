FROM python:2
MAINTAINER David Carboni

WORKDIR /oauth2server
ADD oauth2server ./oauth2server
ADD requirements.txt ./

RUN pip install -r requirements.txt

ENTRYPOINT python oauth2server/manage.py runserver 0.0.0.0:8000
