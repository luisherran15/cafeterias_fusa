# app.py

from flask import Flask, jsonify, render_template, request, redirect, url_for, session, g, send_file, flash
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
from datetime import datetime
from certificado_generator import generar_certificado, verificar_certificado_disponible, registrar_certificado

app = Flask(__name__)
# ¡IMPORTANTE! Cambia esto por una clave larga y aleatoria en producción
app.secret_key = 'tu_clave_super_secreta_aqui_12345' 

# --- CONEXIÓN A LA BASE DE DATOS ---
def get_db_connection():
    # Asegúrate que MySQL/MariaDB esté corriendo en XAMPP
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',         
            password='',         
            database='fusa_cafes', # Usa el nombre de tu BD
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a la BD: {e}")
        return None

# Middleware para cerrar la conexión después de cada solicitud
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- RUTA DE INICIO ---
@app.route('/')
def index():
    cafeterias = []
    
    # Si el usuario NO está logueado, cargar las cafeterías para el mapa
    if 'rol' not in session:
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Obtener todas las cafeterías con sus coordenadas
                    sql = "SELECT nombre, direccion, latitud, longitud FROM cafeterias"
                    cursor.execute(sql)
                    cafeterias_raw = cursor.fetchall()
                    
                    # Convertir Decimal a float para serialización JSON
                    for cafe in cafeterias_raw:
                        cafeterias.append({
                            'nombre': cafe['nombre'],
                            'direccion': cafe['direccion'],
                            'latitud': float(cafe['latitud']) if cafe['latitud'] else 0,
                            'longitud': float(cafe['longitud']) if cafe['longitud'] else 0
                        })
            except Exception as e:
                print(f"Error al cargar cafeterías para index: {e}")
            finally:
                conn.close()
    
    
    # Convertir a JSON para usar en JavaScript
    import json
    cafeterias_json = json.dumps(cafeterias)
    
    return render_template('index.html', session=session, cafeterias_json=cafeterias_json)

# --------------------------
# --- 2. REGISTRO DE USUARIO ---
# --------------------------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        nombre = request.form.get('nombre')
        cafeteria_id = request.form.get('cafeteria_id')  # Para registro de visita
        
        # Si viene cafeteria_id, es un registro de visita
        if cafeteria_id and 'user_id' in session:
            return registrar_visita(cafeteria_id)
        
        # Rol por defecto para el registro público
        rol = 'cliente' 
        
        # Hashear la contraseña por seguridad
        password_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        if conn is None:
            return "Error de conexión a la base de datos.", 500

        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO usuarios (email, password, nombre, rol) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (email, password_hash, nombre, rol))
            
            conn.commit()
            return redirect(url_for('login', mensaje="Registro exitoso. Por favor, inicia sesión."))

        except pymysql.err.IntegrityError:
            # Error común si el email ya existe (UNIQUE)
            return render_template('registro.html', error="El email ya está registrado.")
        
        except Exception as e:
            print(f"Error en el registro: {e}")
            return render_template('registro.html', error="Error al registrar usuario.")
        finally:
            conn.close()

    return render_template('registro.html')

# Función helper para registrar visitas
def registrar_visita(cafeteria_id):
    """Registra una visita de un cliente a una cafetería"""
    if 'user_id' not in session or session.get('rol') != 'cliente':
        return redirect(url_for('login'))
    
    cliente_id = session['user_id']
    conn = get_db_connection()
    
    if conn is None:
        return redirect(url_for('cliente_dashboard', error="Error de conexión a la BD."))
    
    try:
        with conn.cursor() as cursor:
            # Verificar que la cafetería existe
            cursor.execute("SELECT id FROM cafeterias WHERE id = %s", (cafeteria_id,))
            cafeteria = cursor.fetchone()
            
            if not cafeteria:
                return redirect(url_for('cliente_dashboard', error="Cafetería no encontrada."))
            
            # Registrar la visita
            sql = """
                INSERT INTO visitas (cliente_id, cafeteria_id, fecha_visita)
                VALUES (%s, %s, NOW())
            """
            cursor.execute(sql, (cliente_id, cafeteria_id))
            conn.commit()
            
            return redirect(url_for('cliente_dashboard', mensaje="¡Visita registrada exitosamente! +1 punto"))
            
    except pymysql.err.IntegrityError:
        # Ya visitó hoy esta cafetería
        return redirect(url_for('cliente_dashboard', error="Ya registraste una visita a esta cafetería hoy."))
    except Exception as e:
        print(f"Error al registrar visita: {e}")
        return redirect(url_for('cliente_dashboard', error="Error al registrar la visita."))
    finally:
        conn.close()

# -----------------------
# --- 3. INICIO DE SESIÓN ---
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = request.args.get('mensaje') # Mensaje que viene del registro
    error = None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn is None:
            return "Error de conexión a la base de datos.", 500

        try:
            with conn.cursor() as cursor:
                sql = "SELECT id, password, rol, nombre FROM usuarios WHERE email = %s"
                cursor.execute(sql, (email,))
                usuario = cursor.fetchone() 
            
            if usuario and check_password_hash(usuario['password'], password):
                # Sesión exitosa: guardar datos clave en la sesión
                session['user_id'] = usuario['id']
                session['rol'] = usuario['rol']
                session['nombre'] = usuario['nombre']

                # Redirección basada en el rol
                if usuario['rol'] == 'developer':
                    return redirect(url_for('developer_dashboard'))
                elif usuario['rol'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('cliente_dashboard'))

            # Si las credenciales son incorrectas
            error = "Email o contraseña incorrectos."
        
        except Exception as e:
            print(f"Error en el login: {e}")
            error = "Error de autenticación."
        finally:
            conn.close()

    return render_template('login.html', error=error, mensaje=mensaje)

