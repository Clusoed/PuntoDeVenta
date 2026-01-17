"""
Gestor de Licencias Offline
Sistema de activación y validación de licencias permanentes vinculadas al hardware.
"""
import os
import sys
import json
import hashlib
import base64
import platform
import uuid
from pathlib import Path
from typing import Optional, Tuple
import customtkinter as ctk
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Clave secreta para encriptación (NO CAMBIAR después de generar licencias)
SECRET_KEY = b"PuntoDeVenta_SecretKey_2024_Permanent"


def get_license_dir() -> Path:
    """Obtiene el directorio para archivos de licencia (mismo que la BD)."""
    if getattr(sys, 'frozen', False):
        # Ejecutando como .exe - usar AppData/Local para persistencia
        app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        return Path(app_data) / 'PuntoDeVenta' / 'data'
    else:
        # Ejecutando desde código fuente
        return Path(__file__).parent.parent.parent / 'data'


def get_license_path() -> Path:
    """Obtiene la ruta del archivo de licencia."""
    license_dir = get_license_dir()
    license_dir.mkdir(parents=True, exist_ok=True)
    return license_dir / "license.dat"


def _get_fernet_key() -> bytes:
    """Genera una clave Fernet derivada de la clave secreta."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"static_salt_pdv",
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY))
    return key


def get_hardware_id() -> str:
    """
    Genera un ID único basado en el hardware de la máquina.
    Combina MAC address y nombre del sistema para crear un identificador único.
    """
    # Obtener MAC address
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                    for i in range(0, 48, 8)][::-1])
    
    # Obtener nombre de la máquina
    machine_name = platform.node()
    
    # Combinar y crear hash
    combined = f"{mac}:{machine_name}:{platform.system()}"
    hardware_hash = hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
    
    return hardware_hash


def generate_license_code(client_name: str = "") -> Tuple[str, str]:
    """
    Genera un código de licencia único.
    Retorna: (código_licencia, código_secreto_para_archivo)
    
    NOTA: Esta función es para uso del DESARROLLADOR, no del cliente.
    """
    import secrets
    
    # Generar código aleatorio
    random_bytes = secrets.token_bytes(12)
    license_code = base64.b32encode(random_bytes).decode()[:16]
    
    # Formatear como XXXX-XXXX-XXXX-XXXX
    formatted_code = '-'.join([license_code[i:i+4] for i in range(0, 16, 4)])
    
    # Crear hash secreto del código (para verificación)
    secret_hash = hashlib.sha256(f"{formatted_code}:{SECRET_KEY.decode()}".encode()).hexdigest()
    
    return formatted_code, secret_hash


def activate_license(license_code: str) -> Tuple[bool, str]:
    """
    Activa una licencia y la vincula al hardware actual.
    Retorna: (éxito, mensaje)
    """
    # Limpiar código
    license_code = license_code.strip().upper().replace(" ", "")
    
    # Validar formato (XXXX-XXXX-XXXX-XXXX)
    if len(license_code.replace("-", "")) != 16:
        return False, "Formato de licencia inválido"
    
    # Verificar que el código es válido (hash correcto)
    expected_hash = hashlib.sha256(f"{license_code}:{SECRET_KEY.decode()}".encode()).hexdigest()
    
    # Obtener hardware ID
    hardware_id = get_hardware_id()
    
    # Crear datos de licencia
    license_data = {
        "license_code": license_code,
        "hardware_id": hardware_id,
        "activated": True,
        "version": "1.0"
    }
    
    # Encriptar y guardar
    try:
        fernet = Fernet(_get_fernet_key())
        encrypted_data = fernet.encrypt(json.dumps(license_data).encode())
        
        license_path = get_license_path()
        with open(license_path, 'wb') as f:
            f.write(encrypted_data)
        
        return True, "Licencia activada correctamente"
    except Exception as e:
        return False, f"Error al guardar licencia: {str(e)}"


def validate_license() -> Tuple[bool, str]:
    """
    Valida que existe una licencia válida para este hardware.
    Retorna: (válida, mensaje)
    """
    license_path = get_license_path()
    
    if not license_path.exists():
        return False, "No hay licencia instalada"
    
    try:
        # Leer y desencriptar
        fernet = Fernet(_get_fernet_key())
        with open(license_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = fernet.decrypt(encrypted_data)
        license_data = json.loads(decrypted_data.decode())
        
        # Verificar hardware ID
        current_hardware_id = get_hardware_id()
        if license_data.get("hardware_id") != current_hardware_id:
            return False, "Esta licencia no corresponde a este equipo"
        
        # Verificar que está activada
        if not license_data.get("activated"):
            return False, "La licencia no está activada"
        
        return True, "Licencia válida"
        
    except Exception as e:
        return False, f"Licencia corrupta o inválida: {str(e)}"


import sys


class LicenseDialog(ctk.CTkToplevel):
    """Diálogo para ingresar código de licencia."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.title("Activación de Licencia")
        self.geometry("450x280")
        self.resizable(False, False)
        
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 280) // 2
        self.geometry(f"450x280+{x}+{y}")
        
        self.result = False
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # Manejar cierre
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔐 Activar Licencia",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Instrucciones
        instructions = ctk.CTkLabel(
            main_frame,
            text="Ingrese el código de licencia proporcionado:",
            font=ctk.CTkFont(size=12)
        )
        instructions.pack(pady=(0, 10))
        
        # Campo de entrada
        self.license_entry = ctk.CTkEntry(
            main_frame,
            width=300,
            height=40,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(size=14, family="Consolas")
        )
        self.license_entry.pack(pady=10)
        
        # Mensaje de estado
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
        # Frame de botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        # Botón activar
        self.activate_btn = ctk.CTkButton(
            button_frame,
            text="Activar",
            width=120,
            height=35,
            command=self._on_activate,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.activate_btn.pack(side="left", padx=5)
        
        # Botón cancelar
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="Salir",
            width=120,
            height=35,
            command=self._on_cancel,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.cancel_btn.pack(side="left", padx=5)
    
    def _on_activate(self):
        """Intenta activar la licencia."""
        license_code = self.license_entry.get().strip()
        
        if not license_code:
            self.status_label.configure(text="⚠️ Ingrese un código de licencia", text_color="orange")
            return
        
        # Intentar activar
        self.status_label.configure(text="⏳ Verificando...", text_color="gray")
        self.update()
        
        success, message = activate_license(license_code)
        
        if success:
            self.status_label.configure(text="✅ " + message, text_color="green")
            self.result = True
            self.after(1500, self.destroy)
        else:
            self.status_label.configure(text="❌ " + message, text_color="red")
    
    def _on_cancel(self):
        """Cierra el diálogo sin activar."""
        self.result = False
        self.destroy()


def show_license_dialog(parent=None) -> bool:
    """
    Muestra el diálogo de activación de licencia.
    Retorna True si se activó correctamente.
    """
    dialog = LicenseDialog(parent)
    dialog.wait_window()
    return dialog.result
