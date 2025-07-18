from alimentos import alimentos

CALORIAS_OBJETIVO = 2000
MACROS_OBJETIVO = {
    "carbo": 0.5,
    "proteina": 0.3,
    "gordura": 0.2
}

def calcular_total_calorias(alimentos):
    total = {
        "calorias": 0,
        "carbo": 0,
        "proteina": 0,
        "gordura": 0
    }

    for alimento in alimentos:
        total["calorias"] += alimento["calorias"]
        total["carbo"] += alimento["carbo"]
        total["proteina"] += alimento["proteina"]
        total["gordura"] += alimento["gordura"]
    return total

def calcular_calorias(alimento):
    return alimento["calorias"]

def calcular_macros(alimento):
    return {
        "carbo": alimento["carbo"],
        "proteina": alimento["proteina"],
        "gordura": alimento["gordura"]
    }

