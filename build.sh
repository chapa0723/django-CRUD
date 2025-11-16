#!/bin/bash
# install dependencies
pip install -r requirements.txt 
# make migrations
python manage.py makemigrations 
python manage.py migrate 
# definir credenciales de superusuario
export DJANGO_SUPERUSER_USERNAME=david 
export DJANGO_SUPERUSER_EMAIL=david@david.com
export DJANGO_SUPERUSER_PASSWORD=david
# crear superusuario
python manage.py createsuperuser --no-input


