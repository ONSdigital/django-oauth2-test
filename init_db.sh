#!/bin/sh

# This shell script is run once when pushing an application to cloud foundry. It's needed to create a super user on the
# OAuth2 (django) server - which happens only once.
# You can find out more about creating super users on django here: https://docs.djangoproject.com/en/1.11/intro/tutorial02/
#
# To run this script to your cloud foundry application from the cli command you can do:
#   /> cf push my_app_name  -c “bash ./init_db.sh"
# To set the start command to 'null' again you can do:
#   /> cf push my_app_name -c "null"
# To find out more go here: https://docs.cloudfoundry.org/devguide/deploy-apps/start-restart-restage.html

echo "------ Create database tables ------"
python oauth2server/manage.py migrate --noinput
 
# This line will create a super user only if they don't exist. It's needed for startup, and will only create the user at startup
echo "------ create default oauth2 admin user ------"
#echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@onsemail.com', 'admin2017')" | python oauth2server/manage.py shell
#echo "from django.contrib.auth.models import User;if not User.objects.filter(username="admin").exists():User.objects.create_superuser('admin', 'admin@onsemail.com', 'admin2017')" | python oauth2server/manage.py shell

echo "from django.contrib.auth.models import User;User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@onsemail.com', 'admin2017')" | python oauth2server/manage.py shell