# CaféMap FUSA - Sistema de Gestión Digital para Cafeterías

## Descripción del Proyecto
CaféMap FUSA es una aplicación web desarrollada con Python Flask que digitaliza la gestión de cafeterías en el municipio de Fusagasugá. El sistema integra tres roles principales (Developer, Administrador y Cliente) permitiendo la gestión completa de establecimientos, menús, descuentos y un innovador sistema de fidelización basado en códigos QR.

## Características Principales
- **Gestión Administrativa Completa**: CRUD de cafeterías, menús y descuentos con control de permisos
- **Geolocalización Interactiva**: Mapa con Leaflet.js mostrando todas las cafeterías del municipio
- **Sistema de Fidelización con QR**: Registro de visitas mediante códigos QR únicos por establecimiento
- **Gamificación**: Programa de puntos y certificados digitales en PDF
- **Valoraciones**: Sistema de reseñas y calificaciones de 1 a 5 estrellas
- **Autenticación Segura**: Tres roles diferenciados con hash de contraseñas PBKDF2-SHA256

## Tecnologías Utilizadas

### Backend
- Python 3.9+
- Flask 2.3 (Framework web)
- PyMySQL (Conexión a base de datos)
- Werkzeug (Seguridad y hash de contraseñas)

### Frontend
- HTML5
- CSS3 / Tailwind CSS
- JavaScript
- Jinja2 (Motor de plantillas)
- Leaflet.js (Mapas interactivos)

### Base de Datos
- MySQL 8.0+
- Modelo relacional con 7 tablas principales

### Librerías Especiales
- QRCode: Generación de códigos QR únicos
- Pillow: Procesamiento de imágenes
- ReportLab: Generación de certificados PDF

## Requisitos Previos
Antes de instalar el proyecto, asegúrate de tener instalado:
- Python 3.9 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)
- Navegador web moderno (Chrome 90+, Firefox 88+, Edge 90+)

## Instalación

### 1. Clonar o Descomprimir el Proyecto
```bash
# Si lo descargas del .zip
unzip RetoIngenieria_HectorGodoy_LuisHerran.zip
cd RetoIngenieria_HectorGodoy_LuisHerran
```

### 2. Instalar XAMPP (si no lo tienes)
- Descarga XAMPP desde: https://www.apachefriends.org/
- Instala y ejecuta los módulos Apache y MySQL

### 3. Configurar la Base de Datos
```bash
# Abre el panel de XAMPP y inicia MySQL
# Accede a phpMyAdmin: http://localhost/phpmyadmin

# Crea la base de datos
CREATE DATABASE fusa_cafes;

# Importar el archivo SQL
# En phpMyAdmin, selecciona la base de datos 'fusa_cafes'
# Ve a la pestaña 'Importar' y selecciona el archivo: database/fusa_cafes.sql
```

### 4. Crear Entorno Virtual de Python (Recomendado)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 5. Instalar Dependencias de Python
```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` debe contener:
```
Flask==2.3.0
PyMySQL==1.1.0
Werkzeug==2.3.0
qrcode==7.4.2
Pillow==10.0.0
reportlab==4.0.4
```

### 6. Configurar la Aplicación
Edita el archivo `app.py` o crea un archivo `.env` con las credenciales de tu base de datos:

```python
# Configuración de la base de datos
app.config['DB_HOST'] = 'localhost'
app.config['DB_USER'] = 'root'
app.config['DB_PASSWORD'] = ''  # Tu contraseña de MySQL
app.config['DB_NAME'] = 'fusa_cafes'
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
```

### 7. Ejecutar la Aplicación
```bash
python app.py
```

O si tienes configurado Flask:
```bash
flask run
```

### 8. Acceder a la Aplicación
Abre tu navegador y visita:
```
http://localhost:5000
```

## Estructura del Proyecto
```
CafeMapFUSA/
├── app.py                      # Archivo principal de la aplicación
├── requirements.txt            # Dependencias de Python
├── database/
│   └── cafemap_fusa.sql       # Script SQL de la base de datos
├── static/                    # Archivos estáticos
│   ├── images/                # Imágenes
│   └── certificados/          # Certificados generados
├── templates/                 # Plantillas HTML (Jinja2)
│   ├── login.html
│   ├── register.html
│   ├── dashboard_client.html
│   ├── dashboard_admin.html
│   ├── dashboard_developer.html
│   ├── map.html
│   └── ...
├── certificates/              # Certificados PDF generados
├── docs/                      # Documentación
│   ├── CaféMap_FUSA.pdf
└── README.md                  # Este archivo
```

