#!/usr/bin/env python
import os
import sys


def check_env(env):
    if not os.getenv(env):
        print('Missing environmental variable ' + env)
        exit(1)


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings.local')
    check_env('OAUTH2_SUPER_USER')
    check_env('OAUTH2_SUPER_USER_PASSWORD')
    check_env('OAUTH2_SUPER_USER_EMAIL')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
