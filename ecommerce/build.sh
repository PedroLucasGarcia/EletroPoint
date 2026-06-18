#!/usr/bin/env bash
# Script de build executado pelo Render antes de arrancar a aplicação

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate