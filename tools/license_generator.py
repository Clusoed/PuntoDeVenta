#!/usr/bin/env python
"""
Generador de Licencias - HERRAMIENTA PRIVADA
Este script es SOLO para el desarrollador. NO incluir en la distribución al cliente.

Uso:
    python license_generator.py --client "Nombre del Cliente"
    python license_generator.py  # Genera sin nombre
"""
import argparse
import hashlib
import base64
import secrets
from datetime import datetime

# MISMA CLAVE QUE EN license_manager.py - NO CAMBIAR
SECRET_KEY = b"PuntoDeVenta_SecretKey_2024_Permanent"


def generate_license(client_name: str = "") -> dict:
    """
    Genera una nueva licencia válida.
    
    Retorna diccionario con:
    - license_code: Código para dar al cliente
    - secret_hash: Hash interno para verificación
    - client: Nombre del cliente
    - generated_at: Fecha de generación
    """
    # Generar código aleatorio
    random_bytes = secrets.token_bytes(12)
    license_code = base64.b32encode(random_bytes).decode()[:16]
    
    # Formatear como XXXX-XXXX-XXXX-XXXX
    formatted_code = '-'.join([license_code[i:i+4] for i in range(0, 16, 4)])
    
    # Crear hash secreto del código (para verificación posterior si es necesario)
    secret_hash = hashlib.sha256(f"{formatted_code}:{SECRET_KEY.decode()}".encode()).hexdigest()
    
    return {
        "license_code": formatted_code,
        "secret_hash": secret_hash,
        "client": client_name or "Sin nombre",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_license_record(license_info: dict, file_path: str = "licenses_generated.txt"):
    """Guarda un registro de la licencia generada."""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Cliente: {license_info['client']}\n")
        f.write(f"Código: {license_info['license_code']}\n")
        f.write(f"Fecha: {license_info['generated_at']}\n")
        f.write(f"Hash: {license_info['secret_hash'][:32]}...\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generador de licencias para Punto de Venta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python license_generator.py --client "Juan Perez"
  python license_generator.py -c "Tienda ABC" --save
        """
    )
    
    parser.add_argument(
        '-c', '--client',
        type=str,
        default="",
        help="Nombre del cliente"
    )
    
    parser.add_argument(
        '-s', '--save',
        action='store_true',
        help="Guardar registro en licenses_generated.txt"
    )
    
    args = parser.parse_args()
    
    # Generar licencia
    license_info = generate_license(args.client)
    
    # Mostrar resultado
    print("\n" + "="*50)
    print("🔐 LICENCIA GENERADA")
    print("="*50)
    print(f"\n📋 Cliente: {license_info['client']}")
    print(f"📅 Fecha: {license_info['generated_at']}")
    print(f"\n{'*'*50}")
    print(f"📦 CÓDIGO DE LICENCIA:")
    print(f"\n   {license_info['license_code']}")
    print(f"\n{'*'*50}")
    print("\n✅ Envía este código al cliente para activar su licencia.")
    print("⚠️  El código se bloqueará en la primera PC donde se active.\n")
    
    # Guardar registro si se solicitó
    if args.save:
        save_license_record(license_info)
        print(f"💾 Registro guardado en: licenses_generated.txt\n")


if __name__ == "__main__":
    main()
