# Espaçamento padrão necessário entre mesas e cadeiras
CHAIR_SPACE = 1.5

# Paleta de cores usada na visualização
COLORS = {
    'background': (240, 240, 240),
    'wall': (50, 50, 50),
    'bathroom': (170, 210, 230),
    'restriction': (200, 200, 200),
    'table_valid': (100, 180, 100),
    'table_invalid': (220, 100, 100),
    'chair': (160, 120, 80),
    'text': (0, 0, 0),
    'highlight': (255, 255, 0)
}

# Escala de visualização (pixels por unidade)
DEFAULT_SCALE = 15

# Render config
WINDOW_PADDING = 300

# Cadeiras por tipo de mesa
def get_chair_count_for_table(table_width: int) -> int:
    """Retorna o número de cadeiras com base na largura da mesa"""
    return 4 if table_width == 20 else 2