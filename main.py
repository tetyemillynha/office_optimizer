from fitness import calcular_fitness

import random
dieta_exemplo = [random.randint(0, 9) for _ in range(21)]

print("Fitness:", calcular_fitness(dieta_exemplo))
