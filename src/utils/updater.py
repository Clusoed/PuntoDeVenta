"""
Sistema de Actualizaciones Automáticas
Verifica y descarga actualizaciones desde GitHub Releases.
"""
import os
import sys
import json
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Optional, Tuple, Dict
import customtkinter as ctk

try:
    import requests
except ImportError:
    requests = None


# Configuración del repositorio
GITHUB_REPO = "Clusoed/PuntoDeVenta"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def get_base_path() -> Path:
    """Obtiene el directorio base de la aplicación."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent.parent


def get_current_version() -> str:
    """Obtiene la versión actual desde config.json."""
    config_path = get_base_path() / "config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("version", "0.0.0")
    except Exception:
        return "0.0.0"


def parse_version(version: str) -> Tuple[int, ...]:
    """Convierte una versión string a tupla de enteros para comparación."""
    try:
        # Remover 'v' si existe y limpiar
        version = version.lower().replace('v', '').strip()
        parts = version.split('.')
        return tuple(int(p) for p in parts[:3])
    except (ValueError, AttributeError):
        return (0, 0, 0)


def check_for_updates() -> Tuple[bool, Optional[Dict]]:
    """
    Verifica si hay una nueva versión disponible en GitHub.
    Retorna: (hay_actualizacion, info_release)
    """
    if requests is None:
        return False, None
    
    try:
        response = requests.get(GITHUB_API_URL, timeout=10)
        
        if response.status_code != 200:
            return False, None
        
        release_info = response.json()
        
        # Obtener versión del release
        latest_version = release_info.get("tag_name", "0.0.0")
        current_version = get_current_version()
        
        # Comparar versiones
        if parse_version(latest_version) > parse_version(current_version):
            # Buscar el asset .exe
            assets = release_info.get("assets", [])
            exe_asset = None
            
            for asset in assets:
                if asset.get("name", "").endswith(".exe"):
                    exe_asset = asset
                    break
            
            return True, {
                "version": latest_version,
                "current_version": current_version,
                "changelog": release_info.get("body", "Sin información de cambios"),
                "download_url": exe_asset.get("browser_download_url") if exe_asset else None,
                "asset_name": exe_asset.get("name") if exe_asset else None,
                "published_at": release_info.get("published_at", "")
            }
        
        return False, None
        
    except Exception as e:
        print(f"Error verificando actualizaciones: {e}")
        return False, None


def download_update(download_url: str, progress_callback=None) -> Optional[Path]:
    """
    Descarga la actualización a un directorio temporal.
    Retorna la ruta del archivo descargado o None si falla.
    """
    if requests is None or not download_url:
        return None
    
    try:
        # Crear directorio temporal
        temp_dir = Path(tempfile.gettempdir()) / "pdv_update"
        temp_dir.mkdir(exist_ok=True)
        
        # Nombre del archivo
        filename = download_url.split("/")[-1]
        temp_file = temp_dir / filename
        
        # Descargar con progreso
        response = requests.get(download_url, stream=True, timeout=300)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        progress_callback(progress)
        
        return temp_file
        
    except Exception as e:
        print(f"Error descargando actualización: {e}")
        return None


def apply_update(update_file: Path):
    """
    Aplica la actualización: cierra la app actual y ejecuta el nuevo .exe.
    El nuevo .exe debería reemplazar al antiguo.
    """
    if not update_file.exists():
        return
    
    # Crear un script batch que espera, reemplaza y ejecuta
    current_exe = sys.executable if getattr(sys, 'frozen', False) else None
    
    if current_exe:
        batch_content = f'''@echo off
timeout /t 2 /nobreak > nul
copy /y "{update_file}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
'''
        batch_file = Path(tempfile.gettempdir()) / "pdv_update.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        # Ejecutar el batch y cerrar la app
        subprocess.Popen(f'cmd /c "{batch_file}"', shell=True)
        sys.exit(0)
    else:
        # En modo desarrollo, solo mostrar mensaje
        print(f"Actualización descargada en: {update_file}")
        print("En modo desarrollo, la actualización no se aplica automáticamente.")


class UpdateDialog(ctk.CTkToplevel):
    """Diálogo para mostrar y aplicar actualizaciones."""
    
    def __init__(self, parent, update_info: Dict):
        super().__init__(parent)
        
        self.update_info = update_info
        self.title("Actualización Disponible")
        self.geometry("500x350")
        self.resizable(False, False)
        
        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"500x350+{x}+{y}")
        
        self.result = False
        self.is_downloading = False
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_later)
    
    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icono y título
        title_label = ctk.CTkLabel(
            main_frame,
            text="🚀 Nueva Versión Disponible",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Info de versiones
        version_frame = ctk.CTkFrame(main_frame, fg_color=("gray90", "gray20"))
        version_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            version_frame,
            text=f"Versión actual: {self.update_info.get('current_version', '?')}",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            version_frame,
            text=f"Nueva versión: {self.update_info.get('version', '?')}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("green", "#4CAF50")
        ).pack(pady=5)
        
        # Changelog
        changelog_label = ctk.CTkLabel(
            main_frame,
            text="Cambios:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        changelog_label.pack(fill="x", pady=(10, 5))
        
        changelog_text = ctk.CTkTextbox(main_frame, height=80, wrap="word")
        changelog_text.pack(fill="x")
        changelog_text.insert("1.0", self.update_info.get("changelog", "Sin información"))
        changelog_text.configure(state="disabled")
        
        # Barra de progreso (oculta inicialmente)
        self.progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Descargando...",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack()
        
        # Botones
        self.button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.button_frame.pack(pady=15)
        
        self.update_btn = ctk.CTkButton(
            self.button_frame,
            text="Actualizar Ahora",
            width=140,
            height=35,
            command=self._on_update,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.update_btn.pack(side="left", padx=5)
        
        self.later_btn = ctk.CTkButton(
            self.button_frame,
            text="Más Tarde",
            width=140,
            height=35,
            command=self._on_later,
            fg_color="gray50",
            hover_color="gray40"
        )
        self.later_btn.pack(side="left", padx=5)
    
    def _on_update(self):
        """Inicia la descarga e instalación."""
        if self.is_downloading:
            return
        
        download_url = self.update_info.get("download_url")
        if not download_url:
            self.progress_label.configure(text="❌ No se encontró el archivo de actualización")
            return
        
        self.is_downloading = True
        self.update_btn.configure(state="disabled")
        self.later_btn.configure(state="disabled")
        self.button_frame.pack_forget()
        self.progress_frame.pack(pady=10)
        
        # Descargar en hilo separado
        def download_thread():
            def update_progress(progress):
                self.after(0, lambda: self._update_progress(progress))
            
            update_file = download_update(download_url, update_progress)
            
            if update_file:
                self.after(0, lambda: self._on_download_complete(update_file))
            else:
                self.after(0, self._on_download_error)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def _update_progress(self, progress: int):
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"Descargando... {progress}%")
    
    def _on_download_complete(self, update_file: Path):
        self.progress_label.configure(text="✅ Descarga completa. Aplicando actualización...")
        self.progress_bar.set(1)
        self.after(1000, lambda: apply_update(update_file))
    
    def _on_download_error(self):
        self.progress_label.configure(text="❌ Error al descargar la actualización")
        self.is_downloading = False
        self.progress_frame.pack_forget()
        self.button_frame.pack(pady=15)
        self.update_btn.configure(state="normal")
        self.later_btn.configure(state="normal")
    
    def _on_later(self):
        if not self.is_downloading:
            self.destroy()


def check_and_prompt_update(parent=None):
    """
    Verifica actualizaciones y muestra el diálogo si hay una nueva versión.
    Esta función debe llamarse al inicio de la aplicación.
    """
    def check_thread():
        has_update, update_info = check_for_updates()
        
        if has_update and update_info:
            # Mostrar diálogo en el hilo principal
            if parent:
                parent.after(0, lambda: UpdateDialog(parent, update_info))
            else:
                # Sin parent, crear una ventana temporal
                root = ctk.CTk()
                root.withdraw()
                dialog = UpdateDialog(root, update_info)
                dialog.wait_window()
                root.destroy()
    
    # Ejecutar en segundo plano para no bloquear el inicio
    threading.Thread(target=check_thread, daemon=True).start()