# -----------------
# --- 4. LOGOUT ---
# -----------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('rol', None)
    session.pop('nombre', None)
    return redirect(url_for('index'))

# -----------------------------
# --- 5. DASHBOARDS POR ROL ---
# -----------------------------

# Helper para proteger rutas
def rol_required(rol):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'rol' not in session or session['rol'] != rol:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        # Necesario para que Flask reconozca el nombre de la función
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@app.route('/developer/dashboard')
@rol_required('developer')
def developer_dashboard():
    conn = get_db_connection()
    stats = {
        'total_usuarios': 0,
        'usuarios_developer': 0,
        'usuarios_admin': 0,
        'usuarios_cliente': 0,
        'total_cafeterias': 0,
        'total_menus': 0,
        'total_descuentos': 0,
        'total_visitas': 0,
        'total_valoraciones': 0
    }
    
    if conn:
        try:
            with conn.cursor() as cursor:
                # Total de usuarios
                cursor.execute("SELECT COUNT(*) as total FROM usuarios")
                stats['total_usuarios'] = cursor.fetchone()['total']
                
                # Usuarios por rol
                cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE rol = 'developer'")
                stats['usuarios_developer'] = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE rol = 'admin'")
                stats['usuarios_admin'] = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE rol = 'cliente'")
                stats['usuarios_cliente'] = cursor.fetchone()['total']
                
                # Total de cafeterías
                cursor.execute("SELECT COUNT(*) as total FROM cafeterias")
                stats['total_cafeterias'] = cursor.fetchone()['total']
                
                # Total de productos en menús
                cursor.execute("SELECT COUNT(*) as total FROM menus")
                stats['total_menus'] = cursor.fetchone()['total']
                
                # Total de descuentos
                cursor.execute("SELECT COUNT(*) as total FROM descuentos_bonos")
                stats['total_descuentos'] = cursor.fetchone()['total']
                
                # Total de visitas (si existe la tabla)
                try:
                    cursor.execute("SELECT COUNT(*) as total FROM visitas")
                    stats['total_visitas'] = cursor.fetchone()['total']
                except Exception as e:
                    print(f"Tabla 'visitas' no existe: {e}")
                    stats['total_visitas'] = 0
                
                # Total de valoraciones (si existe la tabla)
                try:
                    cursor.execute("SELECT COUNT(*) as total FROM valoraciones")
                    stats['total_valoraciones'] = cursor.fetchone()['total']
                except Exception as e:
                    print(f"Tabla 'valoraciones' no existe: {e}")
                    stats['total_valoraciones'] = 0
                
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
        finally:
            conn.close()
    
    return render_template('developer_dashboard.html', stats=stats, session=session)

@app.route('/admin/dashboard')
@rol_required('admin')
def admin_dashboard():
    conn = get_db_connection()
    cafeterias = []
    stats = {
        'total_cafeterias': 0,
        'total_menus': 0,
        'total_productos': 0,
        'total_descuentos': 0,
        'total_visitas': 0,
        'total_valoraciones': 0,
        'promedio_valoracion': 0,
        'producto_mas_caro': None,
        'cafeteria_mas_visitada': None
    }
    
    # Manejo de mensaje/error que viene de las acciones de CRUD
    mensaje = request.args.get('mensaje') 
    error = request.args.get('error') 
    
    if conn:
        try:
            with conn.cursor() as cursor:
                admin_id = session['user_id']
                
                # 1. Traer cafeterías del admin
                sql = "SELECT id, nombre, direccion, latitud, longitud FROM cafeterias WHERE admin_id = %s"
                cursor.execute(sql, (admin_id,))
                cafeterias = cursor.fetchall()
                stats['total_cafeterias'] = len(cafeterias)
                
                # 2. Contar total de productos en menús del admin
                sql_menus = """
                    SELECT COUNT(*) as total 
                    FROM menus m 
                    JOIN cafeterias c ON m.cafeteria_id = c.id 
                    WHERE c.admin_id = %s
                """
                cursor.execute(sql_menus, (admin_id,))
                result = cursor.fetchone()
                stats['total_menus'] = result['total'] if result else 0
                stats['total_productos'] = stats['total_menus']  # Alias
                
                # 3. Producto más caro
                try:
                    sql_producto_caro = """
                        SELECT m.nombre, m.precio
                        FROM menus m
                        JOIN cafeterias c ON m.cafeteria_id = c.id
                        WHERE c.admin_id = %s
                        ORDER BY m.precio DESC
                        LIMIT 1
                    """
                    cursor.execute(sql_producto_caro, (admin_id,))
                    producto_caro = cursor.fetchone()
                    if producto_caro:
                        stats['producto_mas_caro'] = {
                            'nombre': producto_caro['nombre'],
                            'precio': float(producto_caro['precio'])
                        }
                except Exception as e:
                    print(f"Error al obtener producto más caro: {e}")
                
                # 4. Contar total de descuentos del admin
                sql_descuentos = """
                    SELECT COUNT(*) as total 
                    FROM descuentos_bonos d 
                    JOIN cafeterias c ON d.cafeteria_id = c.id 
                    WHERE c.admin_id = %s
                """
                cursor.execute(sql_descuentos, (admin_id,))
                result = cursor.fetchone()
                stats['total_descuentos'] = result['total'] if result else 0
                
                # 5. Total de visitas (si existe la tabla)
                try:
                    sql_visitas = """
                        SELECT COUNT(*) as total
                        FROM visitas v
                        JOIN cafeterias c ON v.cafeteria_id = c.id
                        WHERE c.admin_id = %s
                    """
                    cursor.execute(sql_visitas, (admin_id,))
                    result = cursor.fetchone()
                    stats['total_visitas'] = result['total'] if result else 0
                except Exception as e:
                    print(f"Tabla 'visitas' no existe: {e}")
                    stats['total_visitas'] = 0
                
                # 6. Cafetería más visitada
                try:
                    sql_cafe_visitada = """
                        SELECT c.nombre, COUNT(*) as visitas
                        FROM visitas v
                        JOIN cafeterias c ON v.cafeteria_id = c.id
                        WHERE c.admin_id = %s
                        GROUP BY c.id, c.nombre
                        ORDER BY visitas DESC
                        LIMIT 1
                    """
                    cursor.execute(sql_cafe_visitada, (admin_id,))
                    cafe_visitada = cursor.fetchone()
                    if cafe_visitada:
                        stats['cafeteria_mas_visitada'] = {
                            'nombre': cafe_visitada['nombre'],
                            'visitas': cafe_visitada['visitas']
                        }
                except Exception as e:
                    print(f"Error al obtener cafetería más visitada: {e}")
                
                # 7. Valoraciones (si existe la tabla)
                try:
                    sql_valoraciones = """
                        SELECT COUNT(*) as total, AVG(puntuacion) as promedio
                        FROM valoraciones v
                        JOIN cafeterias c ON v.cafeteria_id = c.id
                        WHERE c.admin_id = %s
                    """
                    cursor.execute(sql_valoraciones, (admin_id,))
                    result = cursor.fetchone()
                    if result:
                        stats['total_valoraciones'] = result['total'] if result['total'] else 0
                        stats['promedio_valoracion'] = round(float(result['promedio']), 1) if result['promedio'] else 0
                except Exception as e:
                    print(f"Tabla 'valoraciones' no existe: {e}")
                    stats['total_valoraciones'] = 0
                    stats['promedio_valoracion'] = 0
                
        except Exception as e:
            print(f"Error al obtener cafeterías: {e}")
            error = "Error al cargar la lista de cafeterías."
        finally:
            conn.close()
            
    return render_template('admin_dashboard.html', cafeterias=cafeterias, stats=stats, mensaje=mensaje, error=error, session=session)

