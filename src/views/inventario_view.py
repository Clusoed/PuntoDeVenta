"""
Vista de Control de Inventario - Diseño Minimalista
"""
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    get_productos, get_productos_bajo_stock, actualizar_stock,
    get_connection, get_tasa_actual, get_movimientos_producto, get_todos_movimientos
)
from utils.currency import formato_usd, formato_bs
from utils.theme import BG_PRINCIPAL, BG_SECUNDARIO, BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY, WARNING, BG_HOVER, ERROR, ACCENT_HOVER
from utils.excel_import import ImportDialog, generar_plantilla_excel
from tkinter import filedialog


class InventarioView(ctk.CTkFrame):
    """Vista de control de inventario."""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=BG_PRINCIPAL)
        self.app = app_controller
        self.productos = []
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configura la interfaz de inventario."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_header,
            text="📊 CONTROL DE INVENTARIO",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Botones de acción
        frame_acciones = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_acciones.grid(row=0, column=2)
        
        ctk.CTkButton(
            frame_acciones,
            text="📥 Entrada",
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=lambda: self.abrir_ajuste("Entrada")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_acciones,
            text="📤 Salida",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="#ffffff",
            command=lambda: self.abrir_ajuste("Salida")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_acciones,
            text="📝 Movimientos",
            fg_color="#3a4a6b",
            hover_color="#4a5a7b",
            text_color="#ffffff",
            command=self.ver_movimientos
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
        
        # === FILTROS ===
        frame_filtros = ctk.CTkFrame(self, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_filtros.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Búsqueda
        self.entry_buscar = ctk.CTkEntry(
            frame_filtros,
            width=300,
            placeholder_text="🔍 Buscar producto..."
        )
        self.entry_buscar.pack(side="left", padx=10, pady=10)
        self.entry_buscar.bind("<KeyRelease>", self.filtrar_productos)
        
        # Filtro stock bajo
        self.var_stock_bajo = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame_filtros,
            text="⚠️ Solo stock bajo",
            variable=self.var_stock_bajo,
            command=self.filtrar_productos
        ).pack(side="left", padx=20)
        
        # Valorización
        self.lbl_valorizacion = ctk.CTkLabel(
            frame_filtros,
            text="Valor total: $ 0.00 | Bs 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ACCENT_PRIMARY
        )
        self.lbl_valorizacion.pack(side="right", padx=20)
        
        # === TABLA DE INVENTARIO ===
        self.frame_tabla = ctk.CTkScrollableFrame(self)
        self.frame_tabla.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        for i in range(7):
            self.frame_tabla.grid_columnconfigure(i, weight=1)
    
    def cargar_datos(self):
        """Carga los productos de la base de datos."""
        self.productos = get_productos()
        self.mostrar_inventario()
        self.calcular_valorizacion()
    
    def mostrar_inventario(self, productos=None):
        """Muestra el inventario en la tabla."""
        # Limpiar tabla
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        
        # Headers
        headers = ["Código", "Nombre", "Stock", "Mínimo", "Estado", "Valor USD", "Valor Bs"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                self.frame_tabla,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                fg_color=BG_HOVER,
                text_color=TEXT_SECONDARY,
                corner_radius=5,
                padx=10,
                pady=8
            ).grid(row=0, column=i, sticky="ew", padx=2, pady=2)
        
        productos_mostrar = productos if productos is not None else self.productos
        tasa = get_tasa_actual()
        
        for idx, prod in enumerate(productos_mostrar, start=1):
            stock = prod['stock_actual']
            stock_min = prod['stock_minimo']
            precio_usd = prod['precio_usd']
            valor_usd = stock * precio_usd
            valor_bs = valor_usd * tasa
            
            # Determinar estado
            if stock <= 0:
                estado = "❌ Sin Stock"
                color_estado = "#ff4444"
            elif stock <= stock_min:
                estado = "⚠️ Bajo"
                color_estado = "#ffa500"
            else:
                estado = "✅ OK"
                color_estado = "#00ff00"
            
            bg_color = "gray20" if idx % 2 == 0 else "transparent"
            
            # Código
            ctk.CTkLabel(
                self.frame_tabla, text=prod['codigo'],
                fg_color=bg_color, padx=10, pady=5
            ).grid(row=idx, column=0, sticky="ew", padx=2)
            
            # Nombre
            ctk.CTkLabel(
                self.frame_tabla, text=prod['nombre'],
                fg_color=bg_color, padx=10, pady=5
            ).grid(row=idx, column=1, sticky="ew", padx=2)
            
            # Stock
            ctk.CTkLabel(
                self.frame_tabla, text=str(stock),
                fg_color=bg_color, padx=10, pady=5,
                text_color=color_estado
            ).grid(row=idx, column=2, sticky="ew", padx=2)
            
            # Mínimo
            ctk.CTkLabel(
                self.frame_tabla, text=str(stock_min),
                fg_color=bg_color, padx=10, pady=5
            ).grid(row=idx, column=3, sticky="ew", padx=2)
            
            # Estado
            ctk.CTkLabel(
                self.frame_tabla, text=estado,
                fg_color=bg_color, padx=10, pady=5,
                text_color=color_estado
            ).grid(row=idx, column=4, sticky="ew", padx=2)
            
            # Valor USD
            ctk.CTkLabel(
                self.frame_tabla, text=formato_usd(valor_usd),
                fg_color=bg_color, padx=10, pady=5,
                text_color="#0ea5e9"
            ).grid(row=idx, column=5, sticky="ew", padx=2)
            
            # Valor Bs
            ctk.CTkLabel(
                self.frame_tabla, text=formato_bs(valor_bs),
                fg_color=bg_color, padx=10, pady=5,
                text_color="#ffa500"
            ).grid(row=idx, column=6, sticky="ew", padx=2)
    
    def filtrar_productos(self, event=None):
        """Filtra productos según búsqueda y filtros."""
        termino = self.entry_buscar.get().strip().lower()
        solo_bajo = self.var_stock_bajo.get()
        
        filtrados = self.productos
        
        if termino:
            filtrados = [
                p for p in filtrados
                if termino in p['codigo'].lower() or termino in p['nombre'].lower()
            ]
        
        if solo_bajo:
            filtrados = [
                p for p in filtrados
                if p['stock_actual'] <= p['stock_minimo']
            ]
        
        self.mostrar_inventario(filtrados)
    
    def calcular_valorizacion(self):
        """Calcula el valor total del inventario."""
        tasa = get_tasa_actual()
        total_usd = sum(p['stock_actual'] * p['precio_usd'] for p in self.productos)
        total_bs = total_usd * tasa
        
        self.lbl_valorizacion.configure(
            text=f"Valor total: {formato_usd(total_usd)} | {formato_bs(total_bs)}"
        )
    
    def abrir_ajuste(self, tipo: str):
        """Abre el formulario de ajuste de inventario."""
        FormularioAjuste(self, tipo, self.productos, self.ejecutar_ajuste)
    
    def ejecutar_ajuste(self, producto_id: int, cantidad: int, tipo: str, observacion: str):
        """Ejecuta un ajuste de inventario."""
        tipo_mov = "Entrada" if tipo == "Entrada" else "Salida"
        
        if actualizar_stock(producto_id, cantidad, tipo_mov, observacion=observacion):
            self.cargar_datos()
            CTkMessagebox(
                title="Éxito",
                message=f"{tipo_mov} registrada correctamente",
                icon="check"
            )
        else:
            CTkMessagebox(
                title="Error",
                message="Error al registrar el movimiento",
                icon="cancel"
            )
    
    def ver_movimientos(self):
        """Abre el diálogo de movimientos."""
        DialogoMovimientos(self)
    
    def descargar_plantilla(self):
        """Descarga la plantilla Excel para importar inventario."""
        try:
            ruta = filedialog.asksaveasfilename(
                title="Guardar plantilla",
                defaultextension=".xlsx",
                initialfile="Plantilla_Inventario.xlsx",
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
        """Abre el diálogo de importación de inventario."""
        ImportDialog(self, callback=self.cargar_datos)


class FormularioAjuste(ctk.CTkToplevel):
    """Formulario para ajustes de inventario."""
    
    def __init__(self, parent, tipo: str, productos: list, callback):
        super().__init__(parent)
        
        # Configurar color de fondo oscuro ANTES de todo para evitar flash blanco
        self.configure(fg_color="#1a1a2e")
        
        # Ocultar la ventana mientras se configura
        self.withdraw()
        
        self.tipo = tipo
        self.productos = productos
        self.callback = callback
        
        self.title(f"📥 Entrada de Inventario" if tipo == "Entrada" else "📤 Salida de Inventario")
        self.geometry("450x350")
        self.resizable(False, False)
        
        # Centrar ventana - usar solo transient (no grab_set para evitar flash)
        self.transient(parent)
        
        self.setup_ui()
        
        # Centrar en la pantalla y mostrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"450x350+{x}+{y}")
        self.deiconify()
    
    def setup_ui(self):
        """Configura el formulario."""
        # Producto
        ctk.CTkLabel(self, text="Producto:*").pack(pady=(20, 5), padx=20, anchor="w")
        
        productos_nombres = [f"{p['codigo']} - {p['nombre']}" for p in self.productos]
        self.cmb_producto = ctk.CTkComboBox(self, values=productos_nombres, width=400)
        self.cmb_producto.pack(padx=20, anchor="w")
        
        # Cantidad
        ctk.CTkLabel(self, text="Cantidad:*").pack(pady=(15, 5), padx=20, anchor="w")
        self.entry_cantidad = ctk.CTkEntry(self, width=150)
        self.entry_cantidad.pack(padx=20, anchor="w")
        
        # Observación
        ctk.CTkLabel(self, text="Observación:").pack(pady=(15, 5), padx=20, anchor="w")
        self.entry_observacion = ctk.CTkEntry(self, width=400)
        self.entry_observacion.pack(padx=20, anchor="w")
        
        # Color según tipo
        color = "#28a745" if self.tipo == "Entrada" else "#dc3545"
        
        # Botones
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(fill="x", padx=20, pady=30)
        
        ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            fg_color="gray",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            frame_botones,
            text=f"✓ Registrar {self.tipo}",
            fg_color=color,
            command=self.guardar
        ).pack(side="right")
    
    def guardar(self):
        """Guarda el ajuste."""
        producto_str = self.cmb_producto.get()
        cantidad_str = self.entry_cantidad.get().strip()
        observacion = self.entry_observacion.get().strip()
        
        if not producto_str:
            CTkMessagebox(title="Error", message="Seleccione un producto", icon="warning")
            return
        
        if not cantidad_str:
            CTkMessagebox(title="Error", message="Ingrese la cantidad", icon="warning")
            return
        
        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                raise ValueError()
        except:
            CTkMessagebox(title="Error", message="La cantidad debe ser un número positivo", icon="warning")
            return
        
        # Obtener producto_id
        codigo = producto_str.split(" - ")[0]
        producto_id = None
        for p in self.productos:
            if p['codigo'] == codigo:
                producto_id = p['id']
                break
        
        if producto_id:
            self.callback(producto_id, cantidad, self.tipo, observacion)
            self.destroy()


class DialogoMovimientos(ctk.CTkToplevel):
    """Diálogo para ver historial de movimientos."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configurar color de fondo oscuro ANTES de todo para evitar flash blanco
        self.configure(fg_color="#1a1a2e")
        
        # Ocultar la ventana mientras se configura
        self.withdraw()
        
        self.title("📝 Historial de Movimientos")
        self.geometry("800x500")
        self.resizable(True, True)
        
        # Centrar ventana - usar solo transient (no grab_set para evitar flash)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        
        self.setup_ui()
        self.cargar_movimientos()
        
        # Centrar en la pantalla y mostrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 800) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"800x500+{x}+{y}")
        self.deiconify()
    
    def cerrar(self):
        try:
            self.grab_release()
        except:
            pass
        self.withdraw()
        self.after(50, self.destroy)
    
    def setup_ui(self):
        """Configura la interfaz."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            frame_header,
            text="📝 Historial de Movimientos de Inventario",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            frame_header,
            text="🔄 Actualizar",
            width=100,
            command=self.cargar_movimientos
        ).pack(side="right", padx=10)
        
        # Tabla de movimientos
        self.frame_tabla = ctk.CTkScrollableFrame(self)
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        for i in range(7):
            self.frame_tabla.grid_columnconfigure(i, weight=1)
        
        # Botón cerrar
        ctk.CTkButton(
            self,
            text="Cerrar",
            command=self.cerrar
        ).grid(row=2, column=0, pady=10)
    
    def cargar_movimientos(self):
        """Carga los movimientos en la tabla."""
        # Limpiar tabla
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        
        # Headers
        headers = ["Fecha", "Producto", "Tipo", "Cantidad", "Anterior", "Nuevo", "Observación"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                self.frame_tabla,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                fg_color="gray30",
                corner_radius=3,
                padx=8,
                pady=6
            ).grid(row=0, column=i, sticky="ew", padx=1, pady=1)
        
        # Obtener movimientos
        movimientos = get_todos_movimientos(100)
        
        for idx, mov in enumerate(movimientos, start=1):
            bg_color = "gray20" if idx % 2 == 0 else "transparent"
            
            # Formatear fecha
            from datetime import datetime
            fecha = mov.get('fecha', '')
            try:
                fecha = datetime.fromisoformat(fecha).strftime('%d/%m/%Y %H:%M')
            except:
                pass
            
            # Color según tipo
            tipo = mov.get('tipo', '')
            if tipo in ['Entrada', 'Ajuste+']:
                text_color = "#28a745"
            elif tipo in ['Salida', 'Ajuste-']:
                text_color = "#dc3545"
            else:
                text_color = "white"
            
            ctk.CTkLabel(
                self.frame_tabla, text=fecha,
                fg_color=bg_color, padx=5, pady=3
            ).grid(row=idx, column=0, sticky="ew", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla, text=mov.get('producto_nombre', '')[:25],
                fg_color=bg_color, padx=5, pady=3
            ).grid(row=idx, column=1, sticky="ew", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla, text=tipo,
                fg_color=bg_color, padx=5, pady=3,
                text_color=text_color
            ).grid(row=idx, column=2, sticky="ew", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla, text=str(mov.get('cantidad', 0)),
                fg_color=bg_color, padx=5, pady=3
            ).grid(row=idx, column=3, sticky="ew", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla, text=str(mov.get('stock_anterior', 0)),
                fg_color=bg_color, padx=5, pady=3
            ).grid(row=idx, column=4, sticky="ew", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla, text=str(mov.get('stock_nuevo', 0)),
                fg_color=bg_color, padx=5, pady=3
            ).grid(row=idx, column=5, sticky="ew", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla, text=mov.get('observacion', '') or '',
                fg_color=bg_color, padx=5, pady=3
            ).grid(row=idx, column=6, sticky="ew", padx=1)

