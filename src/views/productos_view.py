"""
Vista de Gestión de Productos - Diseño Minimalista
"""
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    get_productos, get_categorias, crear_producto, generar_codigo_producto,
    actualizar_producto, eliminar_producto, get_tasa_actual
)
from utils.currency import formato_usd, formato_bs, usd_a_bs
from utils.theme import (
    BG_PRINCIPAL, BG_SECUNDARIO, BG_HOVER, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY
)
from utils.excel_import import ImportDialog, generar_plantilla_excel
from tkinter import filedialog


class ProductosView(ctk.CTkFrame):
    """Vista de gestión de productos."""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=BG_PRINCIPAL)
        self.app = app_controller
        self.productos = []
        self.categorias = []
        
        # Formulario pre-creado (oculto) para evitar parpadeo
        self.formulario_producto = None
        
        self.setup_ui()
        self.cargar_datos()
        
        # Pre-crear el formulario DESPUÉS de cargar datos (para tener las categorías)
        self._pre_crear_formulario()
    
    def setup_ui(self):
        """Configura la interfaz de productos."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_header,
            text="📦 GESTIÓN DE PRODUCTOS",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Botones de acción
        frame_acciones = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_acciones.grid(row=0, column=2, padx=10)
        
        # Botón nuevo producto
        ctk.CTkButton(
            frame_acciones,
            text="➕ Nuevo Producto",
            fg_color=ACCENT_PRIMARY,
            hover_color="#0284c7",
            command=self.abrir_formulario_nuevo
        ).pack(side="left", padx=5)
        
        # Separador visual
        ctk.CTkLabel(frame_acciones, text="|", text_color="gray50").pack(side="left", padx=10)
        
        # Botón descargar plantilla
        ctk.CTkButton(
            frame_acciones,
            text="📄 Plantilla",
            fg_color="gray50",
            hover_color="gray40",
            text_color="#ffffff",
            command=self.descargar_plantilla
        ).pack(side="left", padx=5)
        
        # Botón importar Excel
        ctk.CTkButton(
            frame_acciones,
            text="📥 Importar Excel",
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            text_color="#ffffff",
            command=self.abrir_importar
        ).pack(side="left", padx=5)
        
        # Búsqueda
        frame_busqueda = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_busqueda.grid(row=0, column=1, sticky="e", padx=20)
        
        self.entry_buscar = ctk.CTkEntry(
            frame_busqueda,
            width=250,
            placeholder_text="🔍 Buscar por código o nombre..."
        )
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind("<KeyRelease>", self.buscar_productos)
        
        # === TABLA DE PRODUCTOS ===
        self.frame_tabla = ctk.CTkScrollableFrame(self)
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configurar columnas
        for i in range(7):
            self.frame_tabla.grid_columnconfigure(i, weight=1)
    
    def cargar_datos(self):
        """Carga los productos de la base de datos."""
        self.productos = get_productos()
        self.categorias = get_categorias()
        self.mostrar_productos()
    
    def mostrar_productos(self, productos=None):
        """Muestra los productos en la tabla."""
        # Limpiar tabla
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        
        # Headers
        headers = ["Código", "Nombre", "Categoría", "Precio USD", "Precio Bs", "Stock", "Acciones"]
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.frame_tabla,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                fg_color=BG_HOVER,
                text_color=TEXT_SECONDARY,
                corner_radius=5,
                padx=10,
                pady=8
            )
            lbl.grid(row=0, column=i, sticky="ew", padx=2, pady=2)
        
        # Datos
        productos_mostrar = productos if productos is not None else self.productos
        tasa = get_tasa_actual()
        
        for idx, prod in enumerate(productos_mostrar, start=1):
            # Código
            ctk.CTkLabel(
                self.frame_tabla,
                text=prod['codigo'],
                fg_color="gray20" if idx % 2 == 0 else "transparent",
                padx=10,
                pady=5
            ).grid(row=idx, column=0, sticky="ew", padx=2)
            
            # Nombre
            ctk.CTkLabel(
                self.frame_tabla,
                text=prod['nombre'],
                fg_color="gray20" if idx % 2 == 0 else "transparent",
                padx=10,
                pady=5
            ).grid(row=idx, column=1, sticky="ew", padx=2)
            
            # Categoría
            ctk.CTkLabel(
                self.frame_tabla,
                text=prod.get('categoria_nombre', '-'),
                fg_color="gray20" if idx % 2 == 0 else "transparent",
                padx=10,
                pady=5
            ).grid(row=idx, column=2, sticky="ew", padx=2)
            
            # Precio USD
            precio_usd = prod['precio_usd']
            ctk.CTkLabel(
                self.frame_tabla,
                text=formato_usd(precio_usd),
                fg_color="gray20" if idx % 2 == 0 else "transparent",
                text_color=ACCENT_PRIMARY,
                padx=10,
                pady=5
            ).grid(row=idx, column=3, sticky="ew", padx=2)
            
            # Precio Bs
            precio_bs = precio_usd * tasa
            ctk.CTkLabel(
                self.frame_tabla,
                text=formato_bs(precio_bs),
                fg_color="gray20" if idx % 2 == 0 else "transparent",
                text_color="#ffa500",
                padx=10,
                pady=5
            ).grid(row=idx, column=4, sticky="ew", padx=2)
            
            # Stock
            stock = prod['stock_actual']
            stock_min = prod['stock_minimo']
            color_stock = "#ff4444" if stock <= stock_min else "white"
            ctk.CTkLabel(
                self.frame_tabla,
                text=str(stock),
                fg_color="gray20" if idx % 2 == 0 else "transparent",
                text_color=color_stock,
                padx=10,
                pady=5
            ).grid(row=idx, column=5, sticky="ew", padx=2)
            
            # Acciones
            frame_acciones = ctk.CTkFrame(
                self.frame_tabla,
                fg_color="gray20" if idx % 2 == 0 else "transparent"
            )
            frame_acciones.grid(row=idx, column=6, sticky="ew", padx=2)
            
            ctk.CTkButton(
                frame_acciones,
                text="✏️",
                width=30,
                height=25,
                fg_color="#3a4a6b",
                hover_color="#4a5a7b",
                text_color="#ffffff",
                command=lambda p=prod: self.editar_producto(p)
            ).pack(side="left", padx=2, pady=2)
            
            ctk.CTkButton(
                frame_acciones,
                text="🗑️",
                width=30,
                height=25,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                text_color="#ffffff",
                command=lambda p=prod: self.eliminar_producto(p)
            ).pack(side="left", padx=2, pady=2)
    
    def buscar_productos(self, event=None):
        """Filtra productos según el término de búsqueda."""
        termino = self.entry_buscar.get().strip().lower()
        if not termino:
            self.mostrar_productos()
            return
        
        filtrados = [
            p for p in self.productos
            if termino in p['codigo'].lower() or termino in p['nombre'].lower()
        ]
        self.mostrar_productos(filtrados)
    
    def _pre_crear_formulario(self):
        """Pre-crea el formulario de producto oculto para evitar parpadeo."""
        self.formulario_producto = FormularioProducto(
            self, 
            self.categorias, 
            self.guardar_producto,
            pre_creado=True  # Indica que se crea oculto
        )
    
    def abrir_formulario_nuevo(self):
        """Abre el formulario pre-creado para crear un nuevo producto."""
        if self.formulario_producto and self.formulario_producto.winfo_exists():
            self.formulario_producto.mostrar_para_nuevo()
        else:
            # Re-crear si fue destruido
            self._pre_crear_formulario()
            self.formulario_producto.mostrar_para_nuevo()
    
    def guardar_producto(self, datos: dict):
        """Guarda un nuevo producto en la base de datos."""
        try:
            crear_producto(
                codigo=datos['codigo'],
                nombre=datos['nombre'],
                precio_usd=datos['precio_usd'],
                categoria_id=datos.get('categoria_id'),
                marca=datos.get('marca'),
                unidad_medida=datos.get('unidad_medida', 'Unidad'),
                costo_usd=datos.get('costo_usd', 0),
                stock_actual=datos.get('stock_actual', 0),
                stock_minimo=datos.get('stock_minimo', 5)
            )
            self.cargar_datos()
            CTkMessagebox(title="Éxito", message="Producto guardado correctamente", icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al guardar: {str(e)}", icon="cancel")
    
    def editar_producto(self, producto: dict):
        """Abre el formulario para editar un producto."""
        FormularioProducto(self, self.categorias, self.actualizar_producto, producto)
    
    def actualizar_producto(self, datos: dict):
        """Actualiza un producto existente."""
        try:
            resultado = actualizar_producto(
                producto_id=datos['id'],
                codigo=datos.get('codigo'),
                nombre=datos['nombre'],
                precio_usd=datos['precio_usd'],
                categoria_id=datos.get('categoria_id'),
                marca=datos.get('marca'),
                unidad_medida=datos.get('unidad_medida', 'Unidad'),
                costo_usd=datos.get('costo_usd', 0),
                stock_minimo=datos.get('stock_minimo', 5)
            )
            if resultado:
                self.cargar_datos()
                CTkMessagebox(title="Éxito", message="Producto actualizado correctamente", icon="check")
            else:
                CTkMessagebox(title="Error", message="Error al actualizar producto", icon="cancel")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error al actualizar: {str(e)}", icon="cancel")
    
    def eliminar_producto(self, producto: dict):
        """Desactiva un producto."""
        msg = CTkMessagebox(
            title="Confirmar",
            message=f"¿Desea eliminar el producto '{producto['nombre']}'?",
            icon="question",
            option_1="Cancelar",
            option_2="Eliminar"
        )
        
        if msg.get() == "Eliminar":
            if eliminar_producto(producto['id']):
                self.cargar_datos()
                CTkMessagebox(title="Éxito", message="Producto eliminado", icon="check")
            else:
                CTkMessagebox(title="Error", message="Error al eliminar producto", icon="cancel")
    
    def descargar_plantilla(self):
        """Descarga la plantilla Excel para importar productos."""
        try:
            ruta = filedialog.asksaveasfilename(
                title="Guardar plantilla",
                defaultextension=".xlsx",
                initialfile="Plantilla_Productos.xlsx",
                filetypes=[("Archivo Excel", "*.xlsx")]
            )
            
            if ruta:
                generar_plantilla_excel(ruta)
                CTkMessagebox(
                    title="Plantilla Generada",
                    message=f"La plantilla se guardó correctamente.\n\nRuta: {ruta}",
                    icon="check"
                )
        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Error al generar plantilla:\n{str(e)}",
                icon="cancel"
            )
    
    def abrir_importar(self):
        """Abre el diálogo de importación de productos desde Excel."""
        ImportDialog(self, callback=self.cargar_datos)


class FormularioProducto(ctk.CTkToplevel):
    """Formulario para crear/editar productos."""
    
    def __init__(self, parent, categorias, callback, producto=None, pre_creado=False):
        super().__init__(parent)
        
        # Configurar color de fondo oscuro PRIMERO
        self.configure(fg_color="#1a1a2e")
        
        # Si es pre-creado, ocultar inmediatamente
        if pre_creado:
            self.withdraw()
        
        # Guardar parámetros
        self.parent = parent
        self.categorias = categorias
        self.callback = callback
        self.producto = producto
        self.es_edicion = producto is not None
        self.pre_creado = pre_creado
        
        # Configurar ventana
        self.title("Editar Producto" if self.es_edicion else "Nuevo Producto")
        self.geometry("520x650")
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        
        # Crear widgets
        self.setup_ui()
        
        if self.es_edicion:
            self.cargar_producto()
        
        # Centrar en la pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 520) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"520x650+{x}+{y}")
    
    def mostrar_para_nuevo(self):
        """Muestra el formulario para crear un nuevo producto."""
        self.es_edicion = False
        self.producto = None
        self.title("Nuevo Producto")
        
        # Limpiar campos
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_codigo.insert(0, "Generando...")
        self.entry_codigo.configure(state="disabled")
        
        self.entry_nombre.delete(0, "end")
        self.cmb_categoria.set("Sin categoría")
        self.entry_marca.delete(0, "end")
        self.cmb_unidad.set("Unidad")
        self.entry_precio_usd.delete(0, "end")
        self.lbl_precio_bs.configure(text="Bs 0.00")
        self.entry_costo.delete(0, "end")
        self.entry_ganancia.delete(0, "end")
        self.entry_ganancia.insert(0, "30")
        self.entry_stock.configure(state="normal")
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, "0")
        self.entry_stock_min.delete(0, "end")
        self.entry_stock_min.insert(0, "5")
        
        # Mostrar la ventana
        self.deiconify()
        self.lift()
        self.focus_force()
        
        # Generar código después
        self.after(10, self._generar_codigo)
    
    def _generar_codigo(self):
        """Genera el código del producto."""
        codigo = generar_codigo_producto()
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_codigo.insert(0, codigo)
        self.entry_codigo.configure(state="disabled")
        self.entry_nombre.focus_set()
    
    def cerrar(self):
        """Cierra el formulario."""
        try:
            self.entry_costo.unbind("<KeyRelease>")
            self.entry_ganancia.unbind("<KeyRelease>")
        except Exception:
            pass
        
        if self.pre_creado:
            self.withdraw()
        else:
            self.destroy()
    
    def setup_ui(self):
        """Configura el formulario."""
        padding = {"padx": 20, "pady": 5}
        
        # Código
        ctk.CTkLabel(self, text="Código:").pack(anchor="w", **padding)
        self.entry_codigo = ctk.CTkEntry(self, width=200)
        self.entry_codigo.pack(anchor="w", padx=20)
        
        if not self.es_edicion:
            codigo = generar_codigo_producto()
            self.entry_codigo.insert(0, codigo)
            self.entry_codigo.configure(state="disabled")
        
        # Nombre
        ctk.CTkLabel(self, text="Nombre:*").pack(anchor="w", **padding)
        self.entry_nombre = ctk.CTkEntry(self, width=400)
        self.entry_nombre.pack(anchor="w", padx=20)
        
        # Categoría
        ctk.CTkLabel(self, text="Categoría:").pack(anchor="w", **padding)
        categorias_nombres = ["Sin categoría"] + [c['nombre'] for c in self.categorias]
        self.cmb_categoria = ctk.CTkComboBox(self, values=categorias_nombres, width=300)
        self.cmb_categoria.pack(anchor="w", padx=20)
        self.cmb_categoria.set("Sin categoría")
        
        # Marca
        ctk.CTkLabel(self, text="Marca:").pack(anchor="w", **padding)
        self.entry_marca = ctk.CTkEntry(self, width=300)
        self.entry_marca.pack(anchor="w", padx=20)
        
        # Unidad de medida
        ctk.CTkLabel(self, text="Unidad de Medida:").pack(anchor="w", **padding)
        self.cmb_unidad = ctk.CTkComboBox(
            self,
            values=["Unidad", "Kg", "Litro", "Metro", "Caja", "Paquete", "Docena"],
            width=200
        )
        self.cmb_unidad.pack(anchor="w", padx=20)
        self.cmb_unidad.set("Unidad")
        
        # Precios (en fila)
        frame_precios = ctk.CTkFrame(self, fg_color="transparent")
        frame_precios.pack(fill="x", padx=20, pady=10)
        
        # Precio USD
        frame_precio_usd = ctk.CTkFrame(frame_precios, fg_color="transparent")
        frame_precio_usd.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(frame_precio_usd, text="Precio USD:*").pack(anchor="w")
        self.entry_precio_usd = ctk.CTkEntry(frame_precio_usd, width=120)
        self.entry_precio_usd.pack(anchor="w")
        self.entry_precio_usd.bind("<KeyRelease>", self.calcular_precio_bs)
        
        # Precio Bs (calculado)
        frame_precio_bs = ctk.CTkFrame(frame_precios, fg_color="transparent")
        frame_precio_bs.pack(side="left")
        ctk.CTkLabel(frame_precio_bs, text="Precio Bs:").pack(anchor="w")
        self.lbl_precio_bs = ctk.CTkLabel(
            frame_precio_bs,
            text="Bs 0.00",
            font=ctk.CTkFont(size=16),
            text_color="#ffa500"
        )
        self.lbl_precio_bs.pack(anchor="w")
        
        # Costo y Porcentaje de ganancia (en fila)
        frame_costo = ctk.CTkFrame(self, fg_color="transparent")
        frame_costo.pack(fill="x", padx=20, pady=10)
        
        frame_costo_usd = ctk.CTkFrame(frame_costo, fg_color="transparent")
        frame_costo_usd.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(frame_costo_usd, text="Costo USD:").pack(anchor="w")
        self.entry_costo = ctk.CTkEntry(frame_costo_usd, width=120)
        self.entry_costo.pack(anchor="w")
        self.entry_costo.bind("<KeyRelease>", self.calcular_precio_desde_costo)
        
        frame_ganancia = ctk.CTkFrame(frame_costo, fg_color="transparent")
        frame_ganancia.pack(side="left")
        ctk.CTkLabel(frame_ganancia, text="% Ganancia:").pack(anchor="w")
        self.entry_ganancia = ctk.CTkEntry(frame_ganancia, width=80)
        self.entry_ganancia.pack(anchor="w")
        self.entry_ganancia.insert(0, "30")
        self.entry_ganancia.bind("<KeyRelease>", self.calcular_precio_desde_costo)
        
        # Stock (en fila)
        frame_stock = ctk.CTkFrame(self, fg_color="transparent")
        frame_stock.pack(fill="x", padx=20, pady=10)
        
        frame_stock_actual = ctk.CTkFrame(frame_stock, fg_color="transparent")
        frame_stock_actual.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(frame_stock_actual, text="Stock Inicial:").pack(anchor="w")
        self.entry_stock = ctk.CTkEntry(frame_stock_actual, width=100)
        self.entry_stock.pack(anchor="w")
        self.entry_stock.insert(0, "0")
        
        if self.es_edicion:
            self.entry_stock.configure(state="disabled")
        
        frame_stock_min = ctk.CTkFrame(frame_stock, fg_color="transparent")
        frame_stock_min.pack(side="left")
        ctk.CTkLabel(frame_stock_min, text="Stock Mínimo:").pack(anchor="w")
        self.entry_stock_min = ctk.CTkEntry(frame_stock_min, width=100)
        self.entry_stock_min.pack(anchor="w")
        self.entry_stock_min.insert(0, "5")
        
        # Botones
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            fg_color="gray",
            command=self.cerrar
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botones,
            text="💾 Guardar",
            command=self.guardar
        ).pack(side="right", padx=5)
    
    def calcular_precio_bs(self, event=None):
        """Calcula el precio en Bs."""
        try:
            precio_usd = float(self.entry_precio_usd.get() or 0)
            tasa = get_tasa_actual()
            precio_bs = precio_usd * tasa
            self.lbl_precio_bs.configure(text=formato_bs(precio_bs))
        except:
            self.lbl_precio_bs.configure(text="Bs 0.00")
    
    def calcular_precio_desde_costo(self, event=None):
        """Calcula el precio de venta basado en costo y porcentaje de ganancia."""
        try:
            if not self.winfo_exists():
                return
            if not self.entry_costo.winfo_exists():
                return
                
            costo = float(self.entry_costo.get() or 0)
            porcentaje = float(self.entry_ganancia.get() or 30)
            
            if costo > 0:
                precio = costo * (1 + porcentaje / 100)
                self.entry_precio_usd.delete(0, 'end')
                self.entry_precio_usd.insert(0, f"{precio:.2f}")
                self.calcular_precio_bs()
        except Exception:
            pass
    
    def cargar_producto(self):
        """Carga los datos del producto a editar."""
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, 'end')
        self.entry_codigo.insert(0, self.producto['codigo'])
        self.entry_codigo.configure(state="disabled")
        
        self.entry_nombre.insert(0, self.producto['nombre'])
        
        if self.producto.get('categoria_nombre'):
            self.cmb_categoria.set(self.producto['categoria_nombre'])
        
        if self.producto.get('marca'):
            self.entry_marca.insert(0, self.producto['marca'])
        
        if self.producto.get('unidad_medida'):
            self.cmb_unidad.set(self.producto['unidad_medida'])
        
        self.entry_precio_usd.insert(0, str(self.producto['precio_usd']))
        self.calcular_precio_bs()
        
        if self.producto.get('costo_usd'):
            self.entry_costo.insert(0, str(self.producto['costo_usd']))
        
        self.entry_ganancia.delete(0, 'end')
        self.entry_ganancia.insert(0, str(self.producto.get('porcentaje_ganancia', 30)))
        
        self.entry_stock_min.delete(0, 'end')
        self.entry_stock_min.insert(0, str(self.producto.get('stock_minimo', 5)))
    
    def guardar(self):
        """Valida y guarda el producto."""
        nombre = self.entry_nombre.get().strip()
        precio_str = self.entry_precio_usd.get().strip()
        
        if not nombre:
            CTkMessagebox(title="Error", message="El nombre es obligatorio", icon="warning")
            return
        
        if not precio_str:
            CTkMessagebox(title="Error", message="El precio es obligatorio", icon="warning")
            return
        
        try:
            precio_usd = float(precio_str)
        except:
            CTkMessagebox(title="Error", message="El precio debe ser un número válido", icon="warning")
            return
        
        # Obtener categoria_id
        categoria_nombre = self.cmb_categoria.get()
        categoria_id = None
        for cat in self.categorias:
            if cat['nombre'] == categoria_nombre:
                categoria_id = cat['id']
                break
        
        datos = {
            'codigo': self.entry_codigo.get(),
            'nombre': nombre,
            'precio_usd': precio_usd,
            'categoria_id': categoria_id,
            'marca': self.entry_marca.get().strip() or None,
            'unidad_medida': self.cmb_unidad.get(),
            'costo_usd': float(self.entry_costo.get() or 0),
            'porcentaje_ganancia': float(self.entry_ganancia.get() or 30),
            'stock_actual': int(self.entry_stock.get() or 0),
            'stock_minimo': int(self.entry_stock_min.get() or 5)
        }
        
        if self.es_edicion:
            datos['id'] = self.producto['id']
        
        self.callback(datos)
        self.cerrar()

