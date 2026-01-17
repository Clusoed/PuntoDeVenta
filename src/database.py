"""
Base de datos SQLite para el Sistema de Ventas e Inventario
"""
import sqlite3
import os
import sys
from datetime import datetime
from typing import Optional, List, Tuple, Any

def get_db_path() -> str:
    """Obtiene la ruta de la base de datos según el entorno de ejecución."""
    # Detectar si estamos ejecutando como .exe empaquetado
    if getattr(sys, 'frozen', False):
        # Ejecutando como .exe - usar AppData/Local para persistencia
        app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        db_dir = os.path.join(app_data, 'PuntoDeVenta', 'data')
    else:
        # Ejecutando desde código fuente - usar carpeta del proyecto
        db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    return os.path.join(db_dir, 'ventas.db')

# Ruta de la base de datos
DB_PATH = get_db_path()



def get_connection() -> sqlite3.Connection:
    """Obtiene una conexión a la base de datos."""
    # Asegurar que existe el directorio data
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    conn.execute("PRAGMA foreign_keys = ON")  # Habilitar claves foráneas
    return conn


def init_database():
    """Inicializa la base de datos con todas las tablas necesarias."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de Configuración
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tienda TEXT NOT NULL DEFAULT 'Mi Tienda',
            rif TEXT,
            direccion TEXT,
            telefono TEXT,
            tasa_cambio REAL NOT NULL DEFAULT 1.0,
            fecha_tasa DATETIME DEFAULT CURRENT_TIMESTAMP,
            iva_porcentaje REAL DEFAULT 16.0,
            password_admin TEXT
        )
    ''')
    
    # Tabla de Categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            activo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabla de Productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            categoria_id INTEGER,
            marca TEXT,
            unidad_medida TEXT DEFAULT 'Unidad',
            precio_usd REAL NOT NULL DEFAULT 0,
            costo_usd REAL DEFAULT 0,
            porcentaje_ganancia REAL DEFAULT 30,
            stock_actual INTEGER DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5,
            activo INTEGER DEFAULT 1,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    ''')
    
    # Tabla de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula_rif TEXT UNIQUE,
            nombre TEXT NOT NULL,
            telefono TEXT,
            direccion TEXT,
            email TEXT,
            activo INTEGER DEFAULT 1,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migración: agregar columna activo a clientes si no existe
    try:
        cursor.execute('ALTER TABLE clientes ADD COLUMN activo INTEGER DEFAULT 1')
    except sqlite3.OperationalError:
        pass  # Columna ya existe
    
    # Tabla de Ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_factura TEXT NOT NULL UNIQUE,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            cliente_id INTEGER,
            subtotal_usd REAL NOT NULL,
            iva_usd REAL DEFAULT 0,
            total_usd REAL NOT NULL,
            tasa_cambio REAL NOT NULL,
            total_bs REAL NOT NULL,
            forma_pago TEXT NOT NULL,
            referencia_pago TEXT,
            monto_recibido REAL,
            vuelto REAL DEFAULT 0,
            estado TEXT DEFAULT 'Completada',
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    # Tabla de Detalle de Ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            nombre_producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unit_usd REAL NOT NULL,
            descuento REAL DEFAULT 0,
            total_linea_usd REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')
    
    # Tabla de Movimientos de Inventario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            producto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            stock_anterior INTEGER NOT NULL,
            stock_nuevo INTEGER NOT NULL,
            referencia TEXT,
            observacion TEXT,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')
    
    # Tabla de Historial de Tasas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_tasas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tasa REAL NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de Compras (entradas de inventario)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_compra TEXT UNIQUE NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            proveedor TEXT,
            total_usd REAL DEFAULT 0,
            observacion TEXT,
            estado TEXT DEFAULT 'Completada'
        )
    ''')
    
    # Tabla de Detalle de Compras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compra_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            nombre_producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            costo_unit_usd REAL NOT NULL,
            total_linea_usd REAL NOT NULL,
            FOREIGN KEY (compra_id) REFERENCES compras(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')
    
    # Crear índices para optimización
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_numero ON ventas(numero_factura)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras(fecha)')
    
    # Insertar configuración inicial si no existe
    cursor.execute('SELECT COUNT(*) FROM configuracion')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO configuracion (nombre_tienda, tasa_cambio, iva_porcentaje)
            VALUES (?, ?, ?)
        ''', ('Mi Tienda', 45.50, 16.0))
    
    # Migración: agregar columna password_admin si no existe
    cursor.execute("PRAGMA table_info(configuracion)")
    columnas = [col[1] for col in cursor.fetchall()]
    if 'password_admin' not in columnas:
        cursor.execute('ALTER TABLE configuracion ADD COLUMN password_admin TEXT')
    
    # Migración: agregar columna porcentaje_ganancia a productos si no existe
    cursor.execute("PRAGMA table_info(productos)")
    columnas_prod = [col[1] for col in cursor.fetchall()]
    if 'porcentaje_ganancia' not in columnas_prod:
        cursor.execute('ALTER TABLE productos ADD COLUMN porcentaje_ganancia REAL DEFAULT 30')
    
    # Insertar categorías iniciales si no existen
    cursor.execute('SELECT COUNT(*) FROM categorias')
    if cursor.fetchone()[0] == 0:
        categorias_iniciales = [
            ('Alimentos', 'Productos alimenticios'),
            ('Bebidas', 'Bebidas y refrescos'),
            ('Limpieza', 'Productos de limpieza'),
            ('Higiene Personal', 'Productos de higiene'),
            ('Otros', 'Otros productos')
        ]
        cursor.executemany(
            'INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)',
            categorias_iniciales
        )
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente")


# ============== FUNCIONES DE CONFIGURACIÓN ==============

def get_configuracion() -> dict:
    """Obtiene la configuración actual del sistema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM configuracion WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return {}


