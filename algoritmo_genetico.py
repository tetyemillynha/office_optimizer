import random
from fitness import calcular_fitness

TAMANHO_POPULACAO = 100
TAMANHO_DIETA = 21
NUMERO_ALIMENTOS = 10
NUMERO_GERACOES = 100
TAXA_MUTACAO = 0.01
TAMANHO_TORNEIO = 2

def gerar_populacao_inicial():
    return [random.randint(0, NUMERO_ALIMENTOS - 1) for _ in range(TAMANHO_DIETA)]



