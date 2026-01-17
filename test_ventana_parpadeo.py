"""
Ventana de prueba para diagnosticar el parpadeo en CTkToplevel
"""
import customtkinter as ctk

# Configurar tema oscuro
ctk.set_appearance_mode("dark")


class VentanaPrueba(ctk.CTkToplevel):
    """Ventana de prueba simple."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # PRUEBA 1: Configurar color de fondo oscuro inmediatamente
        self.configure(fg_color="#1a1a2e")
        
        # PRUEBA 2: Ocultar mientras se configura
        self.withdraw()
        
        self.title("🧪 Ventana de Prueba")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # PRUEBA 3: Solo transient, sin grab_set
        self.transient(parent)
        # self.grab_set()  # <-- Comentado para probar
        
        # Crear widgets simples
        self.setup_ui()
        
        # Centrar en la pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 300) // 2
        self.geometry(f"400x300+{x}+{y}")
        
        # Mostrar la ventana
        self.deiconify()
    
    def setup_ui(self):
        """Widgets simples de prueba."""
        ctk.CTkLabel(
            self,
            text="🧪 Ventana de Prueba",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Campo 1
        ctk.CTkLabel(self, text="Campo 1:").pack(anchor="w", padx=20)
        ctk.CTkEntry(self, width=300, placeholder_text="Escribe algo...").pack(padx=20, pady=5)
        
        # Campo 2
        ctk.CTkLabel(self, text="Campo 2:").pack(anchor="w", padx=20, pady=(10, 0))
        ctk.CTkEntry(self, width=300, placeholder_text="Otro campo...").pack(padx=20, pady=5)
        
        # Botón cerrar
        ctk.CTkButton(
            self,
            text="Cerrar",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.destroy
        ).pack(pady=20)


class AppPrincipal(ctk.CTk):
    """App principal de prueba."""
    
    def __init__(self):
        super().__init__()
        
        self.title("App de Prueba - Parpadeo")
        self.geometry("600x400")
        self.configure(fg_color="#1a1a2e")
        
        # Sidebar simple
        self.sidebar = ctk.CTkFrame(self, width=150, fg_color="#16213e")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(
            self.sidebar,
            text="MENÚ",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=20)
        
        # Botón para abrir ventana de prueba
        ctk.CTkButton(
            self.sidebar,
            text="📝 Abrir Ventana",
            fg_color="#0ea5e9",
            hover_color="#0284c7",
            command=self.abrir_ventana
        ).pack(pady=10, padx=10, fill="x")
        
        # Contenido principal
        self.main_content = ctk.CTkFrame(self, fg_color="#1a1a2e")
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            self.main_content,
            text="Haz clic en 'Abrir Ventana' para probar",
            font=ctk.CTkFont(size=16)
        ).pack(expand=True)
    
    def abrir_ventana(self):
        """Abre la ventana de prueba."""
        VentanaPrueba(self)


if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()
