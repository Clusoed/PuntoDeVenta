"""
Tema visual de la aplicación - Estilo Minimalista
"""

# ============== PALETA DE COLORES ==============

# Fondos
BG_PRINCIPAL = "#1a1a2e"      # Fondo principal oscuro
BG_SECUNDARIO = "#16213e"     # Cards y contenedores
BG_SIDEBAR = "#0f0f23"        # Sidebar
BG_HOVER = "#1f2847"          # Hover en elementos

# Textos
TEXT_PRIMARY = "#ffffff"       # Texto principal
TEXT_SECONDARY = "#a0a0a0"     # Texto secundario/sutil
TEXT_MUTED = "#6c6c8a"         # Texto muy sutil

# Acentos
ACCENT_PRIMARY = "#0ea5e9"     # Azul eléctrico principal
ACCENT_HOVER = "#0284c7"       # Azul eléctrico hover
ACCENT_LIGHT = "#0c4a6e"       # Azul muy sutil (fondos)

# Bordes
BORDER_COLOR = "#2a2a4a"       # Bordes sutiles
BORDER_SELECTED = "#0ea5e9"    # Borde seleccionado

# Estados
SUCCESS = "#22c55e"            # Éxito (verde)
WARNING = "#ffa500"            # Advertencia
ERROR = "#ff6b6b"              # Error
INFO = "#3498db"               # Información

# Botones
BTN_PRIMARY = "#0ea5e9"        # Botón principal
BTN_PRIMARY_HOVER = "#0284c7"  
BTN_SECONDARY = "#3a3a5a"      # Botón secundario
BTN_SECONDARY_HOVER = "#4a4a6a"
BTN_DANGER = "#ff6b6b"
BTN_DANGER_HOVER = "#ff5252"

# Tabla/Lista
TABLE_HEADER = "#1f2847"       # Encabezado tabla
TABLE_ROW_ODD = "#16213e"      # Fila impar
TABLE_ROW_EVEN = "#1a1a2e"     # Fila par
TABLE_ROW_HOVER = "#1f2847"    # Hover en fila

# ============== ESTILOS PREDEFINIDOS ==============

# Estilo de card/frame
CARD_STYLE = {
    "fg_color": BG_SECUNDARIO,
    "border_color": BORDER_COLOR,
    "border_width": 1,
    "corner_radius": 10
}

# Estilo de botón principal
BTN_PRIMARY_STYLE = {
    "fg_color": BTN_PRIMARY,
    "hover_color": BTN_PRIMARY_HOVER,
    "text_color": "#000000",
    "corner_radius": 8,
    "border_width": 0
}

# Estilo de botón secundario (outlined)
BTN_OUTLINED_STYLE = {
    "fg_color": "transparent",
    "hover_color": BG_HOVER,
    "text_color": ACCENT_PRIMARY,
    "border_color": ACCENT_PRIMARY,
    "border_width": 1,
    "corner_radius": 8
}

# Estilo de botón peligro
BTN_DANGER_STYLE = {
    "fg_color": BTN_DANGER,
    "hover_color": BTN_DANGER_HOVER,
    "text_color": "#ffffff",
    "corner_radius": 8
}

# Estilo de input/entry
ENTRY_STYLE = {
    "fg_color": BG_PRINCIPAL,
    "border_color": BORDER_COLOR,
    "border_width": 1,
    "text_color": TEXT_PRIMARY,
    "corner_radius": 6
}

# Estilo de dropdown/combobox
DROPDOWN_STYLE = {
    "fg_color": BG_PRINCIPAL,
    "border_color": BORDER_COLOR,
    "border_width": 1,
    "text_color": TEXT_PRIMARY,
    "button_color": BG_SECUNDARIO,
    "button_hover_color": BG_HOVER,
    "dropdown_fg_color": BG_SECUNDARIO,
    "dropdown_hover_color": BG_HOVER,
    "corner_radius": 6
}

# ============== FUNCIONES HELPER ==============

def aplicar_estilo_card(frame):
    """Aplica estilo de card a un frame."""
    frame.configure(**CARD_STYLE)

def aplicar_estilo_boton_primario(button):
    """Aplica estilo de botón principal."""
    button.configure(**BTN_PRIMARY_STYLE)

def aplicar_estilo_boton_outlined(button):
    """Aplica estilo de botón outlined."""
    button.configure(**BTN_OUTLINED_STYLE)

def aplicar_estilo_entrada(entry):
    """Aplica estilo a un campo de entrada."""
    entry.configure(**ENTRY_STYLE)
