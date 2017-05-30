#!/bin/sh
echo "------ Create database tables ------"
python oauth2server/manage.py migrate --noinput
 
echo "------ create default oauth2 admin user ------"
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@onsemail.com', 'admin2017')" | python oauth2server/manage.py shell
 