@app.route('/admin/cafeteria/crear', methods=['POST'])
@rol_required('admin')
def crear_cafeteria():
    # Solo procesamos la solicitud POST
    nombre = request.form.get('nombre')
    direccion = request.form.get('direccion')
    latitud = request.form.get('latitud')
    longitud = request.form.get('longitud')
    admin_id = session['user_id'] # Clave para la seguridad

    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('admin_dashboard', error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO cafeterias (admin_id, nombre, direccion, latitud, longitud)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (admin_id, nombre, direccion, latitud, longitud))
        
        conn.commit()
        return redirect(url_for('admin_dashboard', mensaje="Cafetería creada con éxito."))

    except Exception as e:
        print(f"Error al crear cafetería: {e}")
        return redirect(url_for('admin_dashboard', error="Error al guardar la cafetería."))
    finally:
        if conn: conn.close()
        
# ----------------------------------------------------
# --- RUTAS DE EDICIÓN, ACTUALIZACIÓN Y ELIMINACIÓN ---
# ----------------------------------------------------

@app.route('/admin/cafeteria/editar/<int:id>', methods=['GET'])
@rol_required('admin')
def editar_cafeteria(id):
    conn = get_db_connection()
    cafeteria = None
    
    if conn:
        try:
            with conn.cursor() as cursor:
                # Traer la cafetería Y verificar que pertenezca al administrador logueado
                sql = "SELECT id, nombre, direccion, latitud, longitud FROM cafeterias WHERE id = %s AND admin_id = %s"
                cursor.execute(sql, (id, session['user_id']))
                cafeteria = cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar cafetería para editar: {e}")
        finally:
            if conn: conn.close()

    if not cafeteria:
        # Si no existe la cafetería o no pertenece al admin, redirigir con error
        return redirect(url_for('admin_dashboard', error="Cafetería no encontrada o acceso denegado."))
    
    return render_template('admin_editar_cafeteria.html', cafeteria=cafeteria)


