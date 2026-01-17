"""
Ventana Principal del Sistema de Ventas - Diseño Minimalista
"""
import customtkinter as ctk
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_configuracion
from utils.currency import set_tasa_global
from utils.theme import (
    BG_PRINCIPAL, BG_SECUNDARIO, BG_SIDEBAR, BG_HOVER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_PRIMARY, BORDER_COLOR
)


class MainWindow(ctk.CTk):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Sistema de Ventas e Inventario")
        self.geometry("1200x720")
        self.minsize(1000, 600)
        
        # Configurar tema oscuro
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=BG_PRINCIPAL)
        
        # Cargar configuración inicial
        self.cargar_configuracion()
        
        # Cache de vistas para evitar parpadeo
        self.vistas_cache = {}
        self.vista_actual = None
        self.vista_nombre_actual = None
        self.botones_menu = {}
        
        # Configurar layout principal
        self.setup_layout()
        
        # Mostrar dashboard por defecto
        self.mostrar_vista("dashboard")
    
    def cargar_configuracion(self):
        """Carga la configuración del sistema."""
        config = get_configuracion()
        self.nombre_tienda = config.get('nombre_tienda', 'Mi Tienda')
        self.tasa_actual = config.get('tasa_cambio', 1.0)
        set_tasa_global(self.tasa_actual)
    
    def setup_layout(self):
        """Configura el layout principal de la ventana."""
        # Configurar grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        self.header = ctk.CTkFrame(
            self, 
            height=50, 
            corner_radius=0,
            fg_color=BG_SIDEBAR
        )
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header.grid_propagate(False)
        self.setup_header()
        
        # === SIDEBAR (Menú lateral) ===
        self.sidebar = ctk.CTkScrollableFrame(
            self, 
            width=160, 
            corner_radius=0,
            fg_color=BG_SIDEBAR
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.setup_sidebar()
        
        # === CONTENIDO PRINCIPAL ===
        self.main_content = ctk.CTkFrame(self, fg_color=BG_PRINCIPAL)
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
    
    def setup_header(self):
        """Configura el header de la aplicación."""
        self.header.grid_columnconfigure(1, weight=1)
        
        # Logo / Nombre de la tienda
        self.lbl_titulo = ctk.CTkLabel(
            self.header,
            text=f"🏪 {self.nombre_tienda}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.lbl_titulo.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Tasa de cambio en el header
        self.lbl_tasa_header = ctk.CTkLabel(
            self.header,
            text=f"💱 Tasa: Bs {self.tasa_actual:,.2f}",
            font=ctk.CTkFont(size=14),
            text_color=ACCENT_PRIMARY
        )
        self.lbl_tasa_header.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        # Fecha y hora
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        self.lbl_fecha = ctk.CTkLabel(
            self.header,
            text=f"📅 {fecha_actual}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY
        )
        self.lbl_fecha.grid(row=0, column=2, padx=20, pady=15, sticky="e")
    
    def setup_sidebar(self):
        """Configura el menú lateral."""
        # Título del menú
        lbl_menu = ctk.CTkLabel(
            self.sidebar,
            text="MENÚ PRINCIPAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED
        )
        lbl_menu.pack(pady=(20, 15), padx=15, anchor="w")
        
        # Botones del menú
        menu_items = [
            ("🏠 Dashboard", "dashboard"),
            ("🛒 Punto de Venta", "pos"),
            ("📥 Compras", "compras"),
            ("📦 Productos", "productos"),
            ("🏷️ Categorías", "categorias"),
            ("📊 Inventario", "inventario"),
            ("👥 Clientes", "clientes"),
            ("📈 Reportes", "reportes"),
        ]
        
        for texto, vista in menu_items:
            # Frame contenedor para el borde izquierdo
            frame_btn = ctk.CTkFrame(
                self.sidebar,
                fg_color="transparent",
                corner_radius=0
            )
            frame_btn.pack(fill="x", pady=1)
            
            btn = ctk.CTkButton(
                frame_btn,
                text=texto,
                anchor="w",
                fg_color="transparent",
                text_color=TEXT_SECONDARY,
                hover_color=BG_HOVER,
                height=40,
                font=ctk.CTkFont(size=13),
                corner_radius=0,
                command=lambda v=vista: self.mostrar_vista(v)
            )
            btn.pack(fill="x", padx=(0, 0), pady=0)
            
            self.botones_menu[vista] = (frame_btn, btn)
        
        # Separador
        ctk.CTkFrame(
            self.sidebar, 
            height=1, 
            fg_color=BORDER_COLOR
        ).pack(fill="x", pady=20, padx=15)
        
        # Configuración al final
        frame_config = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            corner_radius=0
        )
        frame_config.pack(fill="x", pady=1)
        
        btn_config = ctk.CTkButton(
            frame_config,
            text="⚙️ Configuración",
            anchor="w",
            fg_color="transparent",
            text_color=TEXT_SECONDARY,
            hover_color=BG_HOVER,
            height=40,
            font=ctk.CTkFont(size=13),
            corner_radius=0,
            command=lambda: self.mostrar_vista("configuracion")
        )
        btn_config.pack(fill="x")
        
        self.botones_menu["configuracion"] = (frame_config, btn_config)
    
    def actualizar_menu_activo(self, vista_activa: str):
        """Actualiza el estilo del botón activo en el menú."""
        for vista, (frame, btn) in self.botones_menu.items():
            if vista == vista_activa:
                # Estilo activo - borde izquierdo verde
                frame.configure(fg_color="transparent")
                btn.configure(
                    text_color=ACCENT_PRIMARY,
                    fg_color=BG_HOVER
                )
                # Agregar indicador de borde izquierdo
                for child in frame.winfo_children():
                    if isinstance(child, ctk.CTkFrame) and child != btn:
                        child.destroy()
                
                borde = ctk.CTkFrame(
                    frame,
                    width=3,
                    fg_color=ACCENT_PRIMARY,
                    corner_radius=0
                )
                borde.place(x=0, y=0, relheight=1)
            else:
                # Estilo inactivo
                btn.configure(
                    text_color=TEXT_SECONDARY,
                    fg_color="transparent"
                )
                for child in frame.winfo_children():
                    if isinstance(child, ctk.CTkFrame) and child != btn:
                        child.destroy()
    
    def mostrar_vista(self, nombre_vista: str):
        """Muestra la vista especificada en el área de contenido usando cache."""
        # Si es la misma vista, solo refrescar datos
        if nombre_vista == self.vista_nombre_actual and nombre_vista in self.vistas_cache:
            vista = self.vistas_cache[nombre_vista]
            if hasattr(vista, 'refrescar'):
                vista.refrescar()
            return
        
        # Actualizar menú activo
        self.vista_nombre_actual = nombre_vista
        self.actualizar_menu_activo(nombre_vista)
        
        # Verificar si la vista ya está en cache
        if nombre_vista in self.vistas_cache:
            # Usar vista cacheada
            vista = self.vistas_cache[nombre_vista]
            # Refrescar datos si la vista tiene ese método
            if hasattr(vista, 'refrescar'):
                vista.refrescar()
        else:
            # Crear la vista y cachearla
            if nombre_vista == "dashboard":
                from views.dashboard import DashboardView
                vista = DashboardView(self.main_content, self)
            
            elif nombre_vista == "pos":
                from views.pos_view import POSView
                vista = POSView(self.main_content, self)
            
            elif nombre_vista == "productos":
                from views.productos_view import ProductosView
                vista = ProductosView(self.main_content, self)
            
            elif nombre_vista == "inventario":
                from views.inventario_view import InventarioView
                vista = InventarioView(self.main_content, self)
            
            elif nombre_vista == "categorias":
                from views.categorias_view import CategoriasView
                vista = CategoriasView(self.main_content, self)
            
            elif nombre_vista == "clientes":
                from views.clientes_view import ClientesView
                vista = ClientesView(self.main_content, self)
            
            elif nombre_vista == "compras":
                from views.compras_view import ComprasView
                vista = ComprasView(self.main_content, self)
            
            elif nombre_vista == "reportes":
                from views.reportes_view import ReportesView
                vista = ReportesView(self.main_content, self)
            
            elif nombre_vista == "configuracion":
                from views.config_view import ConfigView
                vista = ConfigView(self.main_content, self)
            
            else:
                vista = ctk.CTkLabel(
                    self.main_content,
                    text=f"Vista '{nombre_vista}' no encontrada",
                    font=ctk.CTkFont(size=18)
                )
            
            # Colocar la vista en el grid
            vista.grid(row=0, column=0, sticky="nsew")
            
            # Guardar en cache
            self.vistas_cache[nombre_vista] = vista
        
        # Traer la vista al frente usando tkraise
        self.vista_actual = vista
        vista.tkraise()
    
    def limpiar_cache_vista(self, nombre_vista: str = None):
        """Limpia el cache de una vista específica o todas."""
        if nombre_vista:
            if nombre_vista in self.vistas_cache:
                self.vistas_cache[nombre_vista].destroy()
                del self.vistas_cache[nombre_vista]
        else:
            for vista in self.vistas_cache.values():
                vista.destroy()
            self.vistas_cache.clear()
    
    def actualizar_tasa_header(self, nueva_tasa: float):
        """Actualiza la tasa mostrada en el header."""
        self.tasa_actual = nueva_tasa
        self.lbl_tasa_header.configure(text=f"💱 Tasa: Bs {nueva_tasa:,.2f}")
