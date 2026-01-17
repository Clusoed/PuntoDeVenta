"""
Vista de Gestión de Clientes - Diseño Minimalista
"""
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_connection
from utils.theme import BG_PRINCIPAL, BG_SECUNDARIO, BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY, BG_HOVER


class ClientesView(ctk.CTkFrame):
    """Vista de gestión de clientes."""
    
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=BG_PRINCIPAL)
        self.app = app_controller
        self.clientes = []
        
        self.setup_ui()
        self.cargar_clientes()
    
    def setup_ui(self):
        """Configura la interfaz de clientes."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_header,
            text="👥 GESTIÓN DE CLIENTES",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Botón nuevo cliente
        ctk.CTkButton(
            frame_header,
            text="➕ Nuevo Cliente",
            fg_color=ACCENT_PRIMARY,
            hover_color="#0284c7",
            command=self.abrir_formulario
        ).grid(row=0, column=2, padx=10)
        
        # Búsqueda
        frame_busqueda = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_busqueda.grid(row=0, column=1, sticky="e", padx=20)
        
        self.entry_buscar = ctk.CTkEntry(
            frame_busqueda,
            width=250,
            placeholder_text="🔍 Buscar por nombre o cédula..."
        )
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind("<KeyRelease>", self.buscar_clientes)
        
        # === TABLA DE CLIENTES ===
        self.frame_tabla = ctk.CTkScrollableFrame(self)
        self.frame_tabla.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        for i in range(6):
            self.frame_tabla.grid_columnconfigure(i, weight=1)
    
    def cargar_clientes(self):
        """Carga los clientes de la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, cedula_rif, nombre, telefono, direccion, email
            FROM clientes
            WHERE activo = 1
            ORDER BY nombre
        ''')
        self.clientes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.mostrar_clientes()
    
    def mostrar_clientes(self, clientes=None):
        """Muestra los clientes en la tabla."""
        # Limpiar tabla
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        
        # Headers
        headers = ["Cédula/RIF", "Nombre", "Teléfono", "Email", "Dirección", "Acciones"]
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
        
        # Datos
        lista = clientes if clientes is not None else self.clientes
        
        if not lista:
            ctk.CTkLabel(
                self.frame_tabla,
                text="No hay clientes registrados",
                text_color="gray"
            ).grid(row=1, column=0, columnspan=6, pady=30)
            return
        
        for idx, cliente in enumerate(lista, start=1):
            bg = "gray20" if idx % 2 == 0 else "transparent"
            
            # Cédula
            ctk.CTkLabel(
                self.frame_tabla,
                text=cliente.get('cedula_rif') or '-',
                fg_color=bg,
                padx=10, pady=5
            ).grid(row=idx, column=0, sticky="ew", padx=2)
            
            # Nombre
            ctk.CTkLabel(
                self.frame_tabla,
                text=cliente['nombre'],
                fg_color=bg,
                padx=10, pady=5
            ).grid(row=idx, column=1, sticky="ew", padx=2)
            
            # Teléfono
            ctk.CTkLabel(
                self.frame_tabla,
                text=cliente.get('telefono') or '-',
                fg_color=bg,
                padx=10, pady=5
            ).grid(row=idx, column=2, sticky="ew", padx=2)
            
            # Email
            ctk.CTkLabel(
                self.frame_tabla,
                text=cliente.get('email') or '-',
                fg_color=bg,
                padx=10, pady=5
            ).grid(row=idx, column=3, sticky="ew", padx=2)
            
            # Dirección
            direccion = cliente.get('direccion') or '-'
            if len(direccion) > 30:
                direccion = direccion[:30] + "..."
            ctk.CTkLabel(
                self.frame_tabla,
                text=direccion,
                fg_color=bg,
                padx=10, pady=5
            ).grid(row=idx, column=4, sticky="ew", padx=2)
            
            # Acciones
            frame_acciones = ctk.CTkFrame(self.frame_tabla, fg_color=bg)
            frame_acciones.grid(row=idx, column=5, sticky="ew", padx=2)
            
            ctk.CTkButton(
                frame_acciones,
                text="✏️",
                width=30,
                height=25,
                fg_color="#3a4a6b",
                hover_color="#4a5a7b",
                text_color="#ffffff",
                command=lambda c=cliente: self.editar_cliente(c)
            ).pack(side="left", padx=2, pady=2)
            
            ctk.CTkButton(
                frame_acciones,
                text="🗑️",
                width=30,
                height=25,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                text_color="#ffffff",
                command=lambda c=cliente: self.eliminar_cliente(c)
            ).pack(side="left", padx=2, pady=2)
    
    def buscar_clientes(self, event=None):
        """Filtra clientes según el término de búsqueda."""
        termino = self.entry_buscar.get().strip().lower()
        if not termino:
            self.mostrar_clientes()
            return
        
        filtrados = [
            c for c in self.clientes
            if termino in c['nombre'].lower() or 
               termino in (c.get('cedula_rif') or '').lower()
        ]
        self.mostrar_clientes(filtrados)
    
    def abrir_formulario(self, cliente=None):
        """Abre el formulario de cliente."""
        FormularioCliente(self, cliente, self.guardar_cliente)
    
    def editar_cliente(self, cliente):
        """Edita un cliente."""
        self.abrir_formulario(cliente)
    
    def guardar_cliente(self, datos, cliente_id=None):
        """Guarda o actualiza un cliente."""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if cliente_id:
                cursor.execute('''
                    UPDATE clientes SET
                        cedula_rif = ?, nombre = ?, telefono = ?,
                        email = ?, direccion = ?
                    WHERE id = ?
                ''', (
                    datos['cedula_rif'], datos['nombre'], datos['telefono'],
                    datos['email'], datos['direccion'], cliente_id
                ))
                mensaje = "Cliente actualizado correctamente"
            else:
                cursor.execute('''
                    INSERT INTO clientes (cedula_rif, nombre, telefono, email, direccion)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    datos['cedula_rif'], datos['nombre'], datos['telefono'],
                    datos['email'], datos['direccion']
                ))
                mensaje = "Cliente guardado correctamente"
            
            conn.commit()
            self.cargar_clientes()
            CTkMessagebox(title="Éxito", message=mensaje, icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Error: {str(e)}", icon="cancel")
        finally:
            conn.close()
    
    def eliminar_cliente(self, cliente):
        """Desactiva un cliente."""
        msg = CTkMessagebox(
            title="Confirmar",
            message=f"¿Desea eliminar el cliente '{cliente['nombre']}'?",
            icon="question",
            option_1="Cancelar",
            option_2="Eliminar"
        )
        
        if msg.get() == "Eliminar":
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE clientes SET activo = 0 WHERE id = ?', (cliente['id'],))
            conn.commit()
            conn.close()
            self.cargar_clientes()
            CTkMessagebox(title="Éxito", message="Cliente eliminado", icon="check")


class FormularioCliente(ctk.CTkToplevel):
    """Formulario para crear/editar clientes."""
    
    def __init__(self, parent, cliente, callback):
        super().__init__(parent)
        
        # Configurar color de fondo oscuro ANTES de todo para evitar flash blanco
        self.configure(fg_color="#1a1a2e")
        
        # Ocultar la ventana mientras se configura
        self.withdraw()
        
        self.cliente = cliente
        self.callback = callback
        self.es_edicion = cliente is not None
        
        self.title("Editar Cliente" if self.es_edicion else "Nuevo Cliente")
        self.geometry("500x480")
        self.resizable(False, False)
        
        # Centrar ventana - usar solo transient (no grab_set para evitar flash)
        self.transient(parent)
        
        # Prevenir error de focus al cerrar
        self.protocol("WM_DELETE_WINDOW", self.cerrar_formulario)
        
        self.setup_ui()
        
        if self.es_edicion:
            self.cargar_cliente()
        
        # Centrar en la pantalla y mostrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 480) // 2
        self.geometry(f"500x480+{x}+{y}")
        self.deiconify()
    
    def cerrar_formulario(self):
        """Cierra el formulario de forma segura."""
        try:
            self.grab_release()
        except:
            pass
        # Ocultar primero para evitar errores de focus
        self.withdraw()
        # Destruir después de un pequeño delay
        self.after(50, self.destroy)
    
    def setup_ui(self):
        """Configura el formulario."""
        padding = {"padx": 20, "pady": 5}
        
        # Cédula/RIF
        ctk.CTkLabel(self, text="Cédula/RIF:").pack(anchor="w", **padding)
        self.entry_cedula = ctk.CTkEntry(self, width=200)
        self.entry_cedula.pack(anchor="w", padx=20)
        
        # Nombre
        ctk.CTkLabel(self, text="Nombre:*").pack(anchor="w", **padding)
        self.entry_nombre = ctk.CTkEntry(self, width=350)
        self.entry_nombre.pack(anchor="w", padx=20)
        
        # Teléfono
        ctk.CTkLabel(self, text="Teléfono:").pack(anchor="w", **padding)
        self.entry_telefono = ctk.CTkEntry(self, width=200)
        self.entry_telefono.pack(anchor="w", padx=20)
        
        # Email
        ctk.CTkLabel(self, text="Email:").pack(anchor="w", **padding)
        self.entry_email = ctk.CTkEntry(self, width=300)
        self.entry_email.pack(anchor="w", padx=20)
        
        # Dirección
        ctk.CTkLabel(self, text="Dirección:").pack(anchor="w", **padding)
        self.entry_direccion = ctk.CTkEntry(self, width=400)
        self.entry_direccion.pack(anchor="w", padx=20)
        
        # Botones
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(fill="x", padx=20, pady=30)
        
        ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            fg_color="gray",
            command=self.destroy
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botones,
            text="💾 Guardar",
            command=self.guardar
        ).pack(side="right", padx=5)
    
    def cargar_cliente(self):
        """Carga los datos del cliente a editar."""
        if self.cliente.get('cedula_rif'):
            self.entry_cedula.insert(0, self.cliente['cedula_rif'])
        self.entry_nombre.insert(0, self.cliente['nombre'])
        if self.cliente.get('telefono'):
            self.entry_telefono.insert(0, self.cliente['telefono'])
        if self.cliente.get('email'):
            self.entry_email.insert(0, self.cliente['email'])
        if self.cliente.get('direccion'):
            self.entry_direccion.insert(0, self.cliente['direccion'])
    
    def guardar(self):
        """Valida y guarda el cliente."""
        nombre = self.entry_nombre.get().strip()
        
        if not nombre:
            CTkMessagebox(title="Error", message="El nombre es obligatorio", icon="warning")
            return
        
        datos = {
            'cedula_rif': self.entry_cedula.get().strip() or None,
            'nombre': nombre,
            'telefono': self.entry_telefono.get().strip() or None,
            'email': self.entry_email.get().strip() or None,
            'direccion': self.entry_direccion.get().strip() or None
        }
        
        cliente_id = self.cliente['id'] if self.es_edicion else None
        self.callback(datos, cliente_id)
        self.cerrar_formulario()
