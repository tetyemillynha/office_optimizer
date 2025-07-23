import pygame
import json
from core.genetics import GeneticAlgorithm
from core.layout import Layout
from core.utils import CHAIR_SPACE, COLORS, DEFAULT_SCALE, WINDOW_PADDING, get_chair_count_for_table

class OfficeLayoutVisualizer:
    def __init__(self, config_file):
        pygame.init()
        pygame.font.init()

        # Carrega a configuração
        with open(config_file) as f:
            self.config = json.load(f)
        
        self.planta = self.config['planta']
        self.fixed_elements = [elem for elem in self.planta['elementos'] if elem.get('fixo', False)]
        self.movable_tables = [elem for elem in self.planta['elementos'] if elem['tipo'] == 'mesa']

        self.max_generations = 1000  # Critério 1: Número máximo de gerações
        self.target_fitness = 500    # Critério 2: Fitness desejado
        self.stagnation_limit = 500  # Critério 3: Gerações
        
        # Parâmetros de visualização
        self.scale = DEFAULT_SCALE  # Escala para visualização (pixels por unidade)
        self.width = self.planta['largura'] * self.scale
        self.height = self.planta['altura'] * self.scale
        
        # Cores
        self.colors = COLORS
        
        # Parâmetros do algoritmo genético
        self.population_size = 30
        self.mutation_rate = 0.1
        self.spacing = 2

        # Configuração da janela
        self.screen = pygame.display.set_mode((self.width + WINDOW_PADDING, self.height))
        pygame.display.set_caption("Otimização de Layout com Algoritmo Genético")
        self.font = pygame.font.SysFont('Arial', 14)
        self.big_font = pygame.font.SysFont('Arial', 18, bold=True)

        # Inicialização do algoritmo genético e layout
        
        self.layout = Layout(
            planta=self.planta,
            fixed_elements=self.fixed_elements,
            movable_tables=self.movable_tables,
            spacing=self.spacing
        )
        
        # Parâmetros do algoritmo genético
        self.restricted_areas = self.layout.calculate_restricted_areas()

        self.genetic = GeneticAlgorithm(
            planta=self.planta,
            movable_tables=self.movable_tables,
            restricted_areas=self.restricted_areas,
            spacing=self.spacing,
            mutation_rate=self.mutation_rate,
            layout=self.layout,
            selection_method="roulette"
        )
        
        # Estado da simulação
        self.population = [self.genetic.create_individual() for _ in range(self.population_size)]
        self.generation = 0
        self.best_fitness = -float('inf')
        self.best_individual = None
        self.running = True
        self.paused = False
        self.show_info = True

        fitness_scores = [self.genetic.fitness(ind) for ind in self.genetic.population]
        self.genetic.best_individual = self.genetic.population[fitness_scores.index(max(fitness_scores))]
        self.genetic.best_fitness = max(fitness_scores)

        # Adicione estas linhas:
        self.best_individual = self.genetic.best_individual
        self.best_fitness = self.genetic.best_fitness



    def draw(self):
            """Desenha a visualização"""
            self.screen.fill(self.colors['background'])
            
            # Desenha elementos fixos
            for elem in self.fixed_elements:
                color = self.colors['wall'] if elem['tipo'] == 'parede' else \
                        self.colors['bathroom'] if elem['tipo'] == 'banheiro' else \
                        self.colors['restriction']
                
                pygame.draw.rect(
                    self.screen, color,
                    (elem['x'] * self.scale, elem['y'] * self.scale,
                    elem['w'] * self.scale, elem['h'] * self.scale)
                )
            
            # Desenha as mesas da melhor solução atual
            if self.best_individual:
                # if len(self.best_individual) > 1:
                #     self.best_individual[1]['x'] = self.best_individual[0]['x']
                #     self.best_individual[1]['y'] = self.best_individual[0]['y']

                for table in self.best_individual:
                    chair_space = CHAIR_SPACE
                    valid_position = (chair_space <= table['y'] and 
                                    table['y'] + table['h'] <= self.planta['altura'] - chair_space and
                                    0 <= table['x'] <= self.planta['largura'] - table['w'])
                    
                    color = self.colors['table_valid'] if valid_position else self.colors['table_invalid']
                    # color = self.colors['table_invalid']  # Sempre vermelho para simular erro visível

                    pygame.draw.rect(
                        self.screen, color,
                        (table['x'] * self.scale, table['y'] * self.scale,
                        table['w'] * self.scale, table['h'] * self.scale)
                    )
                    
                    # Desenha cadeiras se posição for válida
                    if valid_position:
                        chairs = get_chair_count_for_table(table['w'])
                        chair_radius = int(self.scale * 0.3)
                        
                        if chairs == 4:
                            positions = [
                                (table['x'] + table['w']/4, table['y'] - 0.5),
                                (table['x'] + 3*table['w']/4, table['y'] - 0.5),
                                (table['x'] + table['w']/4, table['y'] + table['h'] + 0.5),
                                (table['x'] + 3*table['w']/4, table['y'] + table['h'] + 0.5)
                            ]
                        else:
                            positions = [
                                (table['x'] + table['w']/3, table['y'] - 0.5),
                                (table['x'] + 2*table['w']/3, table['y'] + table['h'] + 0.5)
                            ]
                        
                        for cx, cy in positions:
                            pygame.draw.circle(
                                self.screen, self.colors['chair'],
                                (int((cx) * self.scale), int((cy) * self.scale)),
                                chair_radius
                            )
            
            # Painel de informações
            pygame.draw.rect(self.screen, (220, 220, 220), (self.width, 0, 300, self.height))
            
            info_y = 20
            texts = [
                f"Geração: {self.generation}",
                f"Melhor Fitness: {self.best_fitness:.2f}",
                "",
                "Controles:",
                "Espaço: Pausar/Continuar",
                "I: Mostrar/Ocultar Info",
                "R: Reiniciar",
                "ESC: Sair",
                "",
                "Legenda:",
                "Verde: Mesa válida",
                "Vermelho: Mesa inválida",
                "Azul: Banheiro",
                "Cinza: Área restrita"
            ]
            
            for text in texts:
                if text.startswith("Geração") or text.startswith("Melhor"):
                    rendered = self.big_font.render(text, True, self.colors['text'])
                else:
                    rendered = self.font.render(text, True, self.colors['text'])
                self.screen.blit(rendered, (self.width + 10, info_y))
                info_y += 20 if text else 10
            
            pygame.display.flip()
    