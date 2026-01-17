"""
Vista de Gestión de Categorías - Diseño Minimalista
"""
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    get_categorias, crear_categoria, actualizar_categoria, eliminar_categoria
)
from utils.theme import BG_PRINCIPAL, BG_SECUNDARIO, BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY, BG_HOVER


class CategoriasView(ctk.CTkFrame):
    """Vista para gestionar categorías de productos."""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=BG_PRINCIPAL)
        self.app = app_controller
        self.categorias = []
        
        self.setup_ui()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configura la interfaz de categorías."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            frame_header,
            text="🏷️ GESTIÓN DE CATEGORÍAS",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            frame_header,
            text="➕ Nueva Categoría",
            font=ctk.CTkFont(size=14),
            fg_color=ACCENT_PRIMARY,
            hover_color="#0284c7",
            command=self.abrir_formulario_nuevo
        ).pack(side="right", padx=10)
        
        # === CONTENIDO ===
        frame_contenido = ctk.CTkFrame(self, fg_color=BG_SECUNDARIO, border_color=BORDER_COLOR, border_width=1)
        frame_contenido.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame_contenido.grid_columnconfigure(0, weight=1)
        frame_contenido.grid_rowconfigure(0, weight=1)
        
        # Tabla de categorías
        self.frame_tabla = ctk.CTkScrollableFrame(frame_contenido)
        self.frame_tabla.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        for i in range(4):
            self.frame_tabla.grid_columnconfigure(i, weight=1)
    
    def cargar_datos(self):
        """Carga las categorías desde la base de datos."""
        self.categorias = get_categorias()
        self.mostrar_categorias()
    
    def mostrar_categorias(self):
        """Muestra las categorías en la tabla."""
        # Limpiar tabla
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        
        # Headers
        headers = ["ID", "Nombre", "Descripción", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                self.frame_tabla,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=BG_HOVER,
                text_color=TEXT_SECONDARY,
                padx=10,
                pady=8
            ).grid(row=0, column=i, sticky="ew", padx=1, pady=1)
        
        # Filas de categorías
        if not self.categorias:
            ctk.CTkLabel(
                self.frame_tabla,
                text="No hay categorías registradas",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).grid(row=1, column=0, columnspan=4, pady=30)
            return
        
        for idx, cat in enumerate(self.categorias, start=1):
            bg_color = BG_HOVER if idx % 2 == 0 else "transparent"
            
            ctk.CTkLabel(
                self.frame_tabla,
                text=str(cat['id']),
                fg_color=bg_color,
                padx=10,
                pady=6
            ).grid(row=idx, column=0, sticky="ew", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla,
                text=cat['nombre'],
                fg_color=bg_color,
                padx=10,
                pady=6
            ).grid(row=idx, column=1, sticky="ew", padx=1)
            
            ctk.CTkLabel(
                self.frame_tabla,
                text=cat.get('descripcion', '') or '',
                fg_color=bg_color,
                padx=10,
                pady=6
            ).grid(row=idx, column=2, sticky="ew", padx=1)
            
            # Botones de acción
            frame_acciones = ctk.CTkFrame(self.frame_tabla, fg_color=bg_color)
            frame_acciones.grid(row=idx, column=3, sticky="ew", padx=1)
            
            ctk.CTkButton(
                frame_acciones,
                text="✏️",
                width=35,
                fg_color="#3a4a6b",
                hover_color="#4a5a7b",
                text_color="#ffffff",
                command=lambda c=cat: self.abrir_formulario_editar(c)
            ).pack(side="left", padx=2, pady=2)
            
            ctk.CTkButton(
                frame_acciones,
                text="🗑️",
                width=35,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                text_color="#ffffff",
                command=lambda c=cat: self.confirmar_eliminar(c)
            ).pack(side="left", padx=2, pady=2)
    
    def abrir_formulario_nuevo(self):
        """Abre el formulario para crear una nueva categoría."""
        FormularioCategoria(self, self.guardar_categoria)
    
    def abrir_formulario_editar(self, categoria: dict):
        """Abre el formulario para editar una categoría."""
        FormularioCategoria(self, self.actualizar_categoria_callback, categoria)
    
    def guardar_categoria(self, nombre: str, descripcion: str):
        """Guarda una nueva categoría."""
        try:
            crear_categoria(nombre, descripcion)
            CTkMessagebox(
                title="Éxito",
                message="Categoría creada correctamente",
                icon="check"
            )
            self.cargar_datos()
        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Error al crear categoría: {str(e)}",
                icon="cancel"
            )
    
    def actualizar_categoria_callback(self, nombre: str, descripcion: str, categoria_id: int = None):
        """Actualiza una categoría existente."""
        if categoria_id:
            if actualizar_categoria(categoria_id, nombre, descripcion):
                CTkMessagebox(
                    title="Éxito",
                    message="Categoría actualizada correctamente",
                    icon="check"
                )
                self.cargar_datos()
            else:
                CTkMessagebox(
                    title="Error",
                    message="Error al actualizar categoría",
                    icon="cancel"
                )
    
    def confirmar_eliminar(self, categoria: dict):
        """Confirma y elimina una categoría."""
        msg = CTkMessagebox(
            title="Confirmar Eliminación",
            message=f"¿Eliminar la categoría '{categoria['nombre']}'?\n\nLos productos de esta categoría quedarán sin categoría asignada.",
            icon="warning",
            option_1="Cancelar",
            option_2="Eliminar"
        )
        
        if msg.get() == "Eliminar":
            if eliminar_categoria(categoria['id']):
                CTkMessagebox(
                    title="Éxito",
                    message="Categoría eliminada correctamente",
                    icon="check"
                )
                self.cargar_datos()
            else:
                CTkMessagebox(
                    title="Error",
                    message="Error al eliminar categoría",
                    icon="cancel"
                )


