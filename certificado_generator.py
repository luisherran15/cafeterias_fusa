from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

def generar_certificado(nombre_completo, fecha_emision, codigo_certificado, output_path):
    """
    Genera un certificado PDF personalizado
    
    Args:
        nombre_completo: Nombre del cliente
        fecha_emision: Fecha de emisión del certificado
        codigo_certificado: Código único del certificado
        output_path: Ruta donde se guardará el PDF
    """
    
    # Crear el canvas en orientación horizontal
    c = canvas.Canvas(output_path, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Colores
    color_beige = HexColor('#F5E6D3')
    color_verde_oscuro = HexColor('#556B2F')
    color_marron = HexColor('#3E2723')
    
    # Fondo beige
    c.setFillColor(color_beige)
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Dibujar borde decorativo doble
    c.setStrokeColor(color_verde_oscuro)
    c.setLineWidth(3)
    # Borde exterior
    c.roundRect(0.4*inch, 0.4*inch, width-0.8*inch, height-0.8*inch, 15, stroke=1, fill=0)
    # Borde interior
    c.setLineWidth(1.5)
    c.roundRect(0.5*inch, 0.5*inch, width-1*inch, height-1*inch, 12, stroke=1, fill=0)
    
    # Esquinas decorativas
    c.setLineWidth(2)
    esquina_size = 0.3*inch
    # Esquina superior izquierda
    c.line(0.4*inch, height-0.4*inch-esquina_size, 0.4*inch, height-0.4*inch)
    c.line(0.4*inch, height-0.4*inch, 0.4*inch+esquina_size, height-0.4*inch)
    # Esquina superior derecha
    c.line(width-0.4*inch-esquina_size, height-0.4*inch, width-0.4*inch, height-0.4*inch)
    c.line(width-0.4*inch, height-0.4*inch, width-0.4*inch, height-0.4*inch-esquina_size)
    # Esquina inferior izquierda
    c.line(0.4*inch, 0.4*inch, 0.4*inch, 0.4*inch+esquina_size)
    c.line(0.4*inch, 0.4*inch, 0.4*inch+esquina_size, 0.4*inch)
    # Esquina inferior derecha
    c.line(width-0.4*inch, 0.4*inch, width-0.4*inch, 0.4*inch+esquina_size)
    c.line(width-0.4*inch-esquina_size, 0.4*inch, width-0.4*inch, 0.4*inch)
    
    # TÍTULO "CERTIFICADO"
    c.setFillColor(color_marron)
    c.setFont("Helvetica-Bold", 60)
    titulo = "CERTIFICADO"
    titulo_width = c.stringWidth(titulo, "Helvetica-Bold", 60)
    c.drawString((width - titulo_width) / 2, height - 1.8*inch, titulo)
    
    # Subtítulo
    c.setFont("Helvetica", 18)
    subtitulo = "Se otorga el presente certificado a"
    subtitulo_width = c.stringWidth(subtitulo, "Helvetica", 18)
    c.drawString((width - subtitulo_width) / 2, height - 2.4*inch, subtitulo)
    
    # NOMBRE DEL CLIENTE (más grande y destacado)
    c.setFont("Helvetica-Bold", 42)
    nombre_width = c.stringWidth(nombre_completo, "Helvetica-Bold", 42)
    c.drawString((width - nombre_width) / 2, height - 3.2*inch, nombre_completo)
    
    # Texto descriptivo
    c.setFont("Helvetica", 16)
    texto1 = "por haber realizado el"
    texto1_width = c.stringWidth(texto1, "Helvetica", 16)
    c.drawString((width - texto1_width) / 2, height - 3.8*inch, texto1)
    
    # RECORRIDO CAFETERO (destacado)
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(color_verde_oscuro)
    recorrido_texto = "RECORRIDO CAFETERO DE"
    recorrido_width = c.stringWidth(recorrido_texto, "Helvetica-Bold", 32)
    c.drawString((width - recorrido_width) / 2, height - 4.4*inch, recorrido_texto)
    
    fusagasuga_texto = "FUSAGASUGÁ"
    fusagasuga_width = c.stringWidth(fusagasuga_texto, "Helvetica-Bold", 32)
    c.drawString((width - fusagasuga_width) / 2, height - 4.9*inch, fusagasuga_texto)
    
    # ========================================
    # INSERTAR IMÁGENES (LOGOS)
    # ========================================
    
    # Rutas de las imágenes
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_colombia_path = os.path.join(base_dir, 'static', 'images', 'colombia_cert.png')
    logo_fusita_path = os.path.join(base_dir, 'static', 'images', 'fusita.png')
    
    # Logo izquierdo - Denominación de Origen (Colombia)
    logo_left_x = 1.5*inch
    logo_y = height - 5.8*inch
    logo_size = 4*inch  # Tamaño del logo
    
    if os.path.exists(logo_colombia_path):
        try:
            # Insertar imagen centrada
            c.drawImage(
                logo_colombia_path, 
                logo_left_x - logo_size/2,  # Centrar horizontalmente
                logo_y - logo_size/2,        # Centrar verticalmente
                width=logo_size, 
                height=logo_size,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception as e:
            print(f"Error al cargar logo Colombia: {e}")
            # Fallback: dibujar círculo si falla la imagen
            c.setFillColor(color_verde_oscuro)
            c.circle(logo_left_x, logo_y, 0.8*inch, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(color_marron)
            c.drawCentredString(logo_left_x, logo_y, "COLOMBIA")
    else:
        print(f"Advertencia: No se encontró {logo_colombia_path}")
        # Fallback: dibujar círculo
        c.setFillColor(color_verde_oscuro)
        c.circle(logo_left_x, logo_y, 0.8*inch, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(color_marron)
        c.drawCentredString(logo_left_x, logo_y, "COLOMBIA")
    
    # Logo derecho - Escudo de Fusagasugá
    logo_right_x = width - 1.5*inch
    
    if os.path.exists(logo_fusita_path):
        try:
            # Insertar imagen centrada
            c.drawImage(
                logo_fusita_path, 
                logo_right_x - logo_size/2,  # Centrar horizontalmente
                logo_y - logo_size/2,        # Centrar verticalmente
                width=logo_size, 
                height=logo_size,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception as e:
            print(f"Error al cargar logo Fusagasugá: {e}")
            # Fallback: dibujar círculo si falla la imagen
            c.setFillColor(color_verde_oscuro)
            c.circle(logo_right_x, logo_y, 0.8*inch, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(color_marron)
            c.drawCentredString(logo_right_x, logo_y, "FUSAGASUGÁ")
    else:
        print(f"Advertencia: No se encontró {logo_fusita_path}")
        # Fallback: dibujar círculo
        c.setFillColor(color_verde_oscuro)
        c.circle(logo_right_x, logo_y, 0.8*inch, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(color_marron)
        c.drawCentredString(logo_right_x, logo_y, "FUSAGASUGÁ")
    
    # ========================================
    # INFORMACIÓN DE PIE DE PÁGINA
    # ========================================
    
    c.setFont("Helvetica", 11)
    c.setFillColor(color_marron)
    
    # Traducir el mes al español
    meses = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo',
        'April': 'abril', 'May': 'mayo', 'June': 'junio',
        'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
        'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    mes_ingles = fecha_emision.strftime('%B')
    mes_espanol = meses.get(mes_ingles, mes_ingles)
    
    fecha_texto = f"Fecha de expedición: {fecha_emision.day} de {mes_espanol} de {fecha_emision.year}"
    fecha_width = c.stringWidth(fecha_texto, "Helvetica", 11)
    c.drawString((width - fecha_width) / 2, 1.2*inch, fecha_texto)
    
    c.setFont("Helvetica", 9)
    codigo_texto = f"Código de verificación: {codigo_certificado}"
    codigo_width = c.stringWidth(codigo_texto, "Helvetica", 9)
    c.drawString((width - codigo_width) / 2, 0.9*inch, codigo_texto)
    
    # Línea decorativa inferior
    c.setStrokeColor(color_verde_oscuro)
    c.setLineWidth(0.5)
    c.line(2*inch, 0.7*inch, width-2*inch, 0.7*inch)
    
    # Finalizar y guardar
    c.save()
    
    print(f"✅ Certificado generado exitosamente: {output_path}")
    return output_path


def verificar_certificado_disponible(user_id, conn):
    """
    Verifica si el usuario ha visitado todas las cafeterías
    
    Args:
        user_id: ID del usuario (cliente_id)
        conn: Conexión a la base de datos
        
    Returns:
        tuple: (puede_generar: bool, cafeterias_visitadas: int, total_cafeterias: int)
    """
    cursor = conn.cursor()
    
    # Total de cafeterías
    cursor.execute("SELECT COUNT(*) as total FROM cafeterias")
    total_cafeterias = cursor.fetchone()['total']
    
    # Cafeterías visitadas por el usuario
    cursor.execute("""
        SELECT COUNT(DISTINCT cafeteria_id) as visitadas
        FROM visitas WHERE cliente_id = %s
    """, (user_id,))
    visitadas = cursor.fetchone()['visitadas']
    
    puede_generar = visitadas == total_cafeterias and total_cafeterias > 0
    
    return puede_generar, visitadas, total_cafeterias


def registrar_certificado(user_id, codigo_certificado, conn):
    """
    Registra el certificado generado en la base de datos
    
    Args:
        user_id: ID del usuario (cliente_id)
        codigo_certificado: Código único del certificado
        conn: Conexión a la base de datos
    """
    cursor = conn.cursor()
    
    # Verificar si ya existe un certificado
    cursor.execute("SELECT id FROM certificados WHERE cliente_id = %s", (user_id,))
    existe = cursor.fetchone()
    
    if not existe:
        cursor.execute("""
            INSERT INTO certificados (cliente_id, codigo_certificado)
            VALUES (%s, %s)
        """, (user_id, codigo_certificado))
        conn.commit()
    
    return True