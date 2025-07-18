from alimentos import alimentos
from typing import List
CALORIAS_OBJETIVO = 2000
MACROS_OBJETIVO = {
    "carbo": 0.5,
    "proteina": 0.3,
    "gordura": 0.2
}

def calcular_total(dieta: List[int]):
    total = {
        "calorias": 0,
        "carbo": 0,
        "proteina": 0,
        "gordura": 0
    }

    for idx in dieta:
        alimento = alimentos[idx]
        total["calorias"] += alimento["calorias"]
        total["carbo"] += alimento["carbo"]
        total["proteina"] += alimento["proteina"]
        total["gordura"] += alimento["gordura"]
    return total

def calcular_fitness(dieta: List[int]):
    total = calcular_total(dieta)

    #calculo dos percentuais reais de macronutrientes
    cal_carbo = total["carbo"] * 4
    cal_proteina = total["proteina"] * 4
    cal_gordura = total["gordura"] * 9

    if total["calorias"] == 0:
        # dieta vazia, fitness ruim
        return float('inf')
    
    percentuais = {
        "carbo": cal_carbo / total["calorias"],
        "proteina": cal_proteina / total["calorias"],
        "gordura": cal_gordura / total["calorias"]
    }

    #penalidade por desvio calorico
    penalidade_desvio_calorico = ((total["calorias"] - CALORIAS_OBJETIVO) / CALORIAS_OBJETIVO) ** 2

    #penalidade por desvio dos percentuais de macronutrientes
    penalidade_macros = sum(
        (percentuais[m] - MACROS_OBJETIVO[m]) ** 2 for m in MACROS_OBJETIVO
    )
    
    return penalidade_desvio_calorico + penalidade_macros

