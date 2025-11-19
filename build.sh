#!/usr/bin/env bash
set -o errexit
# install dependencies
pip install -r requirements.txt 
pip install psycopg2-binary
# make migrations
python manage.py makemigrations 
python manage.py migrate 
# definir credenciales de superusuario
export DJANGO_SUPERUSER_USERNAME=david2 
export DJANGO_SUPERUSER_EMAIL=david2@david.com
export DJANGO_SUPERUSER_PASSWORD=david2
# crear superusuario
python manage.py createsuperuser --no-input