def update_tasa_cambio(nueva_tasa: float) -> bool:
    """Actualiza la tasa de cambio y guarda en historial."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Actualizar tasa actual
        cursor.execute('''
            UPDATE configuracion 
            SET tasa_cambio = ?, fecha_tasa = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (nueva_tasa,))
        
        # Guardar en historial
        cursor.execute('''
            INSERT INTO historial_tasas (tasa) VALUES (?)
        ''', (nueva_tasa,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error actualizando tasa: {e}")
        return False


def get_tasa_actual() -> float:
    """Obtiene la tasa de cambio actual."""
    config = get_configuracion()
    return config.get('tasa_cambio', 1.0)


def get_historial_tasas(limite: int = 10) -> List[dict]:
    """Obtiene el historial de tasas de cambio."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tasa, fecha FROM historial_tasas 
        ORDER BY fecha DESC LIMIT ?
    ''', (limite,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ============== FUNCIONES DE PRODUCTOS ==============

def crear_producto(codigo: str, nombre: str, precio_usd: float, 
                   categoria_id: int = None, marca: str = None,
                   unidad_medida: str = 'Unidad', costo_usd: float = 0,
                   porcentaje_ganancia: float = 30,
                   stock_actual: int = 0, stock_minimo: int = 5) -> int:
    """Crea un nuevo producto y retorna su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO productos (codigo, nombre, precio_usd, categoria_id, marca,
                              unidad_medida, costo_usd, porcentaje_ganancia, stock_actual, stock_minimo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (codigo, nombre, precio_usd, categoria_id, marca, 
          unidad_medida, costo_usd, porcentaje_ganancia, stock_actual, stock_minimo))
    producto_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return producto_id


def get_productos(activos_only: bool = True) -> List[dict]:
    """Obtiene la lista de productos."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
    '''
    if activos_only:
        query += ' WHERE p.activo = 1'
    query += ' ORDER BY p.nombre'
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def buscar_productos(termino: str) -> List[dict]:
    """Busca productos por código o nombre."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1 AND (p.codigo LIKE ? OR p.nombre LIKE ?)
        ORDER BY p.nombre
    ''', (f'%{termino}%', f'%{termino}%'))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_producto_por_codigo(codigo: str) -> Optional[dict]:
    """Obtiene un producto por su código."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.codigo = ?
    ''', (codigo,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def actualizar_stock(producto_id: int, cantidad: int, tipo: str, 
                     referencia: str = None, observacion: str = None) -> bool:
    """Actualiza el stock de un producto y registra el movimiento."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener stock actual
        cursor.execute('SELECT stock_actual FROM productos WHERE id = ?', (producto_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        stock_anterior = row['stock_actual']
        
        # Calcular nuevo stock según tipo
        if tipo in ['Entrada', 'Ajuste+']:
            stock_nuevo = stock_anterior + cantidad
        elif tipo in ['Salida', 'Ajuste-']:
            stock_nuevo = stock_anterior - cantidad
        else:
            return False
        
        # Actualizar stock del producto
        cursor.execute('''
            UPDATE productos SET stock_actual = ? WHERE id = ?
        ''', (stock_nuevo, producto_id))
        
        # Registrar movimiento
        cursor.execute('''
            INSERT INTO movimientos_inventario 
            (producto_id, tipo, cantidad, stock_anterior, stock_nuevo, referencia, observacion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (producto_id, tipo, cantidad, stock_anterior, stock_nuevo, referencia, observacion))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error actualizando stock: {e}")
        return False


