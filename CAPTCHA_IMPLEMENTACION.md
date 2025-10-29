# Implementación de CAPTCHA

## Resumen

Se ha implementado CAPTCHA en los formularios de registro y login para proteger contra bots y ataques automatizados.

## Características Implementadas

### 1. **Protección con CAPTCHA**

- ✅ CAPTCHA en registro de usuarios (`/signup/`)
- ✅ CAPTCHA en login de usuarios (`/signin/`)
- ✅ Validación automática de CAPTCHA
- ✅ Mensajes de error informativos
- ✅ Diseño integrado con Bootstrap

### 2. **Tecnología Utilizada**

**django-simple-captcha** v0.6.2
- Librería ligera y fácil de implementar
- Genera imágenes CAPTCHA automáticamente
- No requiere servicios externos
- Completamente configurable

## Instalación Realizada

```bash
pip install django-simple-captcha Pillow
```

### Dependencias Agregadas:
- `django-simple-captcha==0.6.2`
- `Pillow==12.0.0` (para generar imágenes)
- `django-ranged-response==0.2.0`

## Configuración

### 1. Settings.py

Se agregó `captcha` a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'captcha',
    'tasks',
    'users',
]
```

### 2. URLs

Se incluyeron las URLs de CAPTCHA:

```python
urlpatterns = [
    ...
    path('captcha/', include('captcha.urls')),
]
```

### 3. Migraciones

Las tablas de CAPTCHA se crearon con:

```bash
python manage.py migrate
```

Se aplicaron las migraciones:
- `captcha.0001_initial`
- `captcha.0002_alter_captchastore_id`

## Archivos Creados/Modificados

### 1. `tasks/auth_forms.py` (NUEVO)

Formularios personalizados con CAPTCHA:

- **SignUpForm**: Formulario de registro con campo CAPTCHA
- **SignInForm**: Formulario de login con campo CAPTCHA

```python
from captcha.fields import CaptchaField

class SignUpForm(UserCreationForm):
    captcha = CaptchaField(
        label='CAPTCHA',
        help_text='Ingresa el código que ves en la imagen'
    )
    ...
```

### 2. `tasks/views.py` (MODIFICADO)

Vistas actualizadas para usar los nuevos formularios:

- `signup()`: Usa `SignUpForm` con validación de CAPTCHA
- `signin()`: Usa `SignInForm` con validación de CAPTCHA

### 3. `tasks/templates/signup.html` (MODIFICADO)

Template actualizado para mostrar:
- Campos del formulario con Bootstrap
- Campo CAPTCHA con imagen
- Mensajes de error específicos

### 4. `tasks/templates/signin.html` (MODIFICADO)

Template actualizado para mostrar:
- Campos del formulario con Bootstrap
- Campo CAPTCHA con imagen
- Mensajes de error específicos

### 5. `djangocrud/urls.py` (MODIFICADO)

Agregadas URLs para CAPTCHA.

### 6. `djangocrud/settings.py` (MODIFICADO)

Agregado `captcha` a INSTALLED_APPS.

### 7. `requirements.txt` (MODIFICADO)

Agregadas dependencias de CAPTCHA.

## Funcionamiento

### Flujo de Registro

1. Usuario accede a `/signup/`
2. Se muestra formulario con campos:
   - Nombre de usuario
   - Contraseña
   - Confirmar contraseña
   - CAPTCHA (imagen con texto)
3. Usuario completa todos los campos
4. Al enviar, el formulario valida:
   - ✅ Username único
   - ✅ Contraseñas coinciden
   - ✅ CAPTCHA correcto
5. Si todo es válido: Usuario creado y logueado automáticamente

### Flujo de Login

1. Usuario accede a `/signin/`
2. Se muestra formulario con campos:
   - Nombre de usuario
   - Contraseña
   - CAPTCHA (imagen con texto)
3. Usuario completa todos los campos
4. Al enviar, el formulario valida:
   - ✅ Credenciales correctas
   - ✅ CAPTCHA correcto
5. Si todo es válido: Usuario logueado

### Validación de CAPTCHA

- El CAPTCHA se genera aleatoriamente
- Tiene un tiempo de expiración
- Se validan contra la base de datos
- Se muestra mensaje de error si es incorrecto

## Mensajes de Error

Si el CAPTCHA es incorrecto:
```
⚠️ CAPTCHA inválido. Por favor, inténtalo de nuevo.
```

Otros errores de formulario se muestran debajo de cada campo correspondiente.

## Características de CAPTCHA

### Visual
- Imagen con texto alfanumérico
- Fondo con ruido y líneas
- Texto distorsionado
- Botón de recarga disponible

### Seguridad
- Expiración automática
- Validación única por sesión
- Protección contra fuerza bruta
- Sin dependencias externas

## Personalización (Opcional)

### Cambiar dificultad

En `settings.py`:

```python
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
CAPTCHA_NOISE_FUNCTIONS = (
    'captcha.helpers.noise_arcs',
    'captcha.helpers.noise_dots',
)
CAPTCHA_LENGTH = 5  # Longitud del código
```

### Cambiar fuente

```python
CAPTCHA_FONT_SIZE = 42
CAPTCHA_LETTER_ROTATION = (-35, 35)
```

## Pruebas

Para probar el CAPTCHA:

1. Ir a `/signup/` o `/signin/`
2. Intentar registrarse/login sin completar CAPTCHA
3. Debe mostrar error
4. Completar CAPTCHA correctamente
5. Debe permitir el registro/login

## Solución de Problemas

### CAPTCHA no se muestra

1. Verificar que las migraciones están aplicadas
2. Verificar que `captcha` está en `INSTALLED_APPS`
3. Verificar que las URLs están configuradas

### Error de PIL/Pillow

```bash
pip install Pillow
```

### Permisos de escritura

CAPTCHA necesita escribir imágenes:
- Verificar permisos de la carpeta del proyecto
- En producción, configurar rutas de almacenamiento

## Archivos de CAPTCHA

Las imágenes CAPTCHA se almacenan temporalmente en:
- Carpeta `.captcha/` en el proyecto
- Se limpian automáticamente

Para ubicar archivos CAPTCHA:
```python
CAPTCHA_CACHE_PREFIX = 'captcha_'
```

## Seguridad Adicional

El CAPTCHA protege contra:
- ✅ Registro masivo de bots
- ✅ Ataques de fuerza bruta en login
- ✅ Spam automatizado
- ✅ Cuentas falsas

**Limitaciones:**
- No protege contra usuarios maliciosos manuales
- No protege si el código CAPTCHA es fácilmente legible
- Se recomienda combinarlo con rate limiting

## Próximas Mejoras Sugeridas

1. **Rate Limiting**: Limitar intentos por IP
2. **reCAPTCHA v3**: CAPTCHA invisible avanzado
3. **CAPTCHA más complejo**: Para mayor seguridad
4. **Notificaciones**: Alertas de intentos fallidos
5. **Logging**: Registrar intentos de acceso

## Referencias

- [django-simple-captcha Docs](https://django-simple-captcha.readthedocs.io/)
- [Django Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)

