#!/usr/bin/env bash
set -e

python oauth2server/manage.py loaddata oauth2server/apps/credentials/fixtures/ons_credentials.json