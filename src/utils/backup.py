"""
Sistema de Backup Automático
"""
import os
import shutil
from datetime import datetime
from pathlib import Path


def crear_backup(db_path: str, backup_dir: str = None) -> str:
    """
    Crea un backup de la base de datos.
    
    Args:
        db_path: Ruta de la base de datos
        backup_dir: Directorio de backup (por defecto 'backups/')
    
    Returns:
        Ruta del archivo de backup creado
    """
    if backup_dir is None:
        # Por defecto, crear en carpeta 'backups' junto a la base de datos
        backup_dir = os.path.join(os.path.dirname(db_path), '..', 'backups')
    
    # Crear directorio si no existe
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'backup_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Copiar archivo
    shutil.copy2(db_path, backup_path)
    
    # Limpiar backups antiguos (mantener solo los últimos 10)
    limpiar_backups_antiguos(backup_dir, mantener=10)
    
    return backup_path


def limpiar_backups_antiguos(backup_dir: str, mantener: int = 10):
    """
    Elimina los backups más antiguos, manteniendo solo los especificados.
    
    Args:
        backup_dir: Directorio de backups
        mantener: Número de backups a mantener
    """
    backups = []
    
    for archivo in os.listdir(backup_dir):
        if archivo.startswith('backup_') and archivo.endswith('.db'):
            ruta_completa = os.path.join(backup_dir, archivo)
            backups.append((ruta_completa, os.path.getmtime(ruta_completa)))
    
    # Ordenar por fecha de modificación (más recientes primero)
    backups.sort(key=lambda x: x[1], reverse=True)
    
    # Eliminar los más antiguos
    for ruta, _ in backups[mantener:]:
        try:
            os.remove(ruta)
        except Exception:
            pass


def restaurar_backup(backup_path: str, db_path: str) -> bool:
    """
    Restaura un backup de la base de datos.
    
    Args:
        backup_path: Ruta del archivo de backup
        db_path: Ruta destino de la base de datos
    
    Returns:
        True si se restauró correctamente
    """
    try:
        # Crear backup del estado actual antes de restaurar
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_backup = db_path + f'.pre_restore_{timestamp}'
        shutil.copy2(db_path, temp_backup)
        
        # Restaurar
        shutil.copy2(backup_path, db_path)
        
        # Eliminar backup temporal
        os.remove(temp_backup)
        
        return True
    except Exception as e:
        print(f"Error al restaurar backup: {e}")
        return False


def listar_backups(backup_dir: str) -> list:
    """
    Lista los backups disponibles.
    
    Returns:
        Lista de diccionarios con información de cada backup
    """
    backups = []
    
    if not os.path.exists(backup_dir):
        return backups
    
    for archivo in os.listdir(backup_dir):
        if archivo.startswith('backup_') and archivo.endswith('.db'):
            ruta_completa = os.path.join(backup_dir, archivo)
            stat = os.stat(ruta_completa)
            
            backups.append({
                'nombre': archivo,
                'ruta': ruta_completa,
                'fecha': datetime.fromtimestamp(stat.st_mtime),
                'tamaño_mb': round(stat.st_size / (1024 * 1024), 2)
            })
    
    # Ordenar por fecha (más recientes primero)
    backups.sort(key=lambda x: x['fecha'], reverse=True)
    
    return backups
