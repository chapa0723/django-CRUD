#!/usr/bin/env bash
set -o errexit
# install dependencies
pip install -r requirements.txt 
<<<<<<< HEAD
#pip install psycopg2-binary
# make migrations
python manage.py makemigrations 
python manage.py migrate 
# recolectar archivos estáticos
python manage.py collectstatic --noinput
# definir credenciales de superusuario
export DJANGO_SUPERUSER_USERNAME=david
=======
pip install psycopg2-binary
# make migrations
python manage.py makemigrations 
python manage.py migrate 
# definir credenciales de superusuario
export DJANGO_SUPERUSER_USERNAME=david 
>>>>>>> 61463ff4fca98f874846df469dc5eba6d309b223
export DJANGO_SUPERUSER_EMAIL=david@david.com
export DJANGO_SUPERUSER_PASSWORD=david
# crear superusuario
python manage.py createsuperuser --no-input


