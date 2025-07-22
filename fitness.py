import json
import random
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Carregar a planta do escritório
with open("espaco_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

planta = config["planta"]
espaco = {
    "largura": planta["largura"],
    "altura": planta["altura"]
}
elementos = planta["elementos"]
regras = config["conectividades"]

# Geração de um indivíduo: posição aleatória para cada elemento
def gerar_individuo():
    while True:
        layout = {
            elem["id"]: {
                "x": random.randint(0, espaco["largura"] - elem["w"]),
                "y": random.randint(0, espaco["altura"] - elem["h"])
            }
            for elem in elementos
        }
        if layout_valido(layout):
            return layout

# Cálculo da distância Euclidiana
def distancia(p1, p2):
    return math.sqrt((p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2)

# Avaliação do fitness (distância total entre pares conectados)
def calcular_fitness(layout):
    penalidade = 0

    # Penalidade por distância (conectividade)
    for regra in regras:
        origem = layout[regra["de"]]
        destino = layout[regra["para"]]
        d = distancia(origem, destino)
        penalidade += regra.get("peso", 1.0) * d

    # Penalidade por sobreposição
    for i in range(len(elementos)):
        for j in range(i + 1, len(elementos)):
            elem1 = elementos[i]
            elem2 = elementos[j]
            pos1 = layout[elem1["id"]]
            pos2 = layout[elem2["id"]]

            if verificar_colisao(elem1, pos1, elem2, pos2):
                penalidade += 1000

    return penalidade



# Algoritmo genético básico
def executar_algoritmo_genetico(pop_size=30, geracoes=100, taxa_mutacao=0.1):
    populacao = [gerar_individuo() for _ in range(pop_size)]
    historico = []

    for _ in range(geracoes):
        populacao.sort(key=calcular_fitness)
        historico.append(calcular_fitness(populacao[0]))

        nova_populacao = populacao[:5]  # elitismo

        while len(nova_populacao) < pop_size:
            pai1, pai2 = random.sample(populacao[:15], 2)
            filho = crossover(pai1, pai2)
            if random.random() < taxa_mutacao:
                mutar(filho)
            nova_populacao.append(filho)

        populacao = nova_populacao

    return populacao[0], historico

# Crossover: média das posições
def crossover(p1, p2):
    return {
        k: {
            "x": int((p1[k]["x"] + p2[k]["x"]) / 2),
            "y": int((p1[k]["y"] + p2[k]["y"]) / 2)
        }
        for k in p1
    }

def get_element(id):
    return next(e for e in elementos if e["id"] == id)


# Mutação: move um item aleatoriamente
def mutar(layout):
    for _ in range(10):  # tenta até 10 vezes encontrar uma mutação válida
        item = random.choice(list(layout.keys()))
        novo_layout = layout.copy()
        novo_layout[item] = {
            "x": random.randint(0, espaco["largura"] - get_element(item)["w"]),
            "y": random.randint(0, espaco["altura"] - get_element(item)["h"])
        }
        if layout_valido(novo_layout):
            layout[item] = novo_layout[item]
            break


def plotar_layout(layout, elementos, largura_total, altura_total, titulo="Layout Otimizado"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, largura_total)
    ax.set_ylim(0, altura_total)
    ax.set_aspect('equal')
    ax.set_title(titulo)
    ax.grid(True, linestyle='--', alpha=0.3)

    for elem in elementos:
        id_elem = elem["id"]
        pos = layout[id_elem]
        largura = elem["w"]
        altura = elem["h"]
        tipo = elem["tipo"]

        # Escolhe cor por tipo
        cor = {
            "recepcao": "#f9e10d",
            "sala_reuniao": "#bcb4fd",
            "banheiro": "#f39bab",
            "mesa": "#cadb66"
        }.get(tipo, "#cccccc")

        # Desenha o retângulo
        ax.add_patch(Rectangle(
            (pos["x"], pos["y"]),
            largura,
            altura,
            facecolor=cor,
            edgecolor="black"
        ))
        # Texto centralizado
        ax.text(
            pos["x"] + largura / 2,
            pos["y"] + altura / 2,
            id_elem,
            ha="center",
            va="center",
            fontsize=8,
            color="black"
        )

    plt.xlabel("Largura")
    plt.ylabel("Altura")
    plt.tight_layout()
    plt.show()

def verificar_colisao(elem1, pos1, elem2, pos2):
    """Verifica se dois retângulos se sobrepõem"""
    return not (
        pos1["x"] + elem1["w"] <= pos2["x"] or  # elem1 à esquerda
        pos2["x"] + elem2["w"] <= pos1["x"] or  # elem2 à esquerda
        pos1["y"] + elem1["h"] <= pos2["y"] or  # elem1 abaixo
        pos2["y"] + elem2["h"] <= pos1["y"]     # elem2 abaixo
    )

def layout_valido(layout):
    for i in range(len(elementos)):
        for j in range(i + 1, len(elementos)):
            elem1 = elementos[i]
            elem2 = elementos[j]
            pos1 = layout[elem1["id"]]
            pos2 = layout[elem2["id"]]

            if verificar_colisao(elem1, pos1, elem2, pos2):
                return False
    return True
