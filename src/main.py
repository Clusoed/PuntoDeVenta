"""
Sistema de Ventas e Inventario
Punto de entrada principal
"""
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.dirname(__file__))

# Inicializar la base de datos antes de importar las vistas
from database import init_database
init_database()

# Importar módulos de licencia y actualizaciones
from utils.license_manager import validate_license, show_license_dialog
from utils.updater import check_and_prompt_update

# Importar la ventana principal
from views.main_window import MainWindow


def main():
    """Función principal que inicia la aplicación."""
    
    # 1. Verificar licencia antes de iniciar
    is_valid, message = validate_license()
    
    if not is_valid:
        # Mostrar diálogo de activación
        import customtkinter as ctk
        
        # Crear ventana temporal para el diálogo
        temp_root = ctk.CTk()
        temp_root.withdraw()  # Ocultar ventana temporal
        
        # Mostrar diálogo de licencia
        activated = show_license_dialog(temp_root)
        temp_root.destroy()
        
        if not activated:
            # Usuario cerró sin activar
            print("Licencia no activada. Cerrando aplicación.")
            return
    
    # 2. Iniciar aplicación principal
    app = MainWindow()
    
    # 3. Verificar actualizaciones después de que la ventana esté lista
    app.after(2000, lambda: check_and_prompt_update(app))
    
    app.mainloop()


if __name__ == "__main__":
    main()