@app.route('/admin/cafeteria/actualizar/<int:id>', methods=['POST'])
@rol_required('admin')
def actualizar_cafeteria(id):
    nombre = request.form.get('nombre')
    direccion = request.form.get('direccion')
    latitud = request.form.get('latitud')
    longitud = request.form.get('longitud')
    
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('admin_dashboard', error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            # Importante: Actualizar SOLO si el admin_id coincide con el usuario logueado
            sql = """
                UPDATE cafeterias SET nombre = %s, direccion = %s, latitud = %s, longitud = %s
                WHERE id = %s AND admin_id = %s
            """
            cursor.execute(sql, (nombre, direccion, latitud, longitud, id, session['user_id']))
        
        conn.commit()
        return redirect(url_for('admin_dashboard', mensaje="Cafetería actualizada con éxito."))

    except Exception as e:
        print(f"Error al actualizar cafetería: {e}")
        return redirect(url_for('admin_dashboard', error="Error al actualizar la cafetería."))
    finally:
        if conn: conn.close()


@app.route('/admin/cafeteria/eliminar/<int:id>', methods=['POST'])
@rol_required('admin')
def eliminar_cafeteria(id):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('admin_dashboard', error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            # 1. Seguridad: Verificar propiedad antes de eliminar
            sql = "DELETE FROM cafeterias WHERE id = %s AND admin_id = %s"
            cursor.execute(sql, (id, session['user_id']))
            
        # 2. Manejar las Claves Foráneas (Asumiendo que no hay CASCADE o que ya se borró lo asociado)
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return redirect(url_for('admin_dashboard', mensaje="Cafetería eliminada con éxito."))
        else:
            return redirect(url_for('admin_dashboard', error="No se encontró la cafetería o acceso denegado."))

    except Exception as e:
        print(f"Error al eliminar cafetería: {e}")
        return redirect(url_for('admin_dashboard', error=f"Error al eliminar (posiblemente hay menús o visitas asociadas)."))
    finally:
        if conn: conn.close()

# ----------------------------------------------------
# --- GESTIÓN DE MENÚS ---
# ----------------------------------------------------

@app.route('/admin/menu/gestion/<int:cafeteria_id>', methods=['GET'])
@rol_required('admin')
def gestion_menus(cafeteria_id):
    conn = get_db_connection()
    menus = []
    cafeteria = None
    mensaje = request.args.get('mensaje')
    error = request.args.get('error')
    
    if conn:
        try:
            with conn.cursor() as cursor:
                # 1. VERIFICACIÓN DE SEGURIDAD:
                # Asegúrate de que esta cafetería pertenezca al admin logueado.
                sql_check = "SELECT admin_id, nombre FROM cafeterias WHERE id = %s"
                cursor.execute(sql_check, (cafeteria_id,))
                cafeteria = cursor.fetchone()
                
                if not cafeteria or cafeteria['admin_id'] != session['user_id']:
                    return redirect(url_for('admin_dashboard', error="Acceso denegado al menú."))
                
                # 2. Si es válido, trae todos los menús de esa cafetería - USAR nombre_plato
                sql_menus = "SELECT id, nombre_plato as nombre, descripcion, precio FROM menus WHERE cafeteria_id = %s"
                cursor.execute(sql_menus, (cafeteria_id,))
                menus = cursor.fetchall()
                
        except Exception as e:
            print(f"Error al obtener menús: {e}")
            error = "Error al cargar los menús."
        finally:
            conn.close()
    
    return render_template('admin_gestion_menus.html', 
                         cafeteria=cafeteria,
                         menus=menus, 
                         cafeteria_id=cafeteria_id,
                         mensaje=mensaje,
                         error=error)


@app.route('/admin/menu/crear/<int:cafeteria_id>', methods=['POST'])
@rol_required('admin')
def crear_menu(cafeteria_id):
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('gestion_menus', cafeteria_id=cafeteria_id, error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            # 1. VERIFICACIÓN DE SEGURIDAD (Es importante repetir la verificación en la acción POST)
            sql_check = "SELECT admin_id FROM cafeterias WHERE id = %s"
            cursor.execute(sql_check, (cafeteria_id,))
            cafeteria = cursor.fetchone()
            
            if not cafeteria or cafeteria['admin_id'] != session['user_id']:
                return redirect(url_for('admin_dashboard', error="Intento de creación no autorizado."))
            
            # 2. Insertar el nuevo producto - USAR nombre_plato
            sql = """
                INSERT INTO menus (cafeteria_id, nombre_plato, descripcion, precio)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (cafeteria_id, nombre, descripcion, precio))
        
        conn.commit()
        return redirect(url_for('gestion_menus', cafeteria_id=cafeteria_id, mensaje="Producto creado con éxito."))

    except Exception as e:
        print(f"Error al crear menú: {e}")
        return redirect(url_for('gestion_menus', cafeteria_id=cafeteria_id, error="Error al guardar el producto."))
    finally:
        if conn: conn.close()


@app.route('/admin/menu/editar/<int:id>', methods=['GET'])
@rol_required('admin')
def editar_menu(id):
    conn = get_db_connection()
    menu = None
    
    if conn:
        try:
            with conn.cursor() as cursor:
                # Traer el menú y verificar propiedad a través de la cafetería - USAR nombre_plato
                sql = """
                    SELECT m.id, m.nombre_plato as nombre, m.descripcion, m.precio, m.cafeteria_id, c.admin_id
                    FROM menus m
                    INNER JOIN cafeterias c ON m.cafeteria_id = c.id
                    WHERE m.id = %s
                """
                cursor.execute(sql, (id,))
                menu = cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar menú para editar: {e}")
        finally:
            if conn: conn.close()

    if not menu or menu['admin_id'] != session['user_id']:
        return redirect(url_for('admin_dashboard', error="Menú no encontrado o acceso denegado."))
    
    return render_template('admin_editar_menu.html', menu=menu)


@app.route('/admin/menu/actualizar/<int:id>', methods=['POST'])
@rol_required('admin')
def actualizar_menu(id):
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    precio = request.form.get('precio')
    
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('admin_dashboard', error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            # Verificar propiedad antes de actualizar
            sql_check = """
                SELECT m.cafeteria_id, c.admin_id
                FROM menus m
                INNER JOIN cafeterias c ON m.cafeteria_id = c.id
                WHERE m.id = %s
            """
            cursor.execute(sql_check, (id,))
            menu = cursor.fetchone()
            
            if not menu or menu['admin_id'] != session['user_id']:
                return redirect(url_for('admin_dashboard', error="Acceso denegado."))
            
            # Actualizar el menú - USAR nombre_plato
            sql = """
                UPDATE menus SET nombre_plato = %s, descripcion = %s, precio = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nombre, descripcion, precio, id))
        
        conn.commit()
        return redirect(url_for('gestion_menus', cafeteria_id=menu['cafeteria_id'], mensaje="Producto actualizado con éxito."))

    except Exception as e:
        print(f"Error al actualizar menú: {e}")
        return redirect(url_for('admin_dashboard', error="Error al actualizar el producto."))
    finally:
        if conn: conn.close()


@app.route('/admin/menu/eliminar/<int:id>', methods=['POST'])
@rol_required('admin')
def eliminar_menu(id):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('admin_dashboard', error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            # Verificar propiedad antes de eliminar
            sql_check = """
                SELECT m.cafeteria_id, c.admin_id
                FROM menus m
                INNER JOIN cafeterias c ON m.cafeteria_id = c.id
                WHERE m.id = %s
            """
            cursor.execute(sql_check, (id,))
            menu = cursor.fetchone()
            
            if not menu or menu['admin_id'] != session['user_id']:
                return redirect(url_for('admin_dashboard', error="Acceso denegado."))
            
            # Eliminar el menú
            sql = "DELETE FROM menus WHERE id = %s"
            cursor.execute(sql, (id,))
        
        conn.commit()
        return redirect(url_for('gestion_menus', cafeteria_id=menu['cafeteria_id'], mensaje="Producto eliminado con éxito."))

    except Exception as e:
        print(f"Error al eliminar menú: {e}")
        return redirect(url_for('gestion_menus', cafeteria_id=menu.get('cafeteria_id', 0), error="Error al eliminar el producto."))
    finally:
        if conn: conn.close()


# ----------------------------------------------------
# --- GESTIÓN DE DESCUENTOS Y BONOS ---
# ----------------------------------------------------

@app.route('/admin/descuento/gestion/<int:cafeteria_id>', methods=['GET'])
@rol_required('admin')
def gestion_descuentos(cafeteria_id):
    # SOLUCIÓN: Definir la variable 'fecha_hoy' antes de usarla
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            

    conn = get_db_connection()
    descuentos = []
    cafeteria = None
    mensaje = request.args.get('mensaje')
    error = request.args.get('error')
            
    if conn:
        try:
            with conn.cursor() as cursor:
                # 1. VERIFICACIÓN DE SEGURIDAD
                sql_check = "SELECT admin_id, nombre FROM cafeterias WHERE id = %s"
                cursor.execute(sql_check, (cafeteria_id,))
                cafeteria = cursor.fetchone()
                
                if not cafeteria or cafeteria['admin_id'] != session['user_id']:
                    return redirect(url_for('admin_dashboard', error="Acceso denegado a los descuentos."))
                
                # 2. Traer todos los descuentos de esa cafetería - CORREGIR COLUMNAS
                sql_descuentos = "SELECT id, nombre, porcentaje as porcentaje_descuento, fecha_inicio, fecha_fin FROM descuentos_bonos WHERE cafeteria_id = %s"
                cursor.execute(sql_descuentos, (cafeteria_id,))
                descuentos = cursor.fetchall()
                
        except Exception as e:
            print(f"Error al obtener descuentos: {e}")
            error = "Error al cargar los descuentos."
        finally:
            conn.close()
       

        return render_template('admin_gestion_descuentos.html', 
                         cafeteria=cafeteria,
                         descuentos=descuentos, 
                         cafeteria_id=cafeteria_id,
                         mensaje=mensaje,
                         error=error,
                        fecha_hoy=fecha_hoy)  # <-- AGREGAR ESTO



@app.route('/admin/descuento/crear/<int:cafeteria_id>', methods=['POST'])
@rol_required('admin')
def crear_descuento(cafeteria_id):
    nombre = request.form.get('nombre')
    porcentaje_descuento = request.form.get('porcentaje_descuento')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('gestion_descuentos', cafeteria_id=cafeteria_id, error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            # Verificar que la cafetería pertenezca al admin
            sql_check = "SELECT admin_id FROM cafeterias WHERE id = %s"
            cursor.execute(sql_check, (cafeteria_id,))
            cafeteria = cursor.fetchone()
            
            if not cafeteria or cafeteria['admin_id'] != session['user_id']:
                return redirect(url_for('admin_dashboard', error="Acceso denegado."))
            
            # Insertar el nuevo descuento - USAR porcentaje y fecha_expiracion
            sql = """
                INSERT INTO descuentos_bonos (cafeteria_id, nombre, porcentaje, fecha_inicio, fecha_fin, fecha_expiracion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (cafeteria_id, nombre, porcentaje_descuento, fecha_inicio, fecha_fin, fecha_fin))
        
        conn.commit()
        return redirect(url_for('gestion_descuentos', cafeteria_id=cafeteria_id, mensaje="Descuento agregado con éxito."))

    except Exception as e:
        print(f"Error al crear descuento: {e}")
        return redirect(url_for('gestion_descuentos', cafeteria_id=cafeteria_id, error="Error al guardar el descuento."))
    finally:
        if conn: conn.close()


@app.route('/admin/descuento/editar/<int:id>', methods=['GET'])
@rol_required('admin')
def editar_descuento(id):
    conn = get_db_connection()
    descuento = None
    
    if conn:
        try:
            with conn.cursor() as cursor:
                # Traer el descuento y verificar propiedad a través de la cafetería
                sql = """
                    SELECT d.id, d.nombre, d.porcentaje as porcentaje_descuento, d.fecha_inicio, d.fecha_fin, d.cafeteria_id, c.admin_id
                    FROM descuentos_bonos d
                    INNER JOIN cafeterias c ON d.cafeteria_id = c.id
                    WHERE d.id = %s
                """
                cursor.execute(sql, (id,))
                descuento = cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar descuento para editar: {e}")
        finally:
            if conn: conn.close()

    if not descuento or descuento['admin_id'] != session['user_id']:
        return redirect(url_for('admin_dashboard', error="Descuento no encontrado o acceso denegado."))
    
    return render_template('admin_editar_descuento.html', descuento=descuento)


@app.route('/admin/descuento/actualizar/<int:id>', methods=['POST'])
@rol_required('admin')
def actualizar_descuento(id):
    nombre = request.form.get('nombre')
    porcentaje_descuento = request.form.get('porcentaje_descuento')
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('admin_dashboard', error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            # Verificar propiedad antes de actualizar
            sql_check = """
                SELECT d.cafeteria_id, c.admin_id
                FROM descuentos_bonos d
                INNER JOIN cafeterias c ON d.cafeteria_id = c.id
                WHERE d.id = %s
            """
            cursor.execute(sql_check, (id,))
            descuento = cursor.fetchone()
            
            if not descuento or descuento['admin_id'] != session['user_id']:
                return redirect(url_for('admin_dashboard', error="Acceso denegado."))
            
            # Actualizar el descuento
            sql = """
                UPDATE descuentos_bonos 
                SET nombre = %s, porcentaje = %s, fecha_inicio = %s, fecha_fin = %s, fecha_expiracion = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nombre, porcentaje_descuento, fecha_inicio, fecha_fin, fecha_fin, id))
        
        conn.commit()
        return redirect(url_for('gestion_descuentos', cafeteria_id=descuento['cafeteria_id'], mensaje="Descuento actualizado con éxito."))

    except Exception as e:
        print(f"Error al actualizar descuento: {e}")
        return redirect(url_for('admin_dashboard', error="Error al actualizar el descuento."))
    finally:
        if conn: conn.close()


@app.route('/admin/descuento/eliminar/<int:id>', methods=['POST'])
@rol_required('admin')
def eliminar_descuento(id):
    conn = get_db_connection()
    if conn is None:
        return redirect(url_for('admin_dashboard', error="Error de conexión a la BD."))

    try:
        with conn.cursor() as cursor:
            # Verificar propiedad antes de eliminar
            sql_check = """
                SELECT d.cafeteria_id, c.admin_id
                FROM descuentos_bonos d
                INNER JOIN cafeterias c ON d.cafeteria_id = c.id
                WHERE d.id = %s
            """
            cursor.execute(sql_check, (id,))
            descuento = cursor.fetchone()
            
            if not descuento or descuento['admin_id'] != session['user_id']:
                return redirect(url_for('admin_dashboard', error="Acceso denegado."))
            
            # Eliminar el descuento
            sql = "DELETE FROM descuentos_bonos WHERE id = %s"
            cursor.execute(sql, (id,))
        
        conn.commit()
        return redirect(url_for('gestion_descuentos', cafeteria_id=descuento['cafeteria_id'], mensaje="Descuento eliminado con éxito."))

    except Exception as e:
        print(f"Error al eliminar descuento: {e}")
        return redirect(url_for('gestion_descuentos', cafeteria_id=descuento.get('cafeteria_id', 0), error="Error al eliminar el descuento."))
    finally:
        if conn: conn.close()


# ----------------------------------------------------
# --- RUTA DE CLIENTE ---
# ----------------------------------------------------
@app.route('/cliente/dashboard')
@rol_required('cliente')
def cliente_dashboard():
    conn = get_db_connection()
    cafeterias = []
    stats = {
        'cafeterias_visitadas': 0,
        'total_visitas': 0,
        'total_resenas': 0,
        'descuentos_disponibles': 0,
        'puntos_fidelidad': 0,
        'dias_activo': 0,
        'cafeteria_favorita': None,
        'visitas_recientes': [],
        'resenas_recientes': []
    }
    
    mensaje = request.args.get('mensaje')
    error = request.args.get('error')
    
    if conn:
        try:
            with conn.cursor() as cursor:
                cliente_id = session['user_id']
                
                # 1. Traer todas las cafeterías para el mapa
                sql = "SELECT id, nombre, direccion, latitud, longitud FROM cafeterias"
                cursor.execute(sql)
                cafeterias_raw = cursor.fetchall()
                
                # Convertir Decimal a float
                for cafe in cafeterias_raw:
                    cafeterias.append({
                        'id': cafe['id'],
                        'nombre': cafe['nombre'],
                        'direccion': cafe['direccion'],
                        'latitud': float(cafe['latitud']) if cafe['latitud'] else 0,
                        'longitud': float(cafe['longitud']) if cafe['longitud'] else 0
                    })
                
                # 2. Estadísticas del cliente (verificar si existen las tablas)
                try:
                    # Total de visitas
                    cursor.execute("SELECT COUNT(*) as total FROM visitas WHERE cliente_id = %s", (cliente_id,))
                    result = cursor.fetchone()
                    stats['total_visitas'] = result['total'] if result else 0
                    
                    # Cafeterías únicas visitadas
                    cursor.execute("""
                        SELECT COUNT(DISTINCT cafeteria_id) as total 
                        FROM visitas 
                        WHERE cliente_id = %s
                    """, (cliente_id,))
                    result = cursor.fetchone()
                    stats['cafeterias_visitadas'] = result['total'] if result else 0
                    
                    # Puntos de fidelidad (1 punto por cada 5 visitas)
                    stats['puntos_fidelidad'] = stats['total_visitas'] // 5
                    
                    # Cafetería favorita (más visitada)
                    cursor.execute("""
                        SELECT c.nombre, COUNT(*) as visitas
                        FROM visitas v
                        JOIN cafeterias c ON v.cafeteria_id = c.id
                        WHERE v.cliente_id = %s
                        GROUP BY v.cafeteria_id, c.nombre
                        ORDER BY visitas DESC
                        LIMIT 1
                    """, (cliente_id,))
                    favorita = cursor.fetchone()
                    if favorita:
                        stats['cafeteria_favorita'] = {
                            'nombre': favorita['nombre'],
                            'visitas': favorita['visitas']
                        }
                    
                    # Visitas recientes (últimas 5)
                    cursor.execute("""
                        SELECT c.nombre, v.fecha_visita
                        FROM visitas v
                        JOIN cafeterias c ON v.cafeteria_id = c.id
                        WHERE v.cliente_id = %s
                        ORDER BY v.fecha_visita DESC
                        LIMIT 5
                    """, (cliente_id,))
                    stats['visitas_recientes'] = cursor.fetchall()
                    
                    # Días activo (desde primera visita)
                    cursor.execute("""
                        SELECT DATEDIFF(CURDATE(), MIN(fecha_visita)) as dias
                        FROM visitas
                        WHERE cliente_id = %s
                    """, (cliente_id,))
                    result = cursor.fetchone()
                    stats['dias_activo'] = result['dias'] if result and result['dias'] else 0
                    
                except Exception as e:
                    print(f"Tabla 'visitas' no existe o error: {e}")        
                
                # 3. Reseñas del cliente
                try:
                    cursor.execute("""
                        SELECT COUNT(*) as total 
                        FROM valoraciones 
                        WHERE cliente_id = %s
                    """, (cliente_id,))
                    result = cursor.fetchone()
                    stats['total_resenas'] = result['total'] if result else 0             
                    
                    # Reseñas recientes
                    cursor.execute("""
                        SELECT c.nombre, v.puntuacion, v.comentario, v.fecha
                        FROM valoraciones v
                        JOIN cafeterias c ON v.cafeteria_id = c.id
                        WHERE v.cliente_id = %s
                        ORDER BY v.fecha DESC
                        LIMIT 3
                    """, (cliente_id,))
                    stats['resenas_recientes'] = cursor.fetchall()         
                except Exception as e:
                    print(f"Tabla 'valoraciones' no existe o error: {e}")
                
                # 4. Descuentos disponibles
                try:
                    cursor.execute("""
                        SELECT COUNT(*) as total
                        FROM descuentos_bonos
                        WHERE fecha_inicio <= CURDATE() 
                        AND fecha_fin >= CURDATE()
                    """)
                    result = cursor.fetchone()
                    stats['descuentos_disponibles'] = result['total'] if result else 0
                except Exception as e:
                    print(f"Error al contar descuentos: {e}")
                    
        except Exception as e:
            print(f"Error al obtener datos para cliente: {e}")
        finally:
            conn.close()
    
    # Convertir a JSON para JavaScript
    import json
    cafeterias_json = json.dumps(cafeterias)
    
    return render_template('cliente_dashboard.html', 
                         cafeterias_json=cafeterias_json,
                         stats=stats,
                         mensaje=mensaje,
                         error=error,
                         session=session)

# ============================================
# --- SISTEMA DE ESCANEO QR PARA CLIENTES ---
# ============================================

@app.route('/api/escanear-qr', methods=['POST'])
def escanear_qr():
    """API para escanear QR desde el dashboard del cliente"""
    # Verificar que el usuario esté logueado
    if 'user_id' not in session or session.get('rol') != 'cliente':
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión como cliente'
        }), 401
    
    try:
        data = request.get_json()
        codigo_qr = data.get('codigo_qr', '').strip()
        
        if not codigo_qr:
            return jsonify({
                'success': False,
                'message': 'Código QR vacío'
            }), 400
        
        cliente_id = session['user_id']
        conn = get_db_connection()
        
        if conn == False:
            return jsonify({
                'success': False,
                'message': 'Error de conexión a la base de datos'
            }), 500
        
        try:
            with conn.cursor() as cursor:
                # Verificar que la cafetería existe
                cursor.execute("SELECT id, nombre FROM cafeterias WHERE id = %s", (codigo_qr,))
                cafeteria = cursor.fetchone()
                
                if not cafeteria:
                    return jsonify({
                        'success': False,
                        'message': 'Código QR inválido. Cafetería no encontrada.'
                    }), 404
                
                # Verificar si ya visitó hoy
                cursor.execute("""
                    SELECT id FROM visitas 
                    WHERE cliente_id = %s 
                    AND cafeteria_id = %s 
                    AND DATE(fecha_visita) = CURDATE()
                """, (cliente_id, codigo_qr))
                
                if cursor.fetchone():
                    return jsonify({
                        'success': False,
                        'message': f'Ya registraste una visita a {cafeteria["nombre"]} hoy.'
                    }), 400
                
                # Registrar la visita
                cursor.execute("""
                    INSERT INTO visitas (cliente_id, cafeteria_id, fecha_visita)
                    VALUES (%s, %s, NOW())
                """, (cliente_id, codigo_qr))
                
                conn.commit()
                
                # Contar visitas totales
                cursor.execute("""
                    SELECT COUNT(DISTINCT cafeteria_id) as visitadas
                    FROM visitas WHERE cliente_id = %s
                """, (cliente_id,))
                visitadas = cursor.fetchone()['visitadas']
                
                return jsonify({
                    'success': True,
                    'message': f'¡Visita registrada en {cafeteria["nombre"]}! +1 punto',
                    'visitadas': visitadas
                })
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error en escanear_qr: {e}")
        return jsonify({
            'success': False,
            'message': 'Error al procesar el código QR'
        }), 500

