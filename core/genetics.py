import random
import matplotlib.pyplot as plt
import os
class GeneticAlgorithm:
    def __init__(self, planta, movable_tables, restricted_areas, spacing, mutation_rate,
                 layout, population_size=30, max_generations=1000, target_fitness=500, stagnation_limit=500,
                 selection_method="rank"):
        self.planta = planta
        self.movable_tables = movable_tables
        self.restricted_areas = restricted_areas
        self.spacing = spacing
        self.mutation_rate = mutation_rate
        self.population_size = population_size
        self.max_generations = max_generations
        self.target_fitness = target_fitness
        self.stagnation_limit = stagnation_limit
        self.layout = layout
        self.selection_method = selection_method
        self.best_fitness = -float("inf")
        self.best_individual = None
        self.generation = 0
        self.last_improvement = 0
        self.fitness_history = []

        self.population = [self.create_individual() for _ in range(self.population_size)]

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
                    
                    if self.layout.is_valid_position(new_table, individual):
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
                    if self.layout.check_collision(table, area):
                        invalid_count += 1
                        break
                
                for j in range(i+1, len(individual)):
                    if self.layout.check_collision(table, individual[j], spacing=self.spacing):
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
                    dist = self.layout.calculate_distance(individual[i], individual[j])
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
    
    #outros metodos de seleção para testes
    def selection_tournament(self, population, fitness_scores, k=5):
        selected = []
        for _ in range(len(population)):
            candidates = random.sample(list(zip(population, fitness_scores)), k)
            winner = max(candidates, key=lambda x: x[1])[0]
            selected.append(winner)
        return selected

    def selection_roulette(self, population, fitness_scores):
        total_fitness = sum(fitness_scores)
        if total_fitness == 0:
            fitness_scores = [1 for _ in fitness_scores]
            total_fitness = sum(fitness_scores)
        probs = [f / total_fitness for f in fitness_scores]
        return random.choices(population, weights=probs, k=len(population))

    def selection_rank(self, population, fitness_scores):
        ranked = sorted(zip(population, fitness_scores), key=lambda x: x[1])
        ranks = list(range(1, len(population)+1))
        probs = [r / sum(ranks) for r in ranks]
        return random.choices([ind for ind, _ in ranked], weights=probs, k=len(population))


    def selection(self, population, fitness_scores):
        if self.selection_method == "tournament":
            return self.selection_tournament(population, fitness_scores)
        elif self.selection_method == "roulette":
            return self.selection_roulette(population, fitness_scores)
        elif self.selection_method == "rank":
            return self.selection_rank(population, fitness_scores)
        else:
            raise ValueError(f"Método de seleção desconhecido: {self.selection_method}")

        
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
                            
                            if self.layout.is_valid_position(new_table, [t for j, t in enumerate(individual) if j != i]):
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
                            
                            if self.layout.is_valid_position(new_table, [t for j, t in enumerate(individual) if j != i]):
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
                stop_reason = f"Finalizou com {self.stagnation_limit} gerações"
            
            self.fitness_history.append(current_best)
                
            return stop_reason
    
    def save_fitness_plot(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.fitness_history, label='Melhor Fitness')
        plt.title(f'Evolução do Fitness - Método: {self.selection_method}')
        plt.xlabel('Gerações')
        plt.ylabel('Fitness')
        plt.legend()
        plt.grid(True)


        filename = f"docs/fitness_plot_{self.selection_method}.png"

        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Salva o gráfico
        plt.savefig(filename)
        plt.close()