# 🧩 Proyecto Django - Tareas App

Este proyecto utiliza **Django** y un entorno virtual de **Python** para gestionar tus tareas.  
A continuación se detallan los pasos para preparar el entorno y ejecutar la aplicación localmente.

---

## 🚀 Configuración inicial

### 1️⃣ Crear el entorno virtual
Desde la raíz del proyecto (donde está `manage.py`):

```bash
$ virtualenv env
```

### 2️⃣ Activar el entorno virtual

```bash
$ source env/bin/activate
```

#### 💡 En Windows sería:

```bash
env\Scripts\activate
```

### 3️⃣ Instalar los requerimientos del proyecto

```bash
$ pip install -r requirements.txt
```

### 🧱 Migraciones de la base de datos

Ejecutá las migraciones para preparar la base de datos local:

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

### 🧭 Ejecutar el servidor de desarrollo

Una vez listo, levantá el servidor con:

```bash
$ python manage.py runserver
```

Abrí tu navegador y accedé a:
👉 http://127.0.0.1:8000/

### 🧰 Notas adicionales

Asegurate de tener Python 3.8+ instalado.

Si el entorno no activa correctamente, verificá que virtualenv esté instalado:

```bash
pip install virtualenv
```

---

## 🔒 Configuración SSL/HTTPS para Producción

### Objetivo

Configurar certificados SSL para hacer funcionar la aplicación bajo HTTPS en el dominio **task.yacaresoft.com**.

### Opción 1: Usando Let's Encrypt (Recomendado - Certificados Gratuitos)

#### 1. Instalar Certbot (Let's Encrypt)

