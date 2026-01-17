# Sistema de Ventas e Inventario

Sistema de gestión comercial para tiendas con manejo de tasa de cambio USD/Bs.

## Tecnologías
- Python 3.11+
- SQLite (Base de datos local)
- CustomTkinter (Interfaz gráfica)

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar:
```bash
python src/main.py
```

## Estructura del Proyecto
```
SistemaVentas/
├── src/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── views/
│   ├── controllers/
│   ├── utils/
│   └── assets/
├── data/
├── backups/
└── requirements.txt
```