## Uso del Sistema

### Roles y Funcionalidades

#### 🔧 Developer (Desarrollador)
- Acceso total al sistema
- Gestión de todos los usuarios y roles
- Visualización de estadísticas globales
- Panel de administración completo

#### 👨‍💼 Administrador
- Gestión de su(s) cafetería(s)
- CRUD de menús y productos
- CRUD de descuentos y promociones
- Generación de códigos QR por cafetería
- Visualización de estadísticas de visitas
- Revisión de valoraciones

#### 👤 Cliente
- Visualización del mapa con todas las cafeterías
- Consulta de menús y descuentos
- Escaneo de códigos QR para registrar visitas
- Acumulación de puntos de fidelización
- Generación de certificados digitales
- Sistema de valoraciones y reseñas

### Funcionalidad Principal: Sistema de Fidelización

#### Para Clientes:
1. Iniciar sesión en el dashboard
2. Visitar una cafetería física
3. Escanear el código QR único del establecimiento
4. El sistema valida y registra la visita (máximo 1 por día por cafetería)
5. Cada 5 visitas acumuladas = 1 punto
6. Con los puntos puedes generar certificados digitales en PDF

#### Para Administradores:
1. Crear/editar información de tu cafetería
2. Agregar productos al menú con precios
3. Crear descuentos con fechas de vigencia
4. Generar el código QR de tu cafetería
5. Imprimir y colocar el QR en un lugar visible
6. Revisar estadísticas de visitas y valoraciones

## Credenciales de Prueba

### Developer
```
Usuario: lfherran@ucundinmarca.edu.co
Contraseña: 12345
```

### Administrador (Ejemplo)
```
Usuario: hagodoy@ucundinmarca.edu.co
Contraseña: 12345
```

### Cliente (Ejemplo)
```
Usuario: luis@a.com
Contraseña: 12345
```

**Nota:** Cambia estas contraseñas en producción.

## Solución de Problemas Comunes

### Error de Conexión a la Base de Datos
**Problema:** `Can't connect to MySQL server`
**Solución:**
- Verifica que XAMPP esté ejecutando MySQL
- Confirma las credenciales en `app.py`
- Asegúrate de que el puerto 3306 esté disponible

### Error al Importar Módulos
**Problema:** `ModuleNotFoundError: No module named 'flask'`
**Solución:**
```bash
# Activa el entorno virtual primero
venv\Scripts\activate
# Reinstala las dependencias
pip install -r requirements.txt
```

### El Mapa No Se Carga
**Problema:** Leaflet.js no muestra el mapa
**Solución:**
- Verifica tu conexión a internet (requiere CDN)
- Revisa la consola del navegador (F12) para errores
- Asegúrate de tener coordenadas válidas en las cafeterías

### Los Códigos QR No Se Generan
**Problema:** Error al crear QR
**Solución:**
```bash
# Verifica que Pillow esté instalado correctamente
pip install --upgrade Pillow qrcode
# Asegúrate de que la carpeta static/qr_codes/ exista
```

### Error al Generar Certificados PDF
**Problema:** Error con ReportLab
**Solución:**
```bash
pip install --upgrade reportlab
# Verifica permisos de escritura en la carpeta certificates/
```

## Características de Seguridad

- **Hash de contraseñas**: PBKDF2-SHA256 con Werkzeug
- **Sesiones seguras**: Cookies con claves secretas
- **Validación de permisos**: Control de acceso por rol en cada ruta
- **Protección SQL Injection**: Consultas parametrizadas con PyMySQL
- **Validación de datos**: Formularios HTML5 y validación backend

## Limitaciones Conocidas

- Requiere conexión a internet para funcionalidad completa
- La geolocalización necesita coordenadas manuales
- Solo permite 1 visita por cafetería al día
- No incluye sistema de pedidos en línea
- No incluye pasarela de pagos


## Autores

**Héctor Andrés Godoy**
- Universidad de Cundinamarca
- Programa: Ingeniería Electrónica

**Luis Felipe Herran Paz**
- Universidad de Cundinamarca
- Programa: Ingeniería Electrónica

## Fecha de Entrega
30 de Octubre de 2025

## Licencia
Este proyecto fue desarrollado con fines académicos para el Reto de Ingeniería de la Universidad de Cundinamarca.



---
**CaféMap FUSA** - Modernizando la gestión de cafeterías universitarias
*Reto de Ingeniería - Universidad de Cundinamarca - 2025*
