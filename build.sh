#!/usr/bin/env bash
set -o errexit
# install dependencies
pip install -r requirements.txt 
pip install psycopg2-binary
# make migrations
python manage.py makemigrations 
python manage.py migrate 

#### Comentar todo esto si el usuario ya fue creado previamente
# definir credenciales de superusuario
#export DJANGO_SUPERUSER_USERNAME=david 
#export DJANGO_SUPERUSER_EMAIL=david@david.com
#export DJANGO_SUPERUSER_PASSWORD=david
# crear superusuario
#python manage.py createsuperuser --no-input


