FROM python:2.7.13

WORKDIR /oauth2server
COPY . /oauth2server
EXPOSE 8040

ENV OAUTH2_SUPER_USER admin
ENV OAUTH2_SUPER_USER_PASSWORD admin2017
ENV OAUTH2_SUPER_USER_EMAIL admin@email.com

RUN pip install pipenv==8.3.1 && pipenv install --deploy --system
RUN cp -f oauth2server/django_oauth2_server .

CMD ["./start.sh"]
