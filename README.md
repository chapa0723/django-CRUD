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