#!/usr/bin/env bash
set -o errexit

# Verificar que estamos en render.com y no en un entorno de desarrollo
if [ -z "$RENDER" ] && [ -z "$RENDER_EXTERNAL_HOSTNAME" ]; then
    echo "Este script solo debe ejecutarse en render.com"
    exit 1
fi

# Verificar que no estamos intentando ejecutar en /dev/
if [[ "$PWD" == /dev/* ]] || [[ "$(pwd)" == /dev/* ]]; then
    echo "Error: No se puede ejecutar en el directorio /dev/"
    exit 1
fi

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


