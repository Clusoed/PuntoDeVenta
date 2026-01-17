"""
Dashboard - Panel principal del sistema - Diseño Minimalista
"""
import customtkinter as ctk
from datetime import datetime
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_ventas_del_dia, get_ventas_del_mes, get_productos_bajo_stock, get_configuracion, update_tasa_cambio
from utils.currency import formato_usd, formato_bs, set_tasa_global
from utils.theme import (
    BG_PRINCIPAL, BG_SECUNDARIO, BG_HOVER, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_PRIMARY, ACCENT_HOVER, WARNING, BTN_OUTLINED_STYLE
)


class DashboardView(ctk.CTkFrame):
    """Vista del Dashboard principal."""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=BG_PRINCIPAL)
        self.app = app_controller
        self.setup_ui()
        self.actualizar_datos()
    
    def setup_ui(self):
        """Configura la interfaz del dashboard."""
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # === FILA 1: Tasa de cambio ===
        self.frame_tasa = ctk.CTkFrame(
            self, 
            fg_color=BG_SECUNDARIO,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=10
        )
        self.frame_tasa.grid(row=0, column=0, columnspan=3, padx=15, pady=15, sticky="ew")
        self.setup_tasa_frame()
        
        # === FILA 2: Tarjetas de resumen ===
        # Tarjeta: Ventas del día
        self.card_ventas_dia = self.crear_tarjeta(
            row=1, column=0, 
            titulo="📊 VENTAS HOY"
        )
        
        # Tarjeta: Ventas del mes
        self.card_ventas_mes = self.crear_tarjeta(
            row=1, column=1,
            titulo="📈 VENTAS MES"
        )
        
        # Tarjeta: Stock bajo
        self.card_stock_bajo = self.crear_tarjeta(
            row=1, column=2,
            titulo="⚠️ STOCK BAJO",
            es_alerta=True
        )
        
        # === FILA 3: Accesos rápidos ===
        self.frame_accesos = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.frame_accesos.grid(row=2, column=0, columnspan=3, padx=15, pady=20, sticky="ew")
        self.setup_accesos_rapidos()
        
        # === FILA 4: Footer del desarrollador ===
        self.frame_footer = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_footer.grid(row=3, column=0, columnspan=3, padx=15, pady=(20, 10), sticky="sew")
        self.grid_rowconfigure(3, weight=1)
        
        ctk.CTkLabel(
            self.frame_footer,
            text="Desarrollado por Gutidev  |  📞 +58 412-7416894  | 📱 @gutidev_st",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(side="bottom", pady=10)
    
    def setup_tasa_frame(self):
        """Configura el frame de la tasa de cambio."""
        self.frame_tasa.grid_columnconfigure(1, weight=1)
        
        # Título
        ctk.CTkLabel(
            self.frame_tasa,
            text="💱 TASA DE CAMBIO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_SECONDARY
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Tasa actual
        self.lbl_tasa_actual = ctk.CTkLabel(
            self.frame_tasa,
            text="1 USD = Bs 0.00",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=ACCENT_PRIMARY
        )
        self.lbl_tasa_actual.grid(row=0, column=1, padx=20, pady=15)
        
        # Fecha de actualización
        self.lbl_fecha_tasa = ctk.CTkLabel(
            self.frame_tasa,
            text="Última actualización: --",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED
        )
        self.lbl_fecha_tasa.grid(row=1, column=1, padx=20, pady=(0, 10))
        
        # Frame para actualizar tasa
        frame_nueva_tasa = ctk.CTkFrame(self.frame_tasa, fg_color="transparent")
        frame_nueva_tasa.grid(row=0, column=2, rowspan=2, padx=20, pady=15, sticky="e")
        
        ctk.CTkLabel(
            frame_nueva_tasa,
            text="Nueva tasa:",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY
        ).pack(side="left", padx=5)
        
        self.entry_nueva_tasa = ctk.CTkEntry(
            frame_nueva_tasa,
            width=100,
            placeholder_text="0.00",
            fg_color=BG_PRINCIPAL,
            border_color=BORDER_COLOR,
            border_width=1
        )
        self.entry_nueva_tasa.pack(side="left", padx=5)
        
        self.btn_actualizar_tasa = ctk.CTkButton(
            frame_nueva_tasa,
            text="✓ Actualizar",
            width=100,
            fg_color="transparent",
            hover_color=BG_HOVER,
            text_color=ACCENT_PRIMARY,
            border_color=ACCENT_PRIMARY,
            border_width=1,
            command=self.actualizar_tasa
        )
        self.btn_actualizar_tasa.pack(side="left", padx=5)
    
    def crear_tarjeta(self, row: int, column: int, titulo: str, es_alerta: bool = False) -> dict:
        """Crea una tarjeta de resumen con diseño minimalista."""
        frame = ctk.CTkFrame(
            self, 
            fg_color=BG_SECUNDARIO, 
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=10
        )
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        
        # Título
        lbl_titulo = ctk.CTkLabel(
            frame,
            text=titulo,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        lbl_titulo.pack(pady=(20, 10))
        
        # Valor principal
        color_valor = WARNING if es_alerta else ACCENT_PRIMARY
        lbl_usd = ctk.CTkLabel(
            frame,
            text="$ 0.00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color_valor
        )
        lbl_usd.pack(pady=5)
        
        # Valor secundario
        lbl_bs = ctk.CTkLabel(
            frame,
            text="Bs 0.00",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_SECONDARY
        )
        lbl_bs.pack(pady=5)
        
        # Info adicional
        lbl_info = ctk.CTkLabel(
            frame,
            text="0 transacciones",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED
        )
        lbl_info.pack(pady=(5, 20))
        
        return {
            'frame': frame,
            'lbl_usd': lbl_usd,
            'lbl_bs': lbl_bs,
            'lbl_info': lbl_info
        }
    
    def setup_accesos_rapidos(self):
        """Configura los botones de acceso rápido."""
        frame_botones = ctk.CTkFrame(self.frame_accesos, fg_color="transparent")
        frame_botones.pack(expand=True)
        
        botones = [
            ("🛒 Nueva Venta", "pos"),
            ("📦 Productos", "productos"),
            ("📊 Inventario", "inventario"),
            ("📈 Reportes", "reportes"),
            ("⚙️ Configuración", "configuracion")
        ]
        
        for texto, vista in botones:
            btn = ctk.CTkButton(
                frame_botones,
                text=texto,
                width=140,
                height=45,
                fg_color="transparent",
                hover_color=BG_HOVER,
                text_color=ACCENT_PRIMARY,
                border_color=ACCENT_PRIMARY,
                border_width=1,
                corner_radius=8,
                font=ctk.CTkFont(size=13),
                command=lambda v=vista: self.app.mostrar_vista(v)
            )
            btn.pack(side="left", padx=8)
    
    def actualizar_datos(self):
        """Actualiza todos los datos del dashboard."""
        # Cargar configuración
        config = get_configuracion()
        tasa = config.get('tasa_cambio', 1.0)
        fecha_tasa = config.get('fecha_tasa', '')
        
        # Actualizar tasa global
        set_tasa_global(tasa)
        
        # Mostrar tasa actual
        self.lbl_tasa_actual.configure(text=f"1 USD = Bs {tasa:,.2f}")
        
        if fecha_tasa:
            try:
                fecha_formateada = datetime.fromisoformat(fecha_tasa).strftime('%d/%m/%Y %H:%M')
                self.lbl_fecha_tasa.configure(text=f"Última actualización: {fecha_formateada}")
            except:
                self.lbl_fecha_tasa.configure(text=f"Última actualización: {fecha_tasa}")
        
        # Obtener ventas del día
        ventas_dia = get_ventas_del_dia()
        total_usd = ventas_dia.get('total_usd', 0)
        total_bs = ventas_dia.get('total_bs', 0)
        cantidad = ventas_dia.get('cantidad', 0)
        
        self.card_ventas_dia['lbl_usd'].configure(text=formato_usd(total_usd))
        self.card_ventas_dia['lbl_bs'].configure(text=formato_bs(total_bs))
        self.card_ventas_dia['lbl_info'].configure(text=f"{cantidad} transacciones")
        
        # Ventas del mes
        ventas_mes = get_ventas_del_mes()
        total_usd_mes = ventas_mes.get('total_usd', 0)
        total_bs_mes = ventas_mes.get('total_bs', 0)
        cantidad_mes = ventas_mes.get('cantidad', 0)
        
        self.card_ventas_mes['lbl_usd'].configure(text=formato_usd(total_usd_mes))
        self.card_ventas_mes['lbl_bs'].configure(text=formato_bs(total_bs_mes))
        self.card_ventas_mes['lbl_info'].configure(text=f"{cantidad_mes} transacciones")
        
        # Productos con stock bajo
        productos_bajo = get_productos_bajo_stock()
        cantidad_bajo = len(productos_bajo)
        self.card_stock_bajo['lbl_usd'].configure(text=f"{cantidad_bajo}")
        self.card_stock_bajo['lbl_bs'].configure(text="productos")
        self.card_stock_bajo['lbl_info'].configure(text="requieren reposición")
    
    def actualizar_tasa(self):
        """Actualiza la tasa de cambio."""
        try:
            nueva_tasa_str = self.entry_nueva_tasa.get().strip()
            if not nueva_tasa_str:
                return
            
            nueva_tasa = float(nueva_tasa_str.replace(',', '.'))
            if nueva_tasa <= 0:
                raise ValueError("La tasa debe ser mayor a 0")
            
            if update_tasa_cambio(nueva_tasa):
                set_tasa_global(nueva_tasa)
                self.entry_nueva_tasa.delete(0, 'end')
                self.actualizar_datos()
                
                # Actualizar header principal
                if hasattr(self.app, 'actualizar_tasa_header'):
                    self.app.actualizar_tasa_header(nueva_tasa)
                
                # Mostrar mensaje de éxito
                from CTkMessagebox import CTkMessagebox
                CTkMessagebox(
                    title="Tasa Actualizada",
                    message=f"La tasa de cambio se actualizó a Bs {nueva_tasa:,.2f}",
                    icon="check"
                )
        except ValueError as e:
            from CTkMessagebox import CTkMessagebox
            CTkMessagebox(
                title="Error",
                message="Por favor ingrese un valor numérico válido",
                icon="cancel"
            )
