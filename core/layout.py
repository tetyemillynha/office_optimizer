class Layout:
    def __init__(self, planta, fixed_elements, movable_tables, spacing):
        self.planta = planta
        self.fixed_elements = fixed_elements
        self.movable_tables = movable_tables
        self.spacing = spacing
        self.restricted_areas = self.calculate_restricted_areas()

    def calculate_restricted_areas(self):
            """Calcula áreas restritas (paredes, banheiro, etc.)"""
            restricted = []
            for elem in self.fixed_elements:
                if elem['tipo'] in ['parede', 'banheiro', 'restricao']:
                    buffer = 3
                    restricted.append({
                        "x": max(0, elem["x"] - buffer),
                        "y": max(0, elem["y"] - buffer),
                        "w": elem["w"] + buffer * 2,
                        "h": elem["h"] + buffer * 2
                    })
            return restricted
        
    def is_valid_position(self, table, other_tables, allow_overlap=False):
        """Verifica se a posição da mesa é válida"""
        # Verifica colisão com elementos fixos (sempre deve ser evitada)
        for area in self.restricted_areas:
            if self.check_collision(table, area):
                return False

        # Verifica colisão com outras mesas, a menos que sobreposição esteja permitida
        if not allow_overlap:
            for other in other_tables:
                if self.check_collision(table, other, spacing=self.spacing):
                    return False

        # Verifica limites da planta com espaço para cadeiras
        chair_space = 1.5
        if (table['x'] < 0 or 
            table['y'] < chair_space or 
            table['x'] + table['w'] > self.planta['largura'] or
            table['y'] + table['h'] > self.planta['altura'] - chair_space):
            return False

        return True
        
    def check_collision(self, rect1, rect2, spacing=0):
            """Verifica colisão entre dois retângulos"""
            return not (rect1['x'] + rect1['w'] + spacing <= rect2['x'] or
                    rect2['x'] + rect2['w'] + spacing <= rect1['x'] or
                    rect1['y'] + rect1['h'] + spacing <= rect2['y'] or
                    rect2['y'] + rect2['h'] + spacing <= rect1['y'])
    
    def calculate_distance(self, table1, table2):
            """Calcula distância entre duas mesas"""
            x1, y1 = table1['x'] + table1['w']/2, table1['y'] + table1['h']/2
            x2, y2 = table2['x'] + table2['w']/2, table2['y'] + table2['h']/2
            return ((x1 - x2)**2 + (y1 - y2)**2)**0.5