En el servidor:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# O si usas Nginx por separado
sudo apt-get install certbot
```

#### 2. Generar el Certificado SSL

```bash
sudo certbot certonly --standalone -d task.yacaresoft.com -d www.task.yacaresoft.com
```

Los certificados se guardarán en:
- **Certificado**: `/etc/letsencrypt/live/task.yacaresoft.com/fullchain.pem`
- **Clave Privada**: `/etc/letsencrypt/live/task.yacaresoft.com/privkey.pem`

#### 3. Configurar Nginx como Reverse Proxy

Crear archivo de configuración de Nginx:

```bash
sudo nano /etc/nginx/sites-available/task.yacaresoft.com
```

**Contenido de la configuración:**

```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name task.yacaresoft.com www.task.yacaresoft.com;
    
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS
server {
    listen 443 ssl http2;
    server_name task.yacaresoft.com www.task.yacaresoft.com;
    
    # Ubicación de los certificados SSL
    ssl_certificate /etc/letsencrypt/live/task.yacaresoft.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/task.yacaresoft.com/privkey.pem;
    
    # Configuración SSL recomendada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Seguridad adicional
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Upload de archivos grandes (si es necesario)
    client_max_body_size 10M;
    
    # Archivos estáticos
    location /static/ {
        alias /ruta/a/tu/proyecto/staticfiles/;
    }
    
    # Archivos de media (avatars, etc.)
    location /media/ {
        alias /ruta/a/tu/proyecto/media/;
    }
    
    # Proxy a Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSockets (si es necesario)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 4. Activar la Configuración de Nginx

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/task.yacaresoft.com /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

#### 5. Configurar Renovación Automática

Los certificados de Let's Encrypt expiran cada 90 días. Configurar renovación automática:

```bash
sudo certbot renew --dry-run
```

Agregar a crontab (renovación cada 12 horas):

```bash
sudo crontab -e

# Agregar esta línea:
0 */12 * * * certbot renew --quiet && systemctl reload nginx
```

---

### Opción 2: Usando Certificados SSL Propios

Si ya tienes certificados SSL (.crt y .key):

#### 1. Crear Directorio para Certificados

```bash
sudo mkdir -p /etc/ssl/private/task.yacaresoft.com
```

#### 2. Copiar Certificados

```bash
# Mover certificado
sudo cp tu_certificado.crt /etc/ssl/private/task.yacaresoft.com/fullchain.pem
sudo cp tu_clave_privada.key /etc/ssl/private/task.yacaresoft.com/privkey.pem

# Ajustar permisos
sudo chmod 600 /etc/ssl/private/task.yacaresoft.com/privkey.pem
sudo chown root:root /etc/ssl/private/task.yacaresoft.com/
```

#### 3. Configurar Nginx

Editar el archivo de configuración de Nginx y cambiar las rutas:

```nginx
ssl_certificate /etc/ssl/private/task.yacaresoft.com/fullchain.pem;
ssl_certificate_key /etc/ssl/private/task.yacaresoft.com/privkey.pem;
```

---

### Configuración de Django para HTTPS

#### 1. Actualizar settings.py

En `djangocrud/settings.py`:

```python
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # Cambiar a False en producción

ALLOWED_HOSTS = ['task.yacaresoft.com', 'www.task.yacaresoft.com', '192.168.100.2']

# Configuración para HTTPS
SECURE_SSL_REDIRECT = True  # Redirigir HTTP a HTTPS
SESSION_COOKIE_SECURE = True  # Cookies solo por HTTPS
CSRF_COOKIE_SECURE = True  # CSRF solo por HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'  # Protección clickjacking
SECURE_HSTS_SECONDS = 31536000  # HTTPS Strict Transport Security
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Proxy configuración
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

#### 2. Colectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

#### 3. Ejecutar con Gunicorn (Producción)

Instalar Gunicorn:

```bash
pip install gunicorn
```

Ejecutar la aplicación:

```bash
# Desarrollo (mejor para testing)
gunicorn djangocrud.wsgi:application --bind 127.0.0.1:8000

# Producción (con múltiples workers)
gunicorn djangocrud.wsgi:application --bind 127.0.0.1:8000 --workers 4 --timeout 30
```

Para ejecutar en segundo plano con systemd, crear archivo:

```bash
sudo nano /etc/systemd/system/django-task.service
```

**Contenido:**

```ini
[Unit]
Description=Django Task App Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/ruta/a/tu/proyecto/django-CRUD
Environment="PATH=/ruta/a/tu/proyecto/env/bin"
ExecStart=/ruta/a/tu/proyecto/env/bin/gunicorn djangocrud.wsgi:application --bind 127.0.0.1:8000 --workers 4

[Install]
WantedBy=multi-user.target
```

Activar el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable django-task
sudo systemctl start django-task
sudo systemctl status django-task
```

---

### Archivos de Configuración del Proyecto

#### Ubicación de Certificados SSL en el Proyecto

Los certificados SSL **NO** se colocan dentro del proyecto Django. Se configuran en el servidor web (Nginx/Apache).

**Estructura recomendada:**

```
/etc/
├── ssl/
│   └── private/
│       └── task.yacaresoft.com/
│           ├── fullchain.pem      # Certificado público
│           └── privkey.pem        # Clave privada
└── letsencrypt/
    └── live/
        └── task.yacaresoft.com/
            ├── fullchain.pem
            └── privkey.pem
```

**Archivos de configuración del proyecto Django:**
- `djangocrud/settings.py` - Configuración de Django
- `/etc/nginx/sites-available/task.yacaresoft.com` - Configuración de Nginx

---

### Verificación

Una vez configurado, verificar:

```bash
# Verificar que Nginx está funcionando
sudo systemctl status nginx

# Verificar certificados
sudo certbot certificates

# Probar la conexión SSL
openssl s_client -connect task.yacaresoft.com:443 -servername task.yacaresoft.com
```

Acceder desde el navegador: **https://task.yacaresoft.com**

---

### Resumen de Archivos Modificados

1. ✅ **djangocrud/settings.py** - Configuración SSL de Django
2. ✅ **ALLOWED_HOSTS** - Agregar dominios permitidos
3. ✅ **/etc/nginx/sites-available/task.yacaresoft.com** - Configuración de Nginx
4. ✅ **/etc/letsencrypt/live/task.yacaresoft.com/** - Ubicación de certificados

### Notas Importantes

- Los certificados SSL **NO van dentro del proyecto Django**
- Se configuran en el servidor web (Nginx/Apache)
- En producción, siempre usar `DEBUG = False`
- Colectar archivos estáticos antes de desplegar
- Usar Gunicorn para ejecutar Django en producción