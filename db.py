import sqlite3
from datetime import datetime

DB_PATH = "inventario.db"

def inicializar_db():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    # Crear la tabla con el nuevo campo fecha_modificacion si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            cantidad INTEGER NOT NULL,
            imagen TEXT,
            fecha_modificacion TEXT
        )
    ''')
    conexion.commit()

    # Verificar si el campo fecha_modificacion existe, si no, agregarlo
    cursor.execute("PRAGMA table_info(productos)")
    columnas = [columna[1] for columna in cursor.fetchall()]
    if "fecha_modificacion" not in columnas:
        cursor.execute("ALTER TABLE productos ADD COLUMN fecha_modificacion TEXT")
        conexion.commit()

    conexion.close()

def obtener_productos():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, cantidad, imagen, fecha_modificacion FROM productos")
    productos = cursor.fetchall()
    conexion.close()
    return productos

def agregar_producto_db(nombre, cantidad, imagen):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO productos (nombre, cantidad, imagen, fecha_modificacion) VALUES (?, ?, ?, ?)",
                   (nombre, cantidad, imagen, fecha_actual))
    conexion.commit()
    conexion.close()

def actualizar_cantidad(nombre, nueva_cantidad):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE productos SET cantidad = ?, fecha_modificacion = ? WHERE nombre = ?",
                   (nueva_cantidad, fecha_actual, nombre))
    conexion.commit()
    conexion.close()

def eliminar_producto_db(nombre):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE nombre = ?", (nombre,))
    conexion.commit()
    conexion.close()

def actualizar_imagen(nombre, nueva_ruta):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE productos SET imagen = ?, fecha_modificacion = ? WHERE nombre = ?",
                   (nueva_ruta, fecha_actual, nombre))
    conexion.commit()
    conexion.close()
