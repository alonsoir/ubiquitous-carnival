from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
import logging
import os
from datetime import datetime
from serpapi import GoogleSearch  # Para usar SerpApi
from dotenv import load_dotenv
import aiofiles

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('research_agent.log')
    ]
)
logger = logging.getLogger(__name__)

class FuenteInformacion(Enum):
    WEB = "web"
    WIKIPEDIA = "wikipedia"
    LINKEDIN = "linkedin"
    ARXIV = "arxiv"

@dataclass
class Analista:
    nombre: str
    rol: str
    afiliacion: str
    descripcion: str
    especialidad: List[FuenteInformacion]
    puntuacion: int  # Puntuación ajustada a int

@dataclass
class Documento:
    """Representa un documento recuperado de cualquier fuente"""
    contenido: str
    fuente: FuenteInformacion
    metadata: Dict[str, Any]
    fecha_obtencion: datetime


class BuscadorInformacion:
    """Gestiona las búsquedas en diferentes fuentes"""

    def __init__(self):
        self.api_key_serpapi = os.getenv("SERPAPI_KEY")  # API Key de SerpApi

    async def buscar(self, query: str, fuente: FuenteInformacion, max_chars: int) -> List[Documento]:
        """Realiza búsquedas en la fuente especificada"""
        logger.info(f"Buscando en {fuente.value}: {query}")

        if fuente == FuenteInformacion.WEB:
            return await self._buscar_web(query, max_chars)
        elif fuente == FuenteInformacion.WIKIPEDIA:
            return await self._buscar_wikipedia(query, max_chars)
        elif fuente == FuenteInformacion.LINKEDIN:
            return await self._buscar_linkedin(query, max_chars)
        elif fuente == FuenteInformacion.ARXIV:
            return await self._buscar_arxiv(query, max_chars)

        raise ValueError(f"Fuente no soportada: {fuente}")

    async def _buscar_web(self, query: str, max_chars: int) -> List[Documento]:
        """Realiza búsquedas web en SerpApi"""
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key_serpapi
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        snippets = results.get('organic_results', [])

        return [
            Documento(
                contenido=snippet.get("snippet", "")[:max_chars],
                fuente=FuenteInformacion.WEB,
                metadata={"url": snippet.get("link")},
                fecha_obtencion=datetime.now()
            )
            for snippet in snippets
        ]

    async def _buscar_wikipedia(self, query: str, max_chars: int) -> List[Documento]:
        """Realiza búsquedas en Wikipedia"""
        params = {
            "engine": "wikipedia",
            "query": query,
            "api_key": self.api_key_serpapi
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        snippets = results.get('organic_results', [])

        return [
            Documento(
                contenido=snippet.get("snippet", "")[:max_chars],
                fuente=FuenteInformacion.WIKIPEDIA,
                metadata={"title": snippet.get("title")},
                fecha_obtencion=datetime.now()
            )
            for snippet in snippets
        ]

    async def _buscar_linkedin(self, query: str, max_chars: int) -> List[Documento]:
        """Realiza búsquedas en LinkedIn"""
        params = {
            "engine": "linkedin",
            "q": query,
            "api_key": self.api_key_serpapi
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        profiles = results.get('profiles', [])

        return [
            Documento(
                contenido=profile.get("snippet", "")[:max_chars],
                fuente=FuenteInformacion.LINKEDIN,
                metadata={"url": profile.get("link")},
                fecha_obtencion=datetime.now()
            )
            for profile in profiles
        ]

    async def _buscar_arxiv(self, query: str, max_chars: int) -> List[Documento]:
        """Realiza búsquedas en ArXiv"""
        params = {
            "engine": "arxiv",
            "q": query,
            "api_key": self.api_key_serpapi
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        papers = results.get('papers', [])

        return [
            Documento(
                contenido=paper.get("abstract", "")[:max_chars],
                fuente=FuenteInformacion.ARXIV,
                metadata={"title": paper.get("title"), "url": paper.get("link")},
                fecha_obtencion=datetime.now()
            )
            for paper in papers
        ]

    async def guardar_md(self, documentos: List[Documento], analista: Analista):
        """Genera y guarda un archivo Markdown (.md) para cada analista con la información de los documentos"""
        filename = f"{analista.nombre.replace(' ', '_')}_resumen.md"
        async with aiofiles.open(filename, mode='w') as f:
            await f.write(f"# Informe de investigación para {analista.nombre}\n\n")
            await f.write(f"**Rol**: {analista.rol}\n")
            await f.write(f"**Afiliación**: {analista.afiliacion}\n")
            await f.write(f"**Descripción**: {analista.descripcion}\n\n")
            await f.write("## Documentos:\n\n")

            for doc in documentos:
                await f.write(f"### Fuente: {doc.fuente.value.capitalize()}\n")
                await f.write(f"**Fecha de obtención**: {doc.fecha_obtencion}\n")
                await f.write(f"**Contenido**:\n{doc.contenido}\n\n")
                await f.write(f"**Metadata**: {doc.metadata}\n\n")

        logger.info(f"Archivo .md generado para {analista.nombre}: {filename}")


class AgenteInvestigacion:
    def __init__(self):
        self.buscador = BuscadorInformacion()
        self.api_key_serpapi = os.getenv("SERPAPI_KEY")

    async def investigar(self, tema: str, max_analistas: int = 3, max_chars: int = 1000) -> List[Analista]:
        logger.info(f"Iniciando investigación sobre: {tema}")

        # 1. Generar analistas reales
        analistas = await self._generar_analistas(tema, max_analistas)
        logger.info(f"Generados {len(analistas)} analistas")

        for analista in analistas:
            # 2. Realizar búsqueda en la web, Wikipedia, LinkedIn y ArXiv para cada analista
            documentos = await self.buscador.buscar(tema, FuenteInformacion.WEB, max_chars)
            documentos += await self.buscador.buscar(tema, FuenteInformacion.WIKIPEDIA, max_chars)
            documentos += await self.buscador.buscar(tema, FuenteInformacion.LINKEDIN, max_chars)
            documentos += await self.buscador.buscar(tema, FuenteInformacion.ARXIV, max_chars)

            # Guardar los documentos en un archivo .md
            await self.buscador.guardar_md(documentos, analista)

        return analistas

    async def _generar_analistas(self, tema: str, max_analistas: int) -> List[Analista]:
        """Genera analistas reales usando Google Scholar a través de SerpApi"""
        logger.info(f"Buscando analistas reales para el tema: {tema}")
        params = {
            "engine": "google_scholar_profiles",
            "mauthors": tema,
            "api_key": self.api_key_serpapi
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        profiles = results.get('profiles', [])
        analistas = []

        for profile in profiles[:max_analistas]:
            nombre = profile.get('name', 'Desconocido')
            afiliacion = profile.get('affiliations', 'Afiliación no disponible')
            descripcion = profile.get('description', 'Sin descripción')
            puntuacion = profile.get('cited_by', 0)  # Manejar cited_by como entero directamente
            rol = "Investigador"
            especialidad = [FuenteInformacion.WEB, FuenteInformacion.WIKIPEDIA, FuenteInformacion.LINKEDIN, FuenteInformacion.ARXIV]

            analista = Analista(
                nombre=nombre,
                rol=rol,
                afiliacion=afiliacion,
                descripcion=descripcion,
                especialidad=especialidad,
                puntuacion=puntuacion
            )
            analistas.append(analista)

        if not analistas:
            logger.warning("No se encontraron analistas en Scholar para este tema.")
        return analistas


# Ejemplo de uso dentro del flujo normal del agente
async def main():
    agente = AgenteInvestigacion()
    tema = "Natural Language Processing"
    max_analistas = 5  # Especificar número de analistas
    max_chars = 500  # Especificar el número de caracteres para la salida
    informe = await agente.investigar(tema, max_analistas=max_analistas, max_chars=max_chars)
    print(f"Investigación completada para {len(informe)} analistas.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
