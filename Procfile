web: python oauth2server/manage.py collectstatic --noinput ;python oauth2server/manage.py migrate; bash ./init_db.sh; gunicorn --bind 0.0.0.0:$PORT --workers 4 proj.wsgi --pythonpath 'oauth2server'
