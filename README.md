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

#### 3. Instalar y Configurar Gunicorn

**Instalar Gunicorn:**

```bash
# En el entorno virtual del proyecto
pip install gunicorn

# Agregar a requirements.txt
echo "gunicorn==21.2.0" >> requirements.txt
```

#### 4. Configurar Gunicorn

Crear archivo de configuración de Gunicorn en la raíz del proyecto:

```bash
nano gunicorn.conf.py
```

**Contenido del archivo:**

```python
# gunicorn.conf.py
import multiprocessing

# Configuración básica
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # Fórmula recomendada
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
preload_app = True

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Proceso
daemon = False
pidfile = "/var/run/gunicorn-task.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# Hooks
def on_starting(server):
    server.log.info("Servidor Gunicorn iniciado")

def on_reload(server):
    server.log.info("Recargando configuración")

def worker_int(worker):
    worker.log.info("Worker recibe señal INT o QUIT")

def pre_fork(server, worker):
    pass

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    pass

def when_ready(server):
    server.log.info("Servidor listo. Spawning workers")
```

**Ejecutar Gunicorn:**

```bash
# Modo básico (testing)
gunicorn djangocrud.wsgi:application

# Usando archivo de configuración
gunicorn djangocrud.wsgi:application -c gunicorn.conf.py

# Modo producción (línea de comandos)
gunicorn djangocrud.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 30 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

#### 5. Crear Servicio Systemd

Crear archivo de servicio para Gunicorn:

```bash
sudo nano /etc/systemd/system/django-task.service
```

**Contenido (AJUSTAR LAS RUTAS SEGÚN TU PROYECTO):**

```ini
[Unit]
Description=Django Task App - Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/home/usuario/django-CRUD
ExecStart=/home/usuario/django-CRUD/env/bin/gunicorn \
    --config /home/usuario/django-CRUD/gunicorn.conf.py \
    djangocrud.wsgi:application

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Activar y gestionar el servicio:**

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable django-task.service

# Iniciar el servicio
sudo systemctl start django-task

# Ver estado
sudo systemctl status django-task

# Ver logs
sudo journalctl -u django-task -f
```

**Comandos útiles del servicio:**

```bash
# Reiniciar
sudo systemctl restart django-task

# Parar
sudo systemctl stop django-task

# Ver logs en tiempo real
sudo journalctl -u django-task -f --lines=50

# Verificar puerto
sudo netstat -tlnp | grep 8000
```

#### 6. Verificación del Despliegue

Verificar que todo funciona correctamente:

```bash
# 1. Verificar que Gunicorn está corriendo
ps aux | grep gunicorn

# 2. Probar la aplicación
curl http://127.0.0.1:8000/

# 3. Verificar logs
tail -f /var/log/gunicorn-task.log

# 4. Verificar procesos
sudo systemctl status django-task
```

#### 7. Optimización de Gunicorn

**Determinar número óptimo de workers:**

```bash
# Verificar CPUs disponibles
nproc

# Fórmula: (2 x CPUs) + 1
# Ejemplo: 4 CPUs = 9 workers

# Para producción con muchos usuarios
workers = 8
threads = 2
worker_class = "gthread"
```

**Archivo de configuración optimizado:**

```python
# gunicorn.conf.py - Producción
import multiprocessing

bind = "127.0.0.1:8000"
workers = 8
threads = 2
worker_class = "gthread"
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/var/log/gunicorn-task-access.log"
errorlog = "/var/log/gunicorn-task-error.log"
loglevel = "info"

# PID
pidfile = "/var/run/gunicorn-task.pid"
```

#### 8. Configurar Logs

Para gestionar logs de Gunicorn con logrotate:

```bash
sudo nano /etc/logrotate.d/gunicorn-task
```

**Contenido:**

```
/var/log/gunicorn-task-*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload django-task > /dev/null
    endscript
}
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