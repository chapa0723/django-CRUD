# gunicorn.conf.py
# Configuración de Gunicorn para producción

import multiprocessing
<<<<<<< HEAD
import os

# Configuración básica
# Render proporciona la variable PORT, si no existe usa 8000 por defecto
port = os.environ.get('PORT', '8000')
bind = f"0.0.0.0:{port}"
=======

# Configuración básica
bind = "127.0.0.1:8000"
>>>>>>> 61463ff4fca98f874846df469dc5eba6d309b223
workers = multiprocessing.cpu_count() * 2 + 1  # Fórmula recomendada: (2 x CPUs) + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50  # Variación aleatoria para evitar que todos los workers se reinicien al mismo tiempo
timeout = 30
keepalive = 5
preload_app = True  # Cargar la app antes de forkar workers (ahorra memoria)

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Proceso
daemon = False
pidfile = "/var/run/gunicorn-task.pid"
umask = 0
user = None  # Dejar que systemd maneje el usuario
group = None
tmp_upload_dir = None

# Hooks para debugging y monitoreo
def on_starting(server):
    """Se ejecuta al iniciar el servidor"""
    server.log.info("Servidor Gunicorn iniciado")

def on_reload(server):
    """Se ejecuta al recargar la configuración"""
    server.log.info("Recargando configuración")

def worker_int(worker):
    """Se ejecuta cuando un worker recibe una señal INT o QUIT"""
    worker.log.info("Worker recibió señal INT o QUIT")

def pre_fork(server, worker):
    """Se ejecuta antes de crear un worker"""
    pass

def post_fork(server, worker):
    """Se ejecuta después de crear un worker"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Se ejecuta después de inicializar un worker"""
    pass

def when_ready(server):
    """Se ejecuta cuando el servidor está listo"""
    server.log.info("Servidor listo. Spawning workers")

