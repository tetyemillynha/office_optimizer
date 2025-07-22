from fitness import executar_algoritmo_genetico
from fitness import plotar_layout
import json

# Carrega a planta e elementos
with open("espaco_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

planta = config["planta"]
elementos = planta["elementos"]
largura = planta["largura"]
altura = planta["altura"]

def main():
    melhor_layout, historico_fitness = executar_algoritmo_genetico()

    print("\n📐 Layout Otimizado:")
    for k, pos in melhor_layout.items():
        print(f"🔹 {k}: (x={pos['x']}, y={pos['y']})")

    print("\n📉 Histórico de fitness (primeiras gerações):")
    print(historico_fitness[:10])

    # Mostrar visualmente
    plotar_layout(melhor_layout, elementos, largura, altura)

if __name__ == "__main__":
    main()
