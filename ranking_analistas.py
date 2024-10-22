import logging
from dataclasses import dataclass
from typing import List

from serpapi import GoogleSearch

# Configura el logging para ver detalles de la ejecución
logging.basicConfig(level=logging.DEBUG)

@dataclass
class Analista:
    """Representa un analista con su expertise y enfoque específico"""
    nombre: str
    rol: str
    afiliacion: str
    descripcion: str
    especialidad: List[str]

def obtener_analistas_de_scholar(query: str, api_key: str, max_analistas: int = 5) -> List[Analista]:
    params = {
        "engine": "google_scholar_profiles",
        "mauthors": query,
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Extraer resultados
    profiles = results.get('profiles', [])
    analistas = []

    for profile in profiles[:max_analistas]:
        nombre = profile.get('name')
        afiliacion = profile.get('affiliations')
        descripcion = profile.get('description', "Sin descripción")
        rol = "Investigador"
        especialidad = ["Scholar"]

        analista = Analista(
            nombre=nombre,
            rol=rol,
            afiliacion=afiliacion,
            descripcion=descripcion,
            especialidad=especialidad
        )
        analistas.append(analista)

    return analistas

# Ejemplo de uso
if __name__ == "__main__":
    api_key = "368980b77ba0e570d2574b8a156677845246adad8182340c463f2c6293ea17c8"
    tema = "Natural Language Processing"

    analistas = obtener_analistas_de_scholar(tema, api_key)

    if analistas:
        for analista in analistas:
            print(f"Nombre: {analista.nombre}, Afiliación: {analista.afiliacion}")
    else:
        print("No se encontraron analistas.")