# ============================================
# --- SISTEMA DE QR PARA ADMIN ---
# ============================================

@app.route('/admin/cafeteria/<int:cafeteria_id>/qr')
@rol_required('admin')
def ver_qr_cafeteria(cafeteria_id):
    """Muestra el QR de una cafetería para que los clientes escaneen"""
    conn = get_db_connection()
    
    if not conn:
        return redirect(url_for('admin_dashboard', error='Error de conexión'))
    
    try:
        with conn.cursor() as cursor:
            # Verificar que la cafetería pertenece al admin
            cursor.execute("""
                SELECT id, nombre, direccion 
                FROM cafeterias 
                WHERE id = %s AND admin_id = %s
            """, (cafeteria_id, session['user_id']))
            
            cafeteria = cursor.fetchone()
            
            if not cafeteria:
                return redirect(url_for('admin_dashboard', error='Cafetería no encontrada'))
            
            # Generar código QR
            import qrcode
            from io import BytesIO
            import base64
            
            # El QR contiene el ID de la cafetería
            qr_data = str(cafeteria['id'])
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64 para mostrar en HTML
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return render_template('admin_ver_qr.html', 
                                 cafeteria=cafeteria,
                                 qr_image=img_str)
            
    except Exception as e:
        print(f"Error generando QR: {e}")
        return redirect(url_for('admin_dashboard', error=f'Error al generar QR: {str(e)}'))
    finally:
        conn.close()


@app.route('/admin/cafeteria/<int:cafeteria_id>/qr/download')
@rol_required('admin')
def descargar_qr_cafeteria(cafeteria_id):
    """Descarga el QR como imagen PNG"""
    conn = get_db_connection()
    
    if not conn:
        return "Error de conexión", 500
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre 
                FROM cafeterias 
                WHERE id = %s AND admin_id = %s
            """, (cafeteria_id, session['user_id']))
            
            cafeteria = cursor.fetchone()
            
            if not cafeteria:
                return "Cafetería no encontrada", 404
            
            # Generar QR
            import qrcode
            from io import BytesIO
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(str(cafeteria['id']))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar en memoria
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            buffered.seek(0)
            
            return send_file(
                buffered,
                mimetype='image/png',
                as_attachment=True,
                download_name=f'QR_{cafeteria["nombre"].replace(" ", "_")}.png'
            )
            
    except Exception as e:
        print(f"Error generando QR para descarga: {e}")
        return "Error al generar QR", 500
    finally:
        conn.close()


# ============================================
# --- SISTEMA DE CERTIFICADOS ---
# ============================================

@app.route('/cliente/certificado/progreso')
@rol_required('cliente')
def verificar_progreso_certificado():
    """Muestra el progreso para obtener el certificado"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    if not conn:
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('cliente_dashboard'))
    
    puede_generar, visitadas, total = verificar_certificado_disponible(user_id, conn)
    
    # Obtener lista de cafeterías y cuáles ha visitado
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, 
        CASE WHEN v.id IS NOT NULL THEN 1 ELSE 0 END as visitada
        FROM cafeterias c
        LEFT JOIN visitas v ON c.id = v.cafeteria_id AND v.cliente_id = %s
        ORDER BY c.nombre
    """, (user_id,))
    cafeterias = cursor.fetchall()
    
    conn.close()
    
    return render_template('progreso_certificado.html',
                         cafeterias=cafeterias,
                         visitadas=visitadas,
                         total=total,
                         puede_generar=puede_generar)


@app.route('/cliente/certificado/generar')
@rol_required('cliente')
def generar_certificado_cliente():
    """Genera el certificado PDF para el cliente"""
    user_id = session['user_id']
    nombre_completo = session['nombre']
    
    conn = get_db_connection()
    
    if not conn:
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('cliente_dashboard'))
    
    # Verificar si puede generar certificado
    puede_generar, visitadas, total = verificar_certificado_disponible(user_id, conn)
    
    if not puede_generar:
        flash(f'Debes visitar todas las cafeterías. Has visitado {visitadas}/{total}', 'warning')
        conn.close()
        return redirect(url_for('verificar_progreso_certificado'))
    
    # Verificar si ya tiene certificado
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM certificados WHERE cliente_id = %s", (user_id,))
    certificado_existente = cursor.fetchone()
    
    if certificado_existente:
        codigo_cert = certificado_existente['codigo_certificado']
    else:
        # Generar código único
        codigo_cert = str(uuid.uuid4())[:16].upper()
        registrar_certificado(user_id, codigo_cert, conn)
    
    conn.close()
    
    # Crear carpeta para certificados si no existe
    os.makedirs('static/certificados', exist_ok=True)
    
    # Ruta del archivo PDF
    filename = f'certificado_{user_id}_{codigo_cert}.pdf'
    output_path = os.path.join('static', 'certificados', filename)
    
    # Generar el certificado
    fecha_emision = datetime.now()
    generar_certificado(nombre_completo, fecha_emision, codigo_cert, output_path)
    
    # Enviar el archivo para descarga
    return send_file(
        output_path,
        as_attachment=True,
        download_name=f'Certificado_Cafetero_{nombre_completo.replace(" ", "_")}.pdf',
        mimetype='application/pdf'
    )


# --- INICIO DE LA APLICACIÓN (DEBE ESTAR AL FINAL) ---
if __name__ == '__main__':
    # Ejecutar en modo debug para desarrollo (se reinicia automáticamente con cambios)
    app.run(debug=True)