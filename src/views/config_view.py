"""
Vista de Configuración del Sistema - Diseño Minimalista
"""
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_configuracion, update_tasa_cambio, get_historial_tasas, get_connection,
                      guardar_password_admin, verificar_password_admin, existe_password_admin,
                      limpiar_base_datos)
from utils.currency import set_tasa_global
from utils.theme import BG_PRINCIPAL, BG_SECUNDARIO, BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY, BG_HOVER, ACCENT_HOVER, ERROR


class ConfigView(ctk.CTkFrame):
    """Vista de configuración del sistema."""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=BG_PRINCIPAL)
        self.app = app_controller
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configura la interfaz de configuración."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame scrolleable principal
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=1)
        
        # Título
        ctk.CTkLabel(
            scroll_frame,
            text="⚙️ CONFIGURACIÓN DEL SISTEMA",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=10, sticky="w", padx=15)
        
        # === COLUMNA 1: Datos de la tienda ===
        frame_tienda = ctk.CTkFrame(scroll_frame, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_tienda.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.setup_datos_tienda(frame_tienda)
        
        # === COLUMNA 2: Tasa de cambio ===
        frame_tasa = ctk.CTkFrame(scroll_frame, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_tasa.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.setup_tasa_cambio(frame_tasa)
        
        # === FILA 2: Seguridad ===
        frame_seguridad = ctk.CTkFrame(scroll_frame, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_seguridad.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.setup_seguridad(frame_seguridad)
    
    def setup_seguridad(self, frame):
        """Configura la sección de seguridad."""
        ctk.CTkLabel(
            frame,
            text="🔒 Seguridad y Mantenimiento",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15, padx=20, anchor="w")
        
        # Frame para contraseña y limpieza
        frame_content = ctk.CTkFrame(frame, fg_color="transparent")
        frame_content.pack(fill="x", padx=20, pady=10)
        
        # --- Contraseña de Administrador ---
        frame_password = ctk.CTkFrame(frame_content)
        frame_password.pack(side="left", padx=10, pady=5, fill="y")
        
        ctk.CTkLabel(
            frame_password,
            text="🔑 Contraseña de Administrador",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10, padx=15, anchor="w")
        
        # Estado de contraseña
        tiene_password = existe_password_admin()
        estado = "✅ Contraseña configurada" if tiene_password else "⚠️ Sin contraseña"
        self.lbl_estado_password = ctk.CTkLabel(
            frame_password,
            text=estado,
            text_color="#0ea5e9" if tiene_password else "orange"
        )
        self.lbl_estado_password.pack(pady=5, padx=15, anchor="w")
        
        ctk.CTkLabel(frame_password, text="Nueva contraseña:").pack(pady=(10, 0), padx=15, anchor="w")
        self.entry_password = ctk.CTkEntry(frame_password, width=200, show="*")
        self.entry_password.pack(pady=5, padx=15)
        
        ctk.CTkLabel(frame_password, text="Confirmar:").pack(pady=(5, 0), padx=15, anchor="w")
        self.entry_password_confirm = ctk.CTkEntry(frame_password, width=200, show="*")
        self.entry_password_confirm.pack(pady=5, padx=15)
        
        ctk.CTkButton(
            frame_password,
            text="💾 Guardar Contraseña",
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self.guardar_password
        ).pack(pady=15, padx=15)
        
        # --- Limpiar Base de Datos ---
        frame_limpiar = ctk.CTkFrame(frame_content)
        frame_limpiar.pack(side="left", padx=30, pady=5, fill="y")
        
        ctk.CTkLabel(
            frame_limpiar,
            text="🗑️ Limpiar Base de Datos",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10, padx=15, anchor="w")
        
        ctk.CTkLabel(
            frame_limpiar,
            text="⚠️ Esto eliminará TODAS las ventas, compras\ny movimientos. Los productos se mantienen.",
            text_color="orange",
            justify="left"
        ).pack(pady=10, padx=15, anchor="w")
        
        ctk.CTkLabel(frame_limpiar, text="Contraseña de admin:").pack(pady=(10, 0), padx=15, anchor="w")
        self.entry_password_limpiar = ctk.CTkEntry(frame_limpiar, width=200, show="*")
        self.entry_password_limpiar.pack(pady=5, padx=15)
        
        ctk.CTkButton(
            frame_limpiar,
            text="🗑️ LIMPIAR TODO",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="#ffffff",
            command=self.limpiar_bd
        ).pack(pady=15, padx=15)
    
    def guardar_password(self):
        """Guarda la contraseña de administrador."""
        password = self.entry_password.get()
        confirm = self.entry_password_confirm.get()
        
        if not password:
            CTkMessagebox(title="Error", message="Ingrese una contraseña", icon="warning")
            return
        
        if password != confirm:
            CTkMessagebox(title="Error", message="Las contraseñas no coinciden", icon="cancel")
            return
        
        if len(password) < 4:
            CTkMessagebox(title="Error", message="La contraseña debe tener al menos 4 caracteres", icon="warning")
            return
        
        guardar_password_admin(password)
        self.entry_password.delete(0, 'end')
        self.entry_password_confirm.delete(0, 'end')
        
        self.lbl_estado_password.configure(text="✅ Contraseña configurada", text_color="#0ea5e9")
        
        CTkMessagebox(
            title="✅ Contraseña Guardada",
            message="La contraseña de administrador se guardó correctamente.",
            icon="check"
        )
    
    def limpiar_bd(self):
        """Limpia la base de datos después de verificar contraseña."""
        password = self.entry_password_limpiar.get()
        
        if not existe_password_admin():
            CTkMessagebox(
                title="Error",
                message="Primero debe configurar una contraseña de administrador.",
                icon="warning"
            )
            return
        
        if not password:
            CTkMessagebox(title="Error", message="Ingrese la contraseña de administrador", icon="warning")
            return
        
        if not verificar_password_admin(password):
            CTkMessagebox(
                title="Error",
                message="Contraseña incorrecta",
                icon="cancel"
            )
            return
        
        # Confirmación final
        msg = CTkMessagebox(
            title="⚠️ CONFIRMAR LIMPIEZA",
            message="¿Está SEGURO de que desea eliminar\nTODAS las ventas, compras y movimientos?\n\nEsta acción NO se puede deshacer.",
            icon="warning",
            option_1="Cancelar",
            option_2="Sí, Limpiar Todo"
        )
        
        if msg.get() == "Sí, Limpiar Todo":
            if limpiar_base_datos():
                self.entry_password_limpiar.delete(0, 'end')
                CTkMessagebox(
                    title="✅ Base de Datos Limpia",
                    message="Se eliminaron todas las ventas, compras y movimientos.\nEl stock de todos los productos se puso en 0.",
                    icon="check"
                )
            else:
                CTkMessagebox(
                    title="Error",
                    message="Ocurrió un error al limpiar la base de datos.",
                    icon="cancel"
                )
    
    def setup_datos_tienda(self, frame):
        """Configura el formulario de datos de la tienda."""
        ctk.CTkLabel(
            frame,
            text="🏪 Datos de la Tienda",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15, padx=20, anchor="w")
        
        # Nombre de la tienda
        ctk.CTkLabel(frame, text="Nombre de la tienda:").pack(pady=(10, 0), padx=20, anchor="w")
        self.entry_nombre = ctk.CTkEntry(frame, width=300)
        self.entry_nombre.pack(pady=5, padx=20, anchor="w")
        
        # RIF
        ctk.CTkLabel(frame, text="RIF:").pack(pady=(10, 0), padx=20, anchor="w")
        self.entry_rif = ctk.CTkEntry(frame, width=300, placeholder_text="J-12345678-9")
        self.entry_rif.pack(pady=5, padx=20, anchor="w")
        
        # Dirección
        ctk.CTkLabel(frame, text="Dirección:").pack(pady=(10, 0), padx=20, anchor="w")
        self.entry_direccion = ctk.CTkEntry(frame, width=300)
        self.entry_direccion.pack(pady=5, padx=20, anchor="w")
        
        # Teléfono
        ctk.CTkLabel(frame, text="Teléfono:").pack(pady=(10, 0), padx=20, anchor="w")
        self.entry_telefono = ctk.CTkEntry(frame, width=300, placeholder_text="0414-1234567")
        self.entry_telefono.pack(pady=5, padx=20, anchor="w")
        
        # IVA
        ctk.CTkLabel(frame, text="IVA (%):").pack(pady=(10, 0), padx=20, anchor="w")
        self.entry_iva = ctk.CTkEntry(frame, width=100)
        self.entry_iva.pack(pady=5, padx=20, anchor="w")
        
        # Botón guardar
        ctk.CTkButton(
            frame,
            text="💾 Guardar Cambios",
            command=self.guardar_datos_tienda
        ).pack(pady=10, padx=15)
    
    def setup_tasa_cambio(self, frame):
        """Configura la sección de tasa de cambio."""
        ctk.CTkLabel(
            frame,
            text="💱 Tasa de Cambio",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15, padx=20, anchor="w")
        
        # Tasa actual (grande y destacada)
        self.lbl_tasa_actual = ctk.CTkLabel(
            frame,
            text="1 USD = Bs 0.00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#0ea5e9"
        )
        self.lbl_tasa_actual.pack(pady=10)
        
        # Fecha de última actualización
        self.lbl_fecha_tasa = ctk.CTkLabel(
            frame,
            text="Última actualización: --",
            text_color="gray"
        )
        self.lbl_fecha_tasa.pack(pady=5)
        
        # Nueva tasa
        frame_nueva = ctk.CTkFrame(frame, fg_color="transparent")
        frame_nueva.pack(pady=10)
        
        ctk.CTkLabel(frame_nueva, text="Nueva tasa:").pack(side="left", padx=5)
        self.entry_nueva_tasa = ctk.CTkEntry(frame_nueva, width=120, placeholder_text="0.00")
        self.entry_nueva_tasa.pack(side="left", padx=5)
        ctk.CTkButton(
            frame_nueva,
            text="✓ Actualizar",
            width=100,
            command=self.actualizar_tasa
        ).pack(side="left", padx=5)
        
        # Historial de tasas
        ctk.CTkLabel(
            frame,
            text="📊 Historial de Tasas",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        # Tabla de historial
        self.frame_historial = ctk.CTkScrollableFrame(frame, height=200)
        self.frame_historial.pack(fill="x", padx=20, pady=10)
    
    def cargar_datos(self):
        """Carga los datos actuales de configuración."""
        config = get_configuracion()
        
        # Datos de la tienda
        self.entry_nombre.delete(0, 'end')
        self.entry_nombre.insert(0, config.get('nombre_tienda', ''))
        
        self.entry_rif.delete(0, 'end')
        self.entry_rif.insert(0, config.get('rif', '') or '')
        
        self.entry_direccion.delete(0, 'end')
        self.entry_direccion.insert(0, config.get('direccion', '') or '')
        
        self.entry_telefono.delete(0, 'end')
        self.entry_telefono.insert(0, config.get('telefono', '') or '')
        
        self.entry_iva.delete(0, 'end')
        self.entry_iva.insert(0, str(config.get('iva_porcentaje', 16)))
        
        # Tasa de cambio
        tasa = config.get('tasa_cambio', 1.0)
        self.lbl_tasa_actual.configure(text=f"1 USD = Bs {tasa:,.2f}")
        
        fecha_tasa = config.get('fecha_tasa', '')
        if fecha_tasa:
            from datetime import datetime
            try:
                fecha_formateada = datetime.fromisoformat(fecha_tasa).strftime('%d/%m/%Y %H:%M')
                self.lbl_fecha_tasa.configure(text=f"Última actualización: {fecha_formateada}")
            except:
                self.lbl_fecha_tasa.configure(text=f"Última actualización: {fecha_tasa}")
        
        # Cargar historial
        self.cargar_historial()
    
    def cargar_historial(self):
        """Carga el historial de tasas de cambio."""
        # Limpiar historial anterior
        for widget in self.frame_historial.winfo_children():
            widget.destroy()
        
        # Headers
        frame_header = ctk.CTkFrame(self.frame_historial, fg_color="gray30")
        frame_header.pack(fill="x", pady=2)
        ctk.CTkLabel(frame_header, text="Fecha", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(frame_header, text="Tasa", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Datos
        historial = get_historial_tasas(10)
        for item in historial:
            frame_row = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
            frame_row.pack(fill="x", pady=1)
            
            fecha = item.get('fecha', '')
            if fecha:
                from datetime import datetime
                try:
                    fecha = datetime.fromisoformat(fecha).strftime('%d/%m/%Y %H:%M')
                except:
                    pass
            
            tasa = item.get('tasa', 0)
            
            ctk.CTkLabel(frame_row, text=fecha, width=150).pack(side="left", padx=5)
            ctk.CTkLabel(frame_row, text=f"Bs {tasa:,.2f}", width=100).pack(side="left", padx=5)
    
    def guardar_datos_tienda(self):
        """Guarda los datos de la tienda."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            nombre = self.entry_nombre.get().strip()
            rif = self.entry_rif.get().strip()
            direccion = self.entry_direccion.get().strip()
            telefono = self.entry_telefono.get().strip()
            iva = float(self.entry_iva.get().strip() or 16)
            
            cursor.execute('''
                UPDATE configuracion 
                SET nombre_tienda = ?, rif = ?, direccion = ?, telefono = ?, iva_porcentaje = ?
                WHERE id = 1
            ''', (nombre, rif, direccion, telefono, iva))
            
            conn.commit()
            conn.close()
            
            # Actualizar título de la ventana
            self.app.lbl_titulo.configure(text=f"🏪 {nombre}")
            
            CTkMessagebox(
                title="Guardado",
                message="Los datos se guardaron correctamente",
                icon="check"
            )
        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Error al guardar: {str(e)}",
                icon="cancel"
            )
    
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
                self.cargar_datos()
                
                # Actualizar tasa en el header
                self.app.actualizar_tasa_header(nueva_tasa)
                
                CTkMessagebox(
                    title="Tasa Actualizada",
                    message=f"La tasa de cambio se actualizó a Bs {nueva_tasa:,.2f}",
                    icon="check"
                )
        except ValueError as e:
            CTkMessagebox(
                title="Error",
                message="Por favor ingrese un valor numérico válido",
                icon="cancel"
            )
