#!/usr/bin/env bash
set -e
./init_db.sh
python oauth2server/manage.py runserver 0.0.0.0:8040
