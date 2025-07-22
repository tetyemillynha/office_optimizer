import pygame
import random
import json
import sys
from pygame import gfxdraw

# Inicialização do Pygame
pygame.init()
class OfficeLayoutVisualizer:
    def __init__(self, config_file):
        # Carrega a configuração
        with open(config_file) as f:
            self.config = json.load(f)
        
        self.planta = self.config['planta']
        self.fixed_elements = [elem for elem in self.planta['elementos'] if elem.get('fixo', False)]
        self.movable_tables = [elem for elem in self.planta['elementos'] if elem['tipo'] == 'mesa']

        self.max_generations = 1000  # Critério 1: Número máximo de gerações
        self.target_fitness = 500    # Critério 2: Fitness desejado
        self.stagnation_limit = 500  # Critério 3: Gerações sem melhoria
        
        # Parâmetros de visualização
        self.scale = 15  # Escala para visualização (pixels por unidade)
        self.width = self.planta['largura'] * self.scale
        self.height = self.planta['altura'] * self.scale
        
        # Cores
        self.colors = {
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
        
        # Configuração da janela
        self.screen = pygame.display.set_mode((self.width + 300, self.height))
        pygame.display.set_caption("Otimização de Layout com Algoritmo Genético")
        self.font = pygame.font.SysFont('Arial', 14)
        self.big_font = pygame.font.SysFont('Arial', 18, bold=True)
        
        # Parâmetros do algoritmo genético
        self.population_size = 30
        self.mutation_rate = 0.1
        self.spacing = 2
        self.restricted_areas = self.calculate_restricted_areas()
        
        # Estado da simulação
        self.population = [self.create_individual() for _ in range(self.population_size)]
        self.generation = 0
        self.best_fitness = -float('inf')
        self.best_individual = None
        self.running = True
        self.paused = False
        self.show_info = True
    
    def calculate_restricted_areas(self):
        """Calcula áreas restritas (paredes, banheiro, etc.)"""
        restricted = []
        for elem in self.fixed_elements:
            if elem['tipo'] in ['parede', 'banheiro', 'restricao']:
                restricted.append({
                    'x': elem['x'],
                    'y': elem['y'],
                    'w': elem['w'],
                    'h': elem['h']
                })
        return restricted
    
    def create_individual(self):
        """Cria um indivíduo (layout) aleatório"""
        individual = []
        for table in self.movable_tables:
            placed = False
            attempts = 0
            
            while not placed and attempts < 50:
                x = random.randint(0, self.planta['largura'] - table['w'])
                y = random.randint(0, self.planta['altura'] - table['h'])
                
                new_table = {
                    'id': table['id'],
                    'tipo': table['tipo'],
                    'w': table['w'],
                    'h': table['h'],
                    'x': x,
                    'y': y
                }
                
                if self.is_valid_position(new_table, individual):
                    individual.append(new_table)
                    placed = True
                
                attempts += 1
            
            if not placed:
                individual.append({
                    'id': table['id'],
                    'tipo': table['tipo'],
                    'w': table['w'],
                    'h': table['h'],
                    'x': -10,
                    'y': -10
                })
        
        return individual
    
    def is_valid_position(self, table, other_tables):
        """Verifica se a posição da mesa é válida"""
        # Verifica colisão com elementos fixos
        for area in self.restricted_areas:
            if self.check_collision(table, area):
                return False
        
        # Verifica colisão com outras mesas
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
    
    def fitness(self, individual):
        """Calcula o fitness de um layout"""
        score = 0
        invalid_count = 0
        collisions = 0
        chair_violations = 0
        chair_space = 1.5

        for i, table in enumerate(individual):
            if not (0 <= table['x'] <= self.planta['largura'] - table['w'] and
                    0 <= table['y'] <= self.planta['altura'] - table['h']):
                invalid_count += 1
                continue
            
            for area in self.restricted_areas:
                if self.check_collision(table, area):
                    invalid_count += 1
                    break
            
            for j in range(i+1, len(individual)):
                if self.check_collision(table, individual[j], spacing=self.spacing):
                    collisions += 1
            
            if table['y'] < chair_space or table['y'] + table['h'] > self.planta['altura'] - chair_space:
                chair_violations += 1

        if invalid_count > 0 or chair_violations > 0:
            penalty = (invalid_count * 100) + (chair_violations * 150) + (collisions * 50)
            return max(1 / (penalty + 1), 0.0001)
        
        chair_capacity = sum(4 if table['w'] == 20 else 2 for table in individual)
        min_distance = float('inf')
        total_distance = 0
        pair_count = 0
        
        for i in range(len(individual)):
            for j in range(i+1, len(individual)):
                dist = self.calculate_distance(individual[i], individual[j])
                if dist < min_distance:
                    min_distance = dist
                total_distance += dist
                pair_count += 1
        
        avg_distance = total_distance / pair_count if pair_count > 0 else 0
        
        center_x, center_y = self.planta['largura'] / 2, self.planta['altura'] / 2
        centrality = 0
        
        for table in individual:
            table_center_x = table['x'] + table['w'] / 2
            table_center_y = table['y'] + table['h'] / 2
            centrality += (1 / (1 + abs(table_center_x - center_x)) + 
                          1 / (1 + abs(table_center_y - center_y)))
        
        used_area = sum(table['w'] * table['h'] for table in individual)
        free_area = (self.planta['largura'] * self.planta['altura']) - used_area
        density_score = min(used_area / free_area, 3)
        
        score = (chair_capacity * 10 + 
                 min_distance * 3 + 
                 avg_distance * 1 + 
                 centrality * 2 + 
                 density_score * 5 + 
                 len(individual) * 2)
        
        if chair_violations == 0:
            score += 50
        
        return score
    
    def calculate_distance(self, table1, table2):
        """Calcula distância entre duas mesas"""
        x1, y1 = table1['x'] + table1['w']/2, table1['y'] + table1['h']/2
        x2, y2 = table2['x'] + table2['w']/2, table2['y'] + table2['h']/2
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    
    def selection(self, population, fitness_scores):
        """Seleção por torneio"""
        selected = []
        for _ in range(len(population)):
            candidates = random.sample(list(zip(population, fitness_scores)), 5)
            winner = max(candidates, key=lambda x: x[1])[0]
            selected.append(winner)
        return selected
    
    def crossover(self, parent1, parent2):
        """Crossover de ponto único"""
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    
    def mutate(self, individual):
        """Aplica mutação a um indivíduo"""
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                table = individual[i]
                
                if random.random() < 0.7:  # 70% de chance de mutação de posição
                    for _ in range(10):
                        new_x = random.randint(0, self.planta['largura'] - table['w'])
                        new_y = random.randint(0, self.planta['altura'] - table['h'])
                        
                        new_table = {
                            'id': table['id'],
                            'tipo': table['tipo'],
                            'w': table['w'],
                            'h': table['h'],
                            'x': new_x,
                            'y': new_y
                        }
                        
                        if self.is_valid_position(new_table, [t for j, t in enumerate(individual) if j != i]):
                            individual[i] = new_table
                            break
                else:  # 30% de chance de rotação
                    if table['w'] != table['h']:
                        new_table = {
                            'id': table['id'],
                            'tipo': table['tipo'],
                            'w': table['h'],
                            'h': table['w'],
                            'x': table['x'],
                            'y': table['y']
                        }
                        
                        if self.is_valid_position(new_table, [t for j, t in enumerate(individual) if j != i]):
                            individual[i] = new_table
        
        return individual
    
    def next_generation(self):
        """Gera a próxima geração"""
        fitness_scores = [self.fitness(ind) for ind in self.population]
        
        # Atualiza o melhor indivíduo
        current_best = max(fitness_scores)
        if current_best > self.best_fitness:
            self.best_fitness = current_best
            self.best_individual = self.population[fitness_scores.index(current_best)]
        
        # Seleção
        selected = self.selection(self.population, fitness_scores)
        
        # Crossover e mutação
        new_population = []
        for i in range(0, len(selected), 2):
            if i+1 < len(selected):
                parent1, parent2 = selected[i], selected[i+1]
                child1, child2 = self.crossover(parent1, parent2)
                new_population.extend([self.mutate(child1), self.mutate(child2)])
            else:
                new_population.append(self.mutate(selected[i]))
        
        self.population = new_population
        self.generation += 1

        # Verifica critérios de parada
        stop_reason = None
        if self.generation >= self.max_generations:
            stop_reason = f"Alcançou {self.max_generations} gerações"
        elif self.best_fitness >= self.target_fitness:
            stop_reason = f"Fitness alvo {self.target_fitness} alcançado"
        elif self.generation - self.last_improvement > self.stagnation_limit:
            stop_reason = f"Estagnou por {self.stagnation_limit} gerações"
            
        return stop_reason
    
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
            for table in self.best_individual:
                chair_space = 1.5
                valid_position = (chair_space <= table['y'] and 
                                 table['y'] + table['h'] <= self.planta['altura'] - chair_space and
                                0 <= table['x'] <= self.planta['largura'] - table['w'])
                
                color = self.colors['table_valid'] if valid_position else self.colors['table_invalid']
                
                pygame.draw.rect(
                    self.screen, color,
                    (table['x'] * self.scale, table['y'] * self.scale,
                     table['w'] * self.scale, table['h'] * self.scale)
                )
                
                # Desenha cadeiras se posição for válida
                if valid_position:
                    chairs = 4 if table['w'] == 20 else 2
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
    
    def run(self):
        """Loop principal com tratamento de erros robusto"""
        try:
            clock = pygame.time.Clock()
            self.last_improvement = 0
            
            while self.running:
                # 1. Processa eventos
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        self._handle_key_event(event)
                
                # 2. Atualização da simulação
                if not self.paused:
                    stop_reason = self.next_generation()
                    if stop_reason:
                        print(f"PARANDO: {stop_reason}")
                        self._handle_stop_condition(stop_reason)
                        break
                
                # 3. Renderização
                self.draw()
                pygame.display.flip()  # Atualiza a tela corretamente
                clock.tick(10)
        
        except Exception as e:
            print(f"ERRO: {str(e)}")
        finally:
            pygame.quit()

    def _handle_key_event(self, event):
        """Gerencia eventos de teclado"""
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_SPACE:
            self.paused = not self.paused
        elif event.key == pygame.K_r:
            self._reset_simulation()
        elif event.key == pygame.K_i:
            self.show_info = not self.show_info

    def _handle_stop_condition(self, stop_reason):
        """Mostra mensagem final e prepara para encerrar"""
        self.draw()
        self.draw_final_message(stop_reason)
        pygame.display.flip()  # Garante que a mensagem seja exibida
        pygame.time.wait(3000)  # Pausa por 3 segundos

    def _reset_simulation(self):
        """Reinicia completamente a simulação"""
        self.population = [self.create_individual() for _ in range(self.population_size)]
        self.generation = 0
        self.best_fitness = -float('inf')
        self.best_individual = None
        self.last_improvement = 0

    def draw_final_message(self, message):
        """Mostra mensagem quando o algoritmo termina"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Fundo semi-transparente
        
        text = self.big_font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width//2, self.height//2))
        
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
