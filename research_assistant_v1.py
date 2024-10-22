from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum
import logging
import os
from datetime import datetime
import arxiv
from dotenv import load_dotenv
from serpapi import GoogleSearch
from pathlib import Path

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
    ARXIV = "arxiv"
    CODIGO = "codigo"


@dataclass
class Analista:
    nombre: str
    rol: str
    afiliacion: str
    descripcion: str
    especialidad: List[FuenteInformacion]


@dataclass
class Documento:
    contenido: str
    fuente: FuenteInformacion
    metadata: Dict[str, Any]
    fecha_obtencion: datetime


@dataclass
class SeccionInforme:
    titulo: str
    contenido: str
    fuentes: List[Documento]
    analista: Analista


class GestorArchivos:
    def __init__(self, directorio_base: str = "investigacion"):
        self.directorio_base = Path(directorio_base)
        self.directorio_base.mkdir(exist_ok=True)

    def guardar_seccion(self, seccion: SeccionInforme) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seccion_{seccion.analista.nombre}_{timestamp}.md"
        filepath = self.directorio_base / filename

        contenido = f"""# {seccion.titulo}

{seccion.contenido}

## Fuentes
{self._formatear_fuentes(seccion.fuentes)}

## Analista
- Nombre: {seccion.analista.nombre}
- Rol: {seccion.analista.rol}
- Afiliación: {seccion.analista.afiliacion}
"""

        filepath.write_text(contenido, encoding='utf-8')
        logger.info(f"Guardada sección en {filepath}")
        return filepath

    def _formatear_fuentes(self, fuentes: List[Documento]) -> str:
        resultado = []
        for doc in fuentes:
            if doc.fuente == FuenteInformacion.ARXIV:
                resultado.append(f"- ArXiv: {doc.metadata.get('title')} ({doc.metadata.get('url')})")
            elif doc.fuente == FuenteInformacion.WEB:
                resultado.append(f"- Web: {doc.metadata.get('url')}")
            elif doc.fuente == FuenteInformacion.WIKIPEDIA:
                resultado.append(f"- Wikipedia: {doc.metadata.get('title')}")
            elif doc.fuente == FuenteInformacion.CODIGO:
                resultado.append(f"- Código generado: {doc.metadata.get('descripcion')}")
        return "\n".join(resultado)


class BuscadorInformacion:
    def __init__(self):
        self.arxiv_client = arxiv.Client()

    async def buscar(self, query: str, fuente: FuenteInformacion) -> List[Documento]:
        logger.info(f"Buscando en {fuente.value}: {query}")
        if fuente == FuenteInformacion.WEB:
            return await self._buscar_web(query)
        elif fuente == FuenteInformacion.WIKIPEDIA:
            return await self._buscar_wikipedia(query)
        elif fuente == FuenteInformacion.ARXIV:
            return await self._buscar_arxiv(query)
        raise ValueError(f"Fuente no soportada: {fuente}")

    async def _buscar_web(self, query: str) -> List[Documento]:
        resultados = []  # Simulación
        return resultados

    async def _buscar_wikipedia(self, query: str) -> List[Documento]:
        # Simulación de búsqueda en Wikipedia
        return []

    async def _buscar_arxiv(self, query: str) -> List[Documento]:
        search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
        documentos = []
        for result in self.arxiv_client.results(search):
            doc = Documento(
                contenido=f"Título: {result.title}\nAutores: {', '.join([author.name for author in result.authors])}\nResumen: {result.summary}",
                fuente=FuenteInformacion.ARXIV,
                metadata={"title": result.title, "url": result.pdf_url,
                          "authors": [author.name for author in result.authors]},
                fecha_obtencion=datetime.now()
            )
            documentos.append(doc)
        return documentos


class AgenteInvestigacion:
    def __init__(self):
        self.api_key_serpapi = os.getenv("SERPAPI_KEY")
        self.buscador = BuscadorInformacion()
        self.gestor_archivos = GestorArchivos()

        if not self.api_key_serpapi:
            raise ValueError("API Key de SerpApi no configurada")

    async def investigar(self, tema: str, max_analistas: int = 3) -> None:
        logger.info(f"Iniciando investigación sobre: {tema}")
        analistas = await self._generar_analistas(tema, max_analistas)
        logger.info(f"Generados {len(analistas)} analistas")

        # Mostrar los detalles de los analistas generados
        self._mostrar_analistas(analistas)

        # Realizar investigación y generar informes para cada analista
        for analista in analistas:
            logger.info(f"Realizando investigación para: {analista.nombre}")
            documentos = await self.buscador.buscar(tema, FuenteInformacion.ARXIV)
            if documentos:
                seccion = SeccionInforme(
                    titulo=f"Informe sobre {tema}",
                    contenido=f"Informe generado para el analista {analista.nombre} sobre {tema}.",
                    fuentes=documentos,
                    analista=analista
                )
                self.gestor_archivos.guardar_seccion(seccion)
            else:
                logger.warning(f"No se encontraron documentos para {analista.nombre}.")

    async def _generar_analistas(self, tema: str, max_analistas: int) -> List[Analista]:
        logger.info(f"Buscando analistas reales para el tema: {tema}")
        params = {
            "engine": "google_scholar_profiles",
            "mauthors": tema,
            "api_key": self.api_key_serpapi
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            profiles = results.get('profiles', [])
            if not profiles:
                logger.warning("No se encontraron perfiles de analistas en Google Scholar.")
                return []

            analistas = []
            for profile in profiles[:max_analistas]:
                nombre = profile.get('name', 'Desconocido')
                afiliacion = profile.get('affiliations', 'Afiliación no disponible')
                descripcion = profile.get('description', 'Sin descripción')
                rol = "Investigador"
                especialidad = [FuenteInformacion.ARXIV]  # Ejemplo

                analista = Analista(
                    nombre=nombre,
                    rol=rol,
                    afiliacion=afiliacion,
                    descripcion=descripcion,
                    especialidad=especialidad
                )
                analistas.append(analista)

            return analistas

        except Exception as e:
            logger.error(f"Error al buscar analistas en SerpApi: {e}")
            return []

    def _mostrar_analistas(self, analistas: List[Analista]) -> None:
        for analista in analistas:
            print(f"\nAnalista: {analista.nombre}")
            print(f"Rol: {analista.rol}")
            print(f"Afiliación: {analista.afiliacion}")
            print(f"Descripción: {analista.descripcion}")
            print(f"Especialidades: {[esp.value for esp in analista.especialidad]}")


# Ejemplo de uso dentro del flujo normal del agente
async def main():
    agente = AgenteInvestigacion()
    tema = "Natural Language Processing"
    await agente.investigar(tema)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