def generar_codigo_producto() -> str:
    """Genera un código único para un nuevo producto."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT codigo FROM productos ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    
    if row:
        try:
            ultimo_numero = int(row['codigo'][3:])
            nuevo_numero = ultimo_numero + 1
        except:
            nuevo_numero = 1
    else:
        nuevo_numero = 1
    
    return f'PRD{nuevo_numero:05d}'


# ============== FUNCIONES DE CATEGORÍAS ==============

def get_categorias() -> List[dict]:
    """Obtiene la lista de categorías activas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categorias WHERE activo = 1 ORDER BY nombre')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def crear_categoria(nombre: str, descripcion: str = None) -> int:
    """Crea una nueva categoría y retorna su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)
    ''', (nombre, descripcion))
    categoria_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return categoria_id


def actualizar_categoria(categoria_id: int, nombre: str, descripcion: str = None) -> bool:
    """Actualiza una categoría existente."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE categorias SET nombre = ?, descripcion = ? WHERE id = ?
        ''', (nombre, descripcion, categoria_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error actualizando categoría: {e}")
        return False


def eliminar_categoria(categoria_id: int) -> bool:
    """Desactiva una categoría (eliminación lógica)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE categorias SET activo = 0 WHERE id = ?', (categoria_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error eliminando categoría: {e}")
        return False


# ============== FUNCIONES ADICIONALES DE PRODUCTOS ==============

def get_producto_por_id(producto_id: int) -> Optional[dict]:
    """Obtiene un producto por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id = ?
    ''', (producto_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def actualizar_producto(producto_id: int, codigo: str = None, nombre: str = None, 
                        precio_usd: float = None, categoria_id: int = None,
                        marca: str = None, unidad_medida: str = None,
                        costo_usd: float = None, porcentaje_ganancia: float = None,
                        stock_minimo: int = None) -> bool:
    """Actualiza un producto existente."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener valores actuales
        cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        producto_actual = dict(row)
        
        # Usar valores nuevos o mantener los actuales
        nuevo_codigo = codigo if codigo is not None else producto_actual['codigo']
        nuevo_nombre = nombre if nombre is not None else producto_actual['nombre']
        nuevo_precio = precio_usd if precio_usd is not None else producto_actual['precio_usd']
        nueva_categoria = categoria_id if categoria_id is not None else producto_actual['categoria_id']
        nueva_marca = marca if marca is not None else producto_actual['marca']
        nueva_unidad = unidad_medida if unidad_medida is not None else producto_actual['unidad_medida']
        nuevo_costo = costo_usd if costo_usd is not None else producto_actual['costo_usd']
        nuevo_porcentaje = porcentaje_ganancia if porcentaje_ganancia is not None else producto_actual.get('porcentaje_ganancia', 30)
        nuevo_stock_min = stock_minimo if stock_minimo is not None else producto_actual['stock_minimo']
        
        cursor.execute('''
            UPDATE productos SET
                codigo = ?, nombre = ?, precio_usd = ?, categoria_id = ?,
                marca = ?, unidad_medida = ?, costo_usd = ?, porcentaje_ganancia = ?, stock_minimo = ?
            WHERE id = ?
        ''', (nuevo_codigo, nuevo_nombre, nuevo_precio, nueva_categoria,
              nueva_marca, nueva_unidad, nuevo_costo, nuevo_porcentaje, nuevo_stock_min, producto_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error actualizando producto: {e}")
        return False


def eliminar_producto(producto_id: int) -> bool:
    """Desactiva un producto (eliminación lógica)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE productos SET activo = 0 WHERE id = ?', (producto_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error eliminando producto: {e}")
        return False


def get_productos_por_categoria(categoria_id: int) -> List[dict]:
    """Obtiene productos de una categoría específica."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1 AND p.categoria_id = ?
        ORDER BY p.nombre
    ''', (categoria_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def actualizar_configuracion(nombre_tienda: str = None, rif: str = None,
                             direccion: str = None, telefono: str = None,
                             iva_porcentaje: float = None) -> bool:
    """Actualiza la configuración de la tienda."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener valores actuales
        cursor.execute('SELECT * FROM configuracion WHERE id = 1')
        row = cursor.fetchone()
        if not row:
            return False
        
        config_actual = dict(row)
        
        nuevo_nombre = nombre_tienda if nombre_tienda is not None else config_actual['nombre_tienda']
        nuevo_rif = rif if rif is not None else config_actual['rif']
        nueva_dir = direccion if direccion is not None else config_actual['direccion']
        nuevo_tel = telefono if telefono is not None else config_actual['telefono']
        nuevo_iva = iva_porcentaje if iva_porcentaje is not None else config_actual['iva_porcentaje']
        
        cursor.execute('''
            UPDATE configuracion SET
                nombre_tienda = ?, rif = ?, direccion = ?, telefono = ?, iva_porcentaje = ?
            WHERE id = 1
        ''', (nuevo_nombre, nuevo_rif, nueva_dir, nuevo_tel, nuevo_iva))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error actualizando configuración: {e}")
        return False


# ============== FUNCIONES DE CLIENTES ==============

def get_clientes(activos_only: bool = True) -> List[dict]:
    """Obtiene la lista de clientes."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if activos_only:
        cursor.execute('SELECT * FROM clientes WHERE activo = 1 ORDER BY nombre')
    else:
        cursor.execute('SELECT * FROM clientes ORDER BY nombre')
    
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clientes


def get_cliente_por_id(cliente_id: int) -> Optional[dict]:
    """Obtiene un cliente por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============== FUNCIONES DE VENTAS ==============

def generar_numero_factura() -> str:
    """Genera un número de factura único."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) + 1 as num FROM ventas')
    row = cursor.fetchone()
    conn.close()
    
    numero = row['num'] if row else 1
    fecha = datetime.now().strftime('%Y%m%d')
    return f'FAC-{fecha}-{numero:05d}'


def crear_venta(subtotal_usd: float, iva_usd: float, total_usd: float,
                tasa_cambio: float, total_bs: float, forma_pago: str,
                detalles: List[dict], cliente_id: int = None,
                referencia_pago: str = None, monto_recibido: float = None,
                vuelto: float = 0) -> int:
    """Crea una nueva venta con sus detalles y retorna el ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        numero_factura = f'FAC-{datetime.now().strftime("%Y%m%d")}-{_get_next_factura_num(cursor):05d}'
        
        # Insertar venta
        cursor.execute('''
            INSERT INTO ventas (numero_factura, cliente_id, subtotal_usd, iva_usd,
                               total_usd, tasa_cambio, total_bs, forma_pago,
                               referencia_pago, monto_recibido, vuelto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (numero_factura, cliente_id, subtotal_usd, iva_usd, total_usd,
              tasa_cambio, total_bs, forma_pago, referencia_pago, monto_recibido, vuelto))
        
        venta_id = cursor.lastrowid
        
        # Insertar detalles y actualizar stock en la misma transacción
        for detalle in detalles:
            cursor.execute('''
                INSERT INTO detalle_ventas (venta_id, producto_id, nombre_producto,
                                            cantidad, precio_unit_usd, descuento, total_linea_usd)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (venta_id, detalle['producto_id'], detalle['nombre_producto'],
                  detalle['cantidad'], detalle['precio_unit_usd'], 
                  detalle.get('descuento', 0), detalle['total_linea_usd']))
            
            # Actualizar stock directamente en la misma transacción
            cursor.execute('''
                UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?
            ''', (detalle['cantidad'], detalle['producto_id']))
            
            # Obtener stock anterior para el movimiento
            cursor.execute('SELECT stock_actual FROM productos WHERE id = ?', (detalle['producto_id'],))
            stock_nuevo = cursor.fetchone()['stock_actual']
            stock_anterior = stock_nuevo + detalle['cantidad']
            
            # Registrar movimiento
            cursor.execute('''
                INSERT INTO movimientos_inventario 
                (producto_id, tipo, cantidad, stock_anterior, stock_nuevo, referencia, observacion)
                VALUES (?, 'Salida', ?, ?, ?, ?, 'Venta')
            ''', (detalle['producto_id'], detalle['cantidad'], stock_anterior, stock_nuevo, numero_factura))
        
        conn.commit()
        return venta_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def _get_next_factura_num(cursor) -> int:
    """Obtiene el siguiente número de factura (uso interno)."""
    cursor.execute('SELECT COUNT(*) + 1 as num FROM ventas')
    row = cursor.fetchone()
    return row['num'] if row else 1


def get_ventas_del_dia() -> dict:
    """Obtiene resumen de ventas del día."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Usar fecha de hoy en formato local
    from datetime import datetime, timedelta
    hoy = datetime.now().date()
    fecha_ini = f"{hoy.isoformat()} 00:00:00"
    # Agregar 1 día para capturar ventas con hora UTC
    manana = hoy + timedelta(days=1)
    fecha_fin = f"{manana.isoformat()} 23:59:59"
    
    cursor.execute('''
        SELECT COUNT(*) as cantidad, 
               COALESCE(SUM(total_usd), 0) as total_usd,
               COALESCE(SUM(total_bs), 0) as total_bs
        FROM ventas 
        WHERE fecha BETWEEN ? AND ?
    ''', (fecha_ini, fecha_fin))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else {'cantidad': 0, 'total_usd': 0, 'total_bs': 0}


def get_ventas_del_mes() -> dict:
    """Obtiene resumen de ventas del mes actual."""
    conn = get_connection()
    cursor = conn.cursor()
    
    from datetime import datetime, timedelta
    hoy = datetime.now().date()
    primer_dia_mes = hoy.replace(day=1)
    fecha_ini = f"{primer_dia_mes.isoformat()} 00:00:00"
    # Agregar 1 día para capturar ventas con hora UTC
    manana = hoy + timedelta(days=1)
    fecha_fin = f"{manana.isoformat()} 23:59:59"
    
    cursor.execute('''
        SELECT COUNT(*) as cantidad, 
               COALESCE(SUM(total_usd), 0) as total_usd,
               COALESCE(SUM(total_bs), 0) as total_bs
        FROM ventas 
        WHERE fecha BETWEEN ? AND ?
    ''', (fecha_ini, fecha_fin))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else {'cantidad': 0, 'total_usd': 0, 'total_bs': 0}


def get_productos_bajo_stock() -> List[dict]:
    """Obtiene productos con stock bajo."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM productos 
        WHERE activo = 1 AND stock_actual <= stock_minimo
        ORDER BY stock_actual
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ============== FUNCIONES DE MOVIMIENTOS ==============

def get_movimientos_producto(producto_id: int, limite: int = 50) -> List[dict]:
    """Obtiene el historial de movimientos de un producto."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.*, p.nombre as producto_nombre, p.codigo as producto_codigo
        FROM movimientos_inventario m
        JOIN productos p ON m.producto_id = p.id
        WHERE m.producto_id = ?
        ORDER BY m.fecha DESC
        LIMIT ?
    ''', (producto_id, limite))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_todos_movimientos(limite: int = 100) -> List[dict]:
    """Obtiene todos los movimientos de inventario recientes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.*, p.nombre as producto_nombre, p.codigo as producto_codigo
        FROM movimientos_inventario m
        JOIN productos p ON m.producto_id = p.id
        ORDER BY m.fecha DESC
        LIMIT ?
    ''', (limite,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ============== FUNCIONES DE SEGURIDAD ==============

def guardar_password_admin(password: str) -> bool:
    """Guarda la contraseña de administrador (hash simple)."""
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_connection()
    cursor = conn.cursor()
    # Actualizar la contraseña en el registro existente
    cursor.execute('UPDATE configuracion SET password_admin = ? WHERE id = 1', (password_hash,))
    if cursor.rowcount == 0:
        # Si no existe registro, crear uno
        cursor.execute('INSERT INTO configuracion (id, password_admin) VALUES (1, ?)', (password_hash,))
    conn.commit()
    conn.close()
    return True


def verificar_password_admin(password: str) -> bool:
    """Verifica si la contraseña de administrador es correcta."""
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_admin FROM configuracion WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row['password_admin']:
        return False
    
    return row['password_admin'] == password_hash


def existe_password_admin() -> bool:
    """Verifica si existe una contraseña de administrador configurada."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_admin FROM configuracion WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return row is not None and row['password_admin'] is not None


def limpiar_base_datos() -> bool:
    """Limpia todas las ventas, detalles y movimientos. Mantiene productos y configuración."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Eliminar en orden correcto por dependencias
        cursor.execute('DELETE FROM detalle_ventas')
        cursor.execute('DELETE FROM ventas')
        cursor.execute('DELETE FROM movimientos_inventario')
        
        # Resetear stock de productos a 0
        cursor.execute('UPDATE productos SET stock_actual = 0')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error limpiando base de datos: {e}")
        return False


# ============== FUNCIONES DE COMPRAS ==============

def crear_compra(proveedor: str, observacion: str, detalles: List[dict], 
                 total_usd: float) -> int:
    """Crea una nueva compra con sus detalles y actualiza stock."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Generar número de compra
        numero_compra = f"COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Insertar compra
        cursor.execute('''
            INSERT INTO compras (numero_compra, proveedor, total_usd, observacion)
            VALUES (?, ?, ?, ?)
        ''', (numero_compra, proveedor, total_usd, observacion))
        
        compra_id = cursor.lastrowid
        
        # Insertar detalles y actualizar stock
        for detalle in detalles:
            cursor.execute('''
                INSERT INTO detalle_compras (compra_id, producto_id, nombre_producto,
                                             cantidad, costo_unit_usd, total_linea_usd)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (compra_id, detalle['producto_id'], detalle['nombre_producto'],
                  detalle['cantidad'], detalle['costo_unit_usd'], detalle['total_linea_usd']))
            
            # Obtener porcentaje de ganancia del producto
            cursor.execute('SELECT porcentaje_ganancia FROM productos WHERE id = ?', (detalle['producto_id'],))
            row = cursor.fetchone()
            porcentaje = row['porcentaje_ganancia'] if row and row['porcentaje_ganancia'] else 30
            
            # Calcular nuevo precio de venta basado en el costo y porcentaje de ganancia
            nuevo_precio = detalle['costo_unit_usd'] * (1 + porcentaje / 100)
            
            # Actualizar stock, costo y precio
            cursor.execute('''
                UPDATE productos SET stock_actual = stock_actual + ?, costo_usd = ?, precio_usd = ?
                WHERE id = ?
            ''', (detalle['cantidad'], detalle['costo_unit_usd'], nuevo_precio, detalle['producto_id']))
            
            # Obtener stock nuevo para el movimiento
            cursor.execute('SELECT stock_actual FROM productos WHERE id = ?', (detalle['producto_id'],))
            stock_nuevo = cursor.fetchone()['stock_actual']
            stock_anterior = stock_nuevo - detalle['cantidad']
            
            # Registrar movimiento
            cursor.execute('''
                INSERT INTO movimientos_inventario 
                (producto_id, tipo, cantidad, stock_anterior, stock_nuevo, referencia, observacion)
                VALUES (?, 'Entrada', ?, ?, ?, ?, 'Compra')
            ''', (detalle['producto_id'], detalle['cantidad'], stock_anterior, stock_nuevo, numero_compra))
        
        conn.commit()
        return compra_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_compras(limite: int = 100) -> List[dict]:
    """Obtiene la lista de compras."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM compras ORDER BY fecha DESC LIMIT ?
    ''', (limite,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Inicializar la base de datos al importar el módulo
if __name__ == '__main__':
    init_database()

