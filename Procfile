web: python oauth2server/manage.py migrate; bash ./init_db.sh; gunicorn --bind 0.0.0.0:8080 --workers 4 proj.wsgi
