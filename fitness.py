from alimentos import alimentos

CALORIAS_OBJETIVO = 2000

def calcular_calorias(alimento):
    return alimento["calorias"]

def calcular_macros(alimento):
    return {
        "carbo": alimento["carbo"],
        "proteina": alimento["proteina"],
        "gordura": alimento["gordura"]
    }

