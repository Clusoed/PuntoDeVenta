"""
Vista del Punto de Venta (POS) - Diseño Minimalista
"""
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    buscar_productos, get_producto_por_codigo, crear_venta,
    get_tasa_actual, get_configuracion, get_clientes
)
from utils.currency import formato_usd, formato_bs, usd_a_bs
from utils.theme import (
    BG_PRINCIPAL, BG_SECUNDARIO, BG_HOVER, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_PRIMARY, ACCENT_HOVER, WARNING, ERROR,
    BTN_PRIMARY, BTN_DANGER
)


class POSView(ctk.CTkFrame):
    """Vista del Punto de Venta."""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=BG_PRINCIPAL)
        self.app = app_controller
        self.carrito = []  # Lista de productos en el carrito
        self.tasa = get_tasa_actual()
        config = get_configuracion()
        self.iva_porcentaje = config.get('iva_porcentaje', 16) / 100
        
        # Cargar clientes
        self.clientes = get_clientes()
        self.cliente_seleccionado_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del POS."""
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            frame_header,
            text="🛒 PUNTO DE VENTA",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Tasa actual
        ctk.CTkLabel(
            frame_header,
            text=f"💱 Tasa: Bs {self.tasa:,.2f}",
            font=ctk.CTkFont(size=16),
            text_color=ACCENT_PRIMARY
        ).pack(side="right", padx=20)
        
        # === COLUMNA IZQUIERDA: Búsqueda y Carrito ===
        frame_izq = ctk.CTkFrame(self, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_izq.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        frame_izq.grid_rowconfigure(1, weight=1)
        frame_izq.grid_columnconfigure(0, weight=1)
        
        self.setup_busqueda(frame_izq)
        self.setup_carrito(frame_izq)
        
        # === COLUMNA DERECHA: Resumen y Pago ===
        frame_der = ctk.CTkFrame(self, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_der.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        self.setup_resumen(frame_der)
        self.setup_pago(frame_der)
    
    def setup_busqueda(self, parent):
        """Configura la sección de búsqueda de productos."""
        frame_busqueda = ctk.CTkFrame(parent, fg_color="transparent")
        frame_busqueda.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            frame_busqueda,
            text="Buscar producto:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)
        
        self.entry_buscar = ctk.CTkEntry(
            frame_busqueda,
            width=300,
            placeholder_text="Código o nombre del producto..."
        )
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind("<Return>", self.buscar_producto)
        self.entry_buscar.bind("<KeyRelease>", self.mostrar_sugerencias)
        
        ctk.CTkButton(
            frame_busqueda,
            text="🔍 Buscar",
            width=100,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self.buscar_producto
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_busqueda,
            text="🗑️ Limpiar",
            width=80,
            fg_color="transparent",
            border_color=BORDER_COLOR,
            border_width=1,
            text_color=TEXT_SECONDARY,
            hover_color=BG_HOVER,
            command=self.limpiar_carrito
        ).pack(side="right", padx=10)
        
        # Frame para sugerencias
        self.frame_sugerencias = ctk.CTkFrame(parent, height=0)
        self.frame_sugerencias.grid(row=0, column=0, sticky="new", padx=10, pady=(60, 0))
        self.frame_sugerencias.grid_remove()
    
    def setup_carrito(self, parent):
        """Configura la tabla del carrito."""
        frame_carrito = ctk.CTkFrame(parent, fg_color="transparent")
        frame_carrito.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame_carrito.grid_columnconfigure(0, weight=1)
        frame_carrito.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_carrito,
            text="📋 PRODUCTOS EN CARRITO",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Tabla del carrito
        self.frame_tabla_carrito = ctk.CTkScrollableFrame(frame_carrito)
        self.frame_tabla_carrito.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        for i in range(6):
            self.frame_tabla_carrito.grid_columnconfigure(i, weight=1)
        
        self.actualizar_tabla_carrito()
    
    def setup_resumen(self, parent):
        """Configura el resumen de la venta."""
        # === SELECTOR DE CLIENTE ===
        frame_cliente = ctk.CTkFrame(parent)
        frame_cliente.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(
            frame_cliente,
            text="👤 CLIENTE",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=2)
        
        # Preparar opciones de clientes
        cliente_nombres = []
        self.cliente_ids = {}
        cliente_generico_idx = 0
        
        for idx, cliente in enumerate(self.clientes):
            nombre_display = f"{cliente['cedula_rif']} - {cliente['nombre']}"
            cliente_nombres.append(nombre_display)
            self.cliente_ids[nombre_display] = cliente['id']
            # Detectar cliente genérico
            if cliente['cedula_rif'] == '000000' or 'GENERICO' in cliente['nombre'].upper():
                cliente_generico_idx = idx
                self.cliente_seleccionado_id = cliente['id']
        
        # Dropdown de clientes
        if cliente_nombres:
            self.combo_cliente = ctk.CTkComboBox(
                frame_cliente,
                values=cliente_nombres,
                width=250,
                command=self.seleccionar_cliente
            )
            self.combo_cliente.set(cliente_nombres[cliente_generico_idx])
            self.combo_cliente.pack(pady=2)
        else:
            ctk.CTkLabel(
                frame_cliente,
                text="No hay clientes registrados",
                text_color="orange"
            ).pack(pady=5)
        
        # === RESUMEN ===
        frame_resumen = ctk.CTkFrame(parent)
        frame_resumen.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(
            frame_resumen,
            text="💰 RESUMEN",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=3)
        
        # Subtotal ($ y Bs en la misma línea)
        frame_subtotal = ctk.CTkFrame(frame_resumen, fg_color="transparent")
        frame_subtotal.pack(fill="x", padx=10, pady=1)
        ctk.CTkLabel(frame_subtotal, text="Subtotal:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.lbl_subtotal_bs = ctk.CTkLabel(frame_subtotal, text="Bs 0.00", text_color="#ffa500", font=ctk.CTkFont(size=12))
        self.lbl_subtotal_bs.pack(side="right")
        self.lbl_subtotal_usd = ctk.CTkLabel(frame_subtotal, text="$ 0.00", text_color=ACCENT_PRIMARY, font=ctk.CTkFont(size=12))
        self.lbl_subtotal_usd.pack(side="right", padx=(0, 10))
        
        # IVA ($ y Bs en la misma línea)
        iva_texto = f"IVA ({int(self.iva_porcentaje * 100)}%):"
        frame_iva = ctk.CTkFrame(frame_resumen, fg_color="transparent")
        frame_iva.pack(fill="x", padx=10, pady=1)
        ctk.CTkLabel(frame_iva, text=iva_texto, font=ctk.CTkFont(size=12)).pack(side="left")
        self.lbl_iva_bs = ctk.CTkLabel(frame_iva, text="Bs 0.00", text_color="#ffa500", font=ctk.CTkFont(size=12))
        self.lbl_iva_bs.pack(side="right")
        self.lbl_iva_usd = ctk.CTkLabel(frame_iva, text="$ 0.00", text_color=ACCENT_PRIMARY, font=ctk.CTkFont(size=12))
        self.lbl_iva_usd.pack(side="right", padx=(0, 10))
        
        # Total ($ y Bs en la misma línea)
        frame_total = ctk.CTkFrame(frame_resumen, fg_color="transparent")
        frame_total.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(frame_total, text="TOTAL:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        self.lbl_total_bs = ctk.CTkLabel(
            frame_total, text="Bs 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffa500"
        )
        self.lbl_total_bs.pack(side="right")
        self.lbl_total_usd = ctk.CTkLabel(
            frame_total, text="$ 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ACCENT_PRIMARY
        )
        self.lbl_total_usd.pack(side="right", padx=(0, 10))
    
    def setup_pago(self, parent):
        """Configura la sección de pago."""
        frame_pago = ctk.CTkFrame(parent)
        frame_pago.pack(fill="x", padx=10, pady=3)
        
        ctk.CTkLabel(
            frame_pago,
            text="💳 PAGO",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=2)
        
        # Forma de pago
        ctk.CTkLabel(frame_pago, text="Forma de pago:").pack(anchor="w", padx=15)
        self.cmb_forma_pago = ctk.CTkComboBox(
            frame_pago,
            values=["Efectivo", "Pago Móvil", "Punto de Venta"],
            width=200
        )
        self.cmb_forma_pago.pack(padx=15, pady=2, anchor="w")
        self.cmb_forma_pago.set("Efectivo")
        self.cmb_forma_pago.configure(command=self.cambiar_forma_pago)
        
        # Referencia (para Pago Móvil y Punto)
        self.lbl_referencia = ctk.CTkLabel(frame_pago, text="Referencia (opcional):")
        self.entry_referencia = ctk.CTkEntry(frame_pago, width=200, placeholder_text="Últimos 4 dígitos...")
        # Ocultos por defecto (Efectivo no requiere)
        
        # Monto recibido
        ctk.CTkLabel(frame_pago, text="Monto recibido:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(3, 0))
        self.entry_monto_recibido = ctk.CTkEntry(frame_pago, width=150, height=28)
        self.entry_monto_recibido.pack(padx=10, pady=1, anchor="w")
        self.entry_monto_recibido.bind("<KeyRelease>", self.calcular_vuelto)
        
        # Vuelto
        frame_vuelto = ctk.CTkFrame(frame_pago, fg_color="transparent")
        frame_vuelto.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame_vuelto, text="Vuelto:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.lbl_vuelto = ctk.CTkLabel(
            frame_vuelto,
            text="$ 0.00 / Bs 0.00",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_PRIMARY
        )
        self.lbl_vuelto.pack(side="right")
        
        # Botones
        frame_botones = ctk.CTkFrame(parent, fg_color="transparent")
        frame_botones.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            frame_botones,
            text="💳 COBRAR",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self.procesar_venta
        ).pack(fill="x", pady=2)
        
        ctk.CTkButton(
            frame_botones,
            text="❌ CANCELAR",
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="#ffffff",
            command=self.limpiar_carrito
        ).pack(fill="x", pady=2)
    
    def cambiar_forma_pago(self, forma_pago):
        """Muestra/oculta el campo de referencia según la forma de pago."""
        # Solo mostrar si es necesario, evitando repack
        if forma_pago in ["Pago Móvil", "Punto de Venta"]:
            if not self.lbl_referencia.winfo_ismapped():
                self.lbl_referencia.pack(anchor="w", padx=15, pady=(10, 0))
                self.entry_referencia.pack(padx=15, pady=5, anchor="w")
        else:
            self.lbl_referencia.pack_forget()
            self.entry_referencia.pack_forget()
    
    def seleccionar_cliente(self, valor):
        """Actualiza el cliente seleccionado."""
        if valor in self.cliente_ids:
            self.cliente_seleccionado_id = self.cliente_ids[valor]
    
    def mostrar_sugerencias(self, event=None):
        """Muestra sugerencias de productos mientras se escribe."""
        termino = self.entry_buscar.get().strip()
        
        # Limpiar sugerencias anteriores
        for widget in self.frame_sugerencias.winfo_children():
            widget.destroy()
        
        if len(termino) < 2:
            self.frame_sugerencias.grid_remove()
            return
        
        productos = buscar_productos(termino)[:5]  # Máximo 5 sugerencias
        
        if not productos:
            self.frame_sugerencias.grid_remove()
            return
        
        self.frame_sugerencias.grid()
        
        for prod in productos:
            precio_bs = prod['precio_usd'] * self.tasa
            texto = f"{prod['codigo']} - {prod['nombre']} | {formato_usd(prod['precio_usd'])} | {formato_bs(precio_bs)}"
            
            btn = ctk.CTkButton(
                self.frame_sugerencias,
                text=texto,
                anchor="w",
                fg_color="gray30",
                hover_color="gray40",
                command=lambda p=prod: self.agregar_al_carrito(p)
            )
            btn.pack(fill="x", padx=5, pady=2)
    
    def buscar_producto(self, event=None):
        """Busca un producto por código exacto."""
        codigo = self.entry_buscar.get().strip()
        if not codigo:
            return
        
        producto = get_producto_por_codigo(codigo)
        if producto:
            self.agregar_al_carrito(producto)
        else:
            # Mostrar sugerencias si no es código exacto
            productos = buscar_productos(codigo)
            if productos:
                self.agregar_al_carrito(productos[0])
            else:
                CTkMessagebox(title="No encontrado", message="Producto no encontrado", icon="warning")
    
    def agregar_al_carrito(self, producto: dict):
        """Agrega un producto al carrito."""
        self.frame_sugerencias.grid_remove()
        self.entry_buscar.delete(0, 'end')
        
        # Obtener stock actual y cantidad ya en carrito
        stock_actual = producto.get('stock_actual', 0)
        cantidad_en_carrito = 0
        
        for item in self.carrito:
            if item['producto_id'] == producto['id']:
                cantidad_en_carrito = item['cantidad']
                break
        
        nueva_cantidad = cantidad_en_carrito + 1
        
        # Verificar si hay stock suficiente
        if nueva_cantidad > stock_actual:
            msg = CTkMessagebox(
                title="⚠️ Stock Insuficiente",
                message=f"El producto '{producto['nombre']}' tiene solo {stock_actual} unidades en stock.\n\n"
                        f"Ya tienes {cantidad_en_carrito} en el carrito.\n\n"
                        f"¿Deseas agregar de todas formas?",
                icon="warning",
                option_1="Cancelar",
                option_2="Agregar"
            )
            if msg.get() != "Agregar":
                return
        
        # Verificar si ya está en el carrito
        for item in self.carrito:
            if item['producto_id'] == producto['id']:
                item['cantidad'] += 1
                item['total_linea_usd'] = item['cantidad'] * item['precio_unit_usd']
                self.actualizar_tabla_carrito()
                self.calcular_totales()
                return
        
        # Agregar nuevo item
        item = {
            'producto_id': producto['id'],
            'codigo': producto['codigo'],
            'nombre_producto': producto['nombre'],
            'cantidad': 1,
            'precio_unit_usd': producto['precio_usd'],
            'descuento': 0,
            'total_linea_usd': producto['precio_usd'],
            'stock_disponible': stock_actual  # Guardar para referencia
        }
        self.carrito.append(item)
        self.actualizar_tabla_carrito()
        self.calcular_totales()
    
    def actualizar_tabla_carrito(self):
        """Actualiza la tabla del carrito."""
        # Limpiar tabla
        for widget in self.frame_tabla_carrito.winfo_children():
            widget.destroy()
        
        # Headers
        headers = ["Código", "Producto", "Cant", "P.Unit $", "P.Unit Bs", "Total $", ""]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                self.frame_tabla_carrito,
                text=header,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=BG_HOVER,
                text_color=TEXT_SECONDARY,
                padx=5,
                pady=5
            ).grid(row=0, column=i, sticky="ew", padx=1, pady=1)
        
        # Productos
        for idx, item in enumerate(self.carrito, start=1):
            precio_bs = item['precio_unit_usd'] * self.tasa
            
            ctk.CTkLabel(
                self.frame_tabla_carrito, text=item['codigo'],
                padx=5, pady=3
            ).grid(row=idx, column=0, sticky="ew")
            
            ctk.CTkLabel(
                self.frame_tabla_carrito, text=item['nombre_producto'][:20],
                padx=5, pady=3
            ).grid(row=idx, column=1, sticky="ew")
            
            # Cantidad con botones +/-
            frame_cant = ctk.CTkFrame(self.frame_tabla_carrito, fg_color="transparent")
            frame_cant.grid(row=idx, column=2)
            
            ctk.CTkButton(
                frame_cant, text="-", width=25, height=25,
                command=lambda i=idx-1: self.modificar_cantidad(i, -1)
            ).pack(side="left", padx=1)
            
            ctk.CTkLabel(frame_cant, text=str(item['cantidad']), width=30).pack(side="left")
            
            ctk.CTkButton(
                frame_cant, text="+", width=25, height=25,
                command=lambda i=idx-1: self.modificar_cantidad(i, 1)
            ).pack(side="left", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla_carrito,
                text=formato_usd(item['precio_unit_usd']),
                text_color="#0ea5e9",
                padx=5, pady=3
            ).grid(row=idx, column=3, sticky="ew")
            
            ctk.CTkLabel(
                self.frame_tabla_carrito,
                text=formato_bs(precio_bs),
                text_color="#ffa500",
                padx=5, pady=3
            ).grid(row=idx, column=4, sticky="ew")
            
            ctk.CTkLabel(
                self.frame_tabla_carrito,
                text=formato_usd(item['total_linea_usd']),
                text_color="#0ea5e9",
                padx=5, pady=3
            ).grid(row=idx, column=5, sticky="ew")
            
            ctk.CTkButton(
                self.frame_tabla_carrito,
                text="🗑️", width=30, height=25,
                fg_color="#dc3545",
                command=lambda i=idx-1: self.eliminar_del_carrito(i)
            ).grid(row=idx, column=6)
    
    def modificar_cantidad(self, index: int, delta: int):
        """Modifica la cantidad de un producto en el carrito."""
        if 0 <= index < len(self.carrito):
            self.carrito[index]['cantidad'] += delta
            if self.carrito[index]['cantidad'] <= 0:
                self.eliminar_del_carrito(index)
            else:
                self.carrito[index]['total_linea_usd'] = (
                    self.carrito[index]['cantidad'] * self.carrito[index]['precio_unit_usd']
                )
                self.actualizar_tabla_carrito()
                self.calcular_totales()
    
    def eliminar_del_carrito(self, index: int):
        """Elimina un producto del carrito."""
        if 0 <= index < len(self.carrito):
            del self.carrito[index]
            self.actualizar_tabla_carrito()
            self.calcular_totales()
    
    def calcular_totales(self):
        """Calcula y muestra los totales."""
        subtotal_usd = sum(item['total_linea_usd'] for item in self.carrito)
        iva_usd = subtotal_usd * self.iva_porcentaje
        total_usd = subtotal_usd + iva_usd
        
        subtotal_bs = subtotal_usd * self.tasa
        iva_bs = iva_usd * self.tasa
        total_bs = total_usd * self.tasa
        
        self.lbl_subtotal_usd.configure(text=formato_usd(subtotal_usd))
        self.lbl_subtotal_bs.configure(text=formato_bs(subtotal_bs))
        self.lbl_iva_usd.configure(text=formato_usd(iva_usd))
        self.lbl_iva_bs.configure(text=formato_bs(iva_bs))
        self.lbl_total_usd.configure(text=formato_usd(total_usd))
        self.lbl_total_bs.configure(text=formato_bs(total_bs))
        
        # Guardar para uso posterior
        self.subtotal_usd = subtotal_usd
        self.iva_usd = iva_usd
        self.total_usd = total_usd
        self.total_bs = total_bs
    
    def calcular_vuelto(self, event=None):
        """Calcula el vuelto según la forma de pago."""
        try:
            monto_str = self.entry_monto_recibido.get().strip()
            if not monto_str:
                self.lbl_vuelto.configure(text="$ 0.00 / Bs 0.00", text_color="#00ff00")
                return
            
            monto = float(monto_str.replace(',', '.'))
            forma_pago = self.cmb_forma_pago.get()
            
            # Pagos electrónicos: el monto está en Bs
            if forma_pago in ["Pago Móvil", "Punto de Venta"]:
                total_bs = getattr(self, 'total_bs', 0)
                vuelto_bs = monto - total_bs
                vuelto_usd = vuelto_bs / self.tasa if self.tasa > 0 else 0
            else:
                # Efectivo: el monto puede estar en USD
                vuelto_usd = monto - getattr(self, 'total_usd', 0)
                vuelto_bs = vuelto_usd * self.tasa
            
            if vuelto_usd < 0:
                self.lbl_vuelto.configure(
                    text=f"Falta: {formato_usd(abs(vuelto_usd))} / {formato_bs(abs(vuelto_bs))}",
                    text_color="#ff4444"
                )
            else:
                self.lbl_vuelto.configure(
                    text=f"{formato_usd(vuelto_usd)} / {formato_bs(vuelto_bs)}",
                    text_color="#00ff00"
                )
        except:
            self.lbl_vuelto.configure(text="$ 0.00 / Bs 0.00", text_color="#00ff00")
    
    def limpiar_carrito(self):
        """Limpia el carrito."""
        self.carrito = []
        self.actualizar_tabla_carrito()
        self.calcular_totales()
        self.entry_monto_recibido.delete(0, 'end')
        self.entry_referencia.delete(0, 'end')
        self.lbl_vuelto.configure(text="$ 0.00 / Bs 0.00", text_color="#00ff00")
    
    def procesar_venta(self):
        """Procesa y registra la venta."""
        if not self.carrito:
            CTkMessagebox(title="Error", message="El carrito está vacío", icon="warning")
            return
        
        forma_pago = self.cmb_forma_pago.get()
        referencia = self.entry_referencia.get().strip() if forma_pago != "Efectivo" else None
        
        monto_str = self.entry_monto_recibido.get().strip()
        try:
            monto_recibido = float(monto_str.replace(',', '.')) if monto_str else self.total_usd
        except:
            monto_recibido = self.total_usd
        
        vuelto = max(0, monto_recibido - self.total_usd)
        
        # Confirmar venta
        msg = CTkMessagebox(
            title="Confirmar Venta",
            message=f"Total: {formato_usd(self.total_usd)} / {formato_bs(self.total_bs)}\n\n¿Procesar venta?",
            icon="question",
            option_1="Cancelar",
            option_2="Confirmar"
        )
        
        if msg.get() != "Confirmar":
            return
        
        try:
            venta_id = crear_venta(
                subtotal_usd=self.subtotal_usd,
                iva_usd=self.iva_usd,
                total_usd=self.total_usd,
                tasa_cambio=self.tasa,
                total_bs=self.total_bs,
                forma_pago=forma_pago,
                detalles=self.carrito,
                cliente_id=self.cliente_seleccionado_id,
                referencia_pago=referencia,
                monto_recibido=monto_recibido,
                vuelto=vuelto
            )
            
            CTkMessagebox(
                title="Venta Exitosa",
                message=f"Venta registrada correctamente\n\nVuelto: {formato_usd(vuelto)} / {formato_bs(vuelto * self.tasa)}",
                icon="check"
            )
            
            self.limpiar_carrito()
            
        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Error al procesar la venta: {str(e)}",
                icon="cancel"
            )
