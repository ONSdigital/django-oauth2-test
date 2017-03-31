# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-03-30 13:54
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credentials', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauthclient',
            name='client_id',
            field=models.CharField(help_text=b'This is a unique string used to identify the client', max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='oauthclient',
            name='redirect_uri',
            field=models.URLField(default=b'http://www.example.com', help_text=b'This is a unique URI to describe the callback used by the OAuth2 server', max_length=254, validators=[django.core.validators.URLValidator]),
        ),
    ]
