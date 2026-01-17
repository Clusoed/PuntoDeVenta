"""
Vista de Gestión de Compras (Entrada de Inventario) - Diseño Minimalista
"""
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    get_productos, buscar_productos, crear_compra, get_compras
)
from utils.currency import formato_usd, formato_bs, get_tasa_global
from utils.theme import BG_PRINCIPAL, BG_SECUNDARIO, BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY, BG_HOVER


class ComprasView(ctk.CTkFrame):
    """Vista para registrar compras/entradas de inventario."""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=BG_PRINCIPAL)
        self.app = app_controller
        self.carrito = []
        self.tasa = get_tasa_global()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de compras."""
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            frame_header,
            text="📥 REGISTRO DE COMPRAS",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        
        # === PANEL IZQUIERDO: Búsqueda y carrito ===
        frame_izq = ctk.CTkFrame(self, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_izq.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        frame_izq.grid_columnconfigure(0, weight=1)
        frame_izq.grid_rowconfigure(3, weight=1)
        
        # Búsqueda de productos
        frame_buscar = ctk.CTkFrame(frame_izq, fg_color="transparent")
        frame_buscar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(frame_buscar, text="Buscar Producto:").pack(side="left", padx=5)
        self.entry_buscar = ctk.CTkEntry(frame_buscar, width=300, placeholder_text="Código o nombre...")
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind('<KeyRelease>', self.buscar_producto)
        
        # Frame para sugerencias
        self.frame_sugerencias = ctk.CTkFrame(frame_izq)
        self.frame_sugerencias.grid(row=1, column=0, sticky="ew", padx=10)
        self.frame_sugerencias.grid_remove()
        
        # Tabla del carrito
        ctk.CTkLabel(
            frame_izq, text="📦 Productos a Ingresar",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=2, column=0, sticky="nw", padx=10, pady=(5, 3))
        
        self.frame_tabla = ctk.CTkScrollableFrame(frame_izq, height=300)
        self.frame_tabla.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 5))
        
        for i in range(6):
            self.frame_tabla.grid_columnconfigure(i, weight=1)
        
        self.actualizar_tabla_carrito()
        
        # === PANEL DERECHO: Datos de compra y resumen ===
        frame_der = ctk.CTkFrame(self, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_der.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Datos del proveedor
        ctk.CTkLabel(
            frame_der, text="📋 Datos de la Compra",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(frame_der, text="Proveedor (opcional):").pack(anchor="w", padx=15)
        self.entry_proveedor = ctk.CTkEntry(frame_der, width=250, placeholder_text="Nombre del proveedor")
        self.entry_proveedor.pack(padx=15, pady=5)
        
        ctk.CTkLabel(frame_der, text="Observación:").pack(anchor="w", padx=15, pady=(10, 0))
        self.entry_observacion = ctk.CTkEntry(frame_der, width=250, placeholder_text="Nota opcional...")
        self.entry_observacion.pack(padx=15, pady=5)
        
        # Resumen
        ctk.CTkLabel(
            frame_der, text="💰 RESUMEN",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 8))
        
        self.lbl_total = ctk.CTkLabel(
            frame_der, text="$ 0.00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=ACCENT_PRIMARY
        )
        self.lbl_total.pack(pady=5)
        
        self.lbl_items = ctk.CTkLabel(
            frame_der, text="0 productos",
            font=ctk.CTkFont(size=14)
        )
        self.lbl_items.pack(pady=5)
        
        # Botones
        ctk.CTkButton(
            frame_der,
            text="✅ REGISTRAR COMPRA",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=ACCENT_PRIMARY,
            hover_color="#0284c7",
            command=self.registrar_compra
        ).pack(pady=10, padx=15, fill="x")
        
        ctk.CTkButton(
            frame_der,
            text="🗑️ Limpiar",
            fg_color="#3a4a6b",
            hover_color="#4a5a7b",
            text_color="#ffffff",
            command=self.limpiar_carrito
        ).pack(pady=5, padx=15, fill="x")
    
    def buscar_producto(self, event=None):
        """Busca productos mientras se escribe."""
        termino = self.entry_buscar.get().strip()
        
        if len(termino) < 2:
            self.frame_sugerencias.grid_remove()
            return
        
        productos = buscar_productos(termino)[:5]
        
        # Limpiar sugerencias anteriores
        for widget in self.frame_sugerencias.winfo_children():
            widget.destroy()
        
        if productos:
            self.frame_sugerencias.grid()
            for producto in productos:
                btn = ctk.CTkButton(
                    self.frame_sugerencias,
                    text=f"{producto['codigo']} - {producto['nombre']} (Stock: {producto['stock_actual']})",
                    anchor="w",
                    fg_color="transparent",
                    text_color="white",
                    hover_color="gray30",
                    command=lambda p=producto: self.abrir_dialogo_cantidad(p)
                )
                btn.pack(fill="x", padx=5, pady=2)
        else:
            self.frame_sugerencias.grid_remove()
    
    def abrir_dialogo_cantidad(self, producto: dict):
        """Abre diálogo para ingresar cantidad y costo."""
        self.frame_sugerencias.grid_remove()
        self.entry_buscar.delete(0, 'end')
        
        dialogo = DialogoCompra(self, producto, self.agregar_al_carrito)
    
    def agregar_al_carrito(self, producto_id: int, nombre: str, cantidad: int, costo_usd: float):
        """Agrega un producto al carrito de compra."""
        # Verificar si ya está
        for item in self.carrito:
            if item['producto_id'] == producto_id:
                item['cantidad'] += cantidad
                item['total_linea_usd'] = item['cantidad'] * item['costo_unit_usd']
                self.actualizar_tabla_carrito()
                self.calcular_totales()
                return
        
        # Agregar nuevo
        item = {
            'producto_id': producto_id,
            'nombre_producto': nombre,
            'cantidad': cantidad,
            'costo_unit_usd': costo_usd,
            'total_linea_usd': cantidad * costo_usd
        }
        self.carrito.append(item)
        self.actualizar_tabla_carrito()
        self.calcular_totales()
    
    def actualizar_tabla_carrito(self):
        """Actualiza la tabla del carrito."""
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        
        # Headers
        headers = ["Producto", "Cantidad", "Costo Unit $", "Total $", ""]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                self.frame_tabla,
                text=header,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="gray30",
                padx=5, pady=5
            ).grid(row=0, column=i, sticky="ew", padx=1, pady=1)
        
        # Productos
        for idx, item in enumerate(self.carrito, start=1):
            ctk.CTkLabel(self.frame_tabla, text=item['nombre_producto'][:30]).grid(row=idx, column=0, sticky="ew", padx=2)
            ctk.CTkLabel(self.frame_tabla, text=str(item['cantidad'])).grid(row=idx, column=1, sticky="ew", padx=2)
            ctk.CTkLabel(self.frame_tabla, text=formato_usd(item['costo_unit_usd'])).grid(row=idx, column=2, sticky="ew", padx=2)
            ctk.CTkLabel(self.frame_tabla, text=formato_usd(item['total_linea_usd'])).grid(row=idx, column=3, sticky="ew", padx=2)
            
            ctk.CTkButton(
                self.frame_tabla,
                text="❌",
                width=30,
                fg_color="red",
                command=lambda i=idx-1: self.eliminar_item(i)
            ).grid(row=idx, column=4, padx=2)
    
    def eliminar_item(self, index: int):
        """Elimina un item del carrito."""
        if 0 <= index < len(self.carrito):
            self.carrito.pop(index)
            self.actualizar_tabla_carrito()
            self.calcular_totales()
    
    def calcular_totales(self):
        """Calcula los totales."""
        total = sum(item['total_linea_usd'] for item in self.carrito)
        items = sum(item['cantidad'] for item in self.carrito)
        
        self.lbl_total.configure(text=formato_usd(total))
        self.lbl_items.configure(text=f"{items} productos")
    
    def registrar_compra(self):
        """Registra la compra en el sistema."""
        if not self.carrito:
            CTkMessagebox(title="Error", message="Agregue productos al carrito", icon="warning")
            return
        
        proveedor = self.entry_proveedor.get().strip() or "Sin proveedor"
        observacion = self.entry_observacion.get().strip()
        total = sum(item['total_linea_usd'] for item in self.carrito)
        
        try:
            compra_id = crear_compra(proveedor, observacion, self.carrito, total)
            
            CTkMessagebox(
                title="✅ Compra Registrada",
                message=f"Compra registrada exitosamente.\n\n"
                        f"Se actualizó el stock de {len(self.carrito)} productos.",
                icon="check"
            )
            
            self.limpiar_carrito()
            
        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Error al registrar compra: {str(e)}",
                icon="cancel"
            )
    
    def limpiar_carrito(self):
        """Limpia el carrito."""
        self.carrito = []
        self.entry_proveedor.delete(0, 'end')
        self.entry_observacion.delete(0, 'end')
        self.actualizar_tabla_carrito()
        self.calcular_totales()


class DialogoCompra(ctk.CTkToplevel):
    """Diálogo para ingresar cantidad y costo de compra."""
    
    def __init__(self, parent, producto: dict, callback):
        super().__init__(parent)
        
        # Configurar color de fondo oscuro ANTES de todo para evitar flash blanco
        self.configure(fg_color="#1a1a2e")
        
        # Ocultar la ventana mientras se configura
        self.withdraw()
        
        self.producto = producto
        self.callback = callback
        
        self.title("Agregar Producto")
        self.geometry("350x350")
        self.resizable(False, False)
        
        # Centrar ventana - usar solo transient (no grab_set para evitar flash)
        self.transient(parent)
        
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        
        self.setup_ui()
        
        # Centrar en la pantalla y mostrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 350) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"350x350+{x}+{y}")
        self.deiconify()
    
    def cerrar(self):
        try:
            self.grab_release()
        except:
            pass
        self.withdraw()
        self.after(50, self.destroy)
    
    def setup_ui(self):
        ctk.CTkLabel(
            self,
            text=self.producto['nombre'],
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        ctk.CTkLabel(self, text=f"Stock actual: {self.producto['stock_actual']}").pack()
        
        # Cantidad
        ctk.CTkLabel(self, text="Cantidad a ingresar:").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_cantidad = ctk.CTkEntry(self, width=200)
        self.entry_cantidad.pack(padx=20)
        self.entry_cantidad.insert(0, "1")
        
        # Costo
        costo_actual = self.producto.get('costo_usd', 0) or 0
        ctk.CTkLabel(self, text="Costo unitario (USD):").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_costo = ctk.CTkEntry(self, width=200)
        self.entry_costo.pack(padx=20)
        self.entry_costo.insert(0, str(costo_actual))
        
        # Botones
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(pady=20)
        
        ctk.CTkButton(frame_btns, text="Cancelar", fg_color="gray", command=self.cerrar).pack(side="left", padx=10)
        ctk.CTkButton(frame_btns, text="Agregar", fg_color="#28a745", command=self.agregar).pack(side="left", padx=10)
    
    def agregar(self):
        try:
            cantidad = int(self.entry_cantidad.get())
            costo = float(self.entry_costo.get().replace(',', '.'))
            
            if cantidad <= 0:
                raise ValueError("Cantidad debe ser mayor a 0")
            if costo < 0:
                raise ValueError("Costo no puede ser negativo")
            
            self.callback(
                self.producto['id'],
                self.producto['nombre'],
                cantidad,
                costo
            )
            self.cerrar()
            
        except ValueError as e:
            CTkMessagebox(title="Error", message=str(e), icon="warning")
