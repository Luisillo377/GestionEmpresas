import json
import requests
from datetime import datetime

class Mindicador:
    def __init__(self, indicador_data):
        self.codigo = indicador_data.get("codigo")
        self.nombre = indicador_data.get("nombre")
        self.unidad_medida = indicador_data.get("unidad_medida")
        self.fecha = indicador_data.get("fecha")
        self.valor = indicador_data.get("valor")


def obtener_indicadores():
    url = "https://mindicador.cl/api"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error si la respuesta no es 200
        data = json.loads(response.text.encode('utf-8'))
        
        indicadores = {}
        for key, value in data.items():
            if isinstance(value, dict) and "codigo" in value:
                indicadores[key] = Mindicador(value)
        
        return indicadores
    except requests.RequestException as e:
        print(f"Error al obtener los indicadores: {e}")
        return {}