class FormularioCategoria(ctk.CTkToplevel):
    """Formulario para crear/editar categorías."""
    
    def __init__(self, parent, callback, categoria: dict = None):
        super().__init__(parent)
        
        # Configurar color de fondo oscuro ANTES de todo para evitar flash blanco
        self.configure(fg_color="#1a1a2e")
        
        # Ocultar la ventana mientras se configura
        self.withdraw()
        
        self.callback = callback
        self.categoria = categoria
        self.es_edicion = categoria is not None
        
        # Configuración de la ventana
        self.title("Editar Categoría" if self.es_edicion else "Nueva Categoría")
        self.geometry("400x280")
        self.resizable(False, False)
        
        # Centrar ventana - usar solo transient (no grab_set para evitar flash)
        self.transient(parent)
        
        # Prevenir error de focus al cerrar
        self.protocol("WM_DELETE_WINDOW", self.cerrar_formulario)
        
        self.setup_ui()
        
        if self.es_edicion:
            self.cargar_datos()
        
        # Centrar en la pantalla y mostrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 280) // 2
        self.geometry(f"400x280+{x}+{y}")
        self.deiconify()
    
    def cerrar_formulario(self):
        """Cierra el formulario de forma segura."""
        try:
            self.grab_release()
        except:
            pass
        self.withdraw()
        self.after(50, self.destroy)
    
    def setup_ui(self):
        """Configura la interfaz del formulario."""
        self.grid_columnconfigure(1, weight=1)
        
        # Nombre
        ctk.CTkLabel(self, text="Nombre:*").grid(row=0, column=0, padx=20, pady=15, sticky="e")
        self.entry_nombre = ctk.CTkEntry(self, width=250)
        self.entry_nombre.grid(row=0, column=1, padx=20, pady=15, sticky="ew")
        
        # Descripción (usando Entry en lugar de Textbox para evitar errores de focus)
        ctk.CTkLabel(self, text="Descripción:").grid(row=1, column=0, padx=20, pady=15, sticky="e")
        self.entry_descripcion = ctk.CTkEntry(self, width=250, placeholder_text="Descripción opcional...")
        self.entry_descripcion.grid(row=1, column=1, padx=20, pady=15, sticky="ew")
        
        # Botones
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.grid(row=2, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(
            frame_botones,
            text="❌ Cancelar",
            fg_color="gray",
            command=self.cerrar_formulario
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            frame_botones,
            text="💾 Guardar",
            fg_color="#28a745",
            command=self.guardar
        ).pack(side="left", padx=10)
    
    def cargar_datos(self):
        """Carga los datos de la categoría a editar."""
        self.entry_nombre.insert(0, self.categoria['nombre'])
        if self.categoria.get('descripcion'):
            self.entry_descripcion.insert(0, self.categoria['descripcion'])
    
    def guardar(self):
        """Valida y guarda la categoría."""
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        
        if not nombre:
            CTkMessagebox(
                title="Error",
                message="El nombre es obligatorio",
                icon="warning"
            )
            return
        
        if self.es_edicion:
            self.callback(nombre, descripcion, self.categoria['id'])
        else:
            self.callback(nombre, descripcion)
        
        self.cerrar_formulario()
