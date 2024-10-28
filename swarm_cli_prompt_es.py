import os
import requests
from typing import Optional, List, Dict
from dataclasses import dataclass
from swarm import Agent, Swarm
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from abc import ABC, abstractmethod
import urllib.parse  # Para codificar el query

# Crear el directorio de logs si no existe
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configuración del logging
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Formato para los logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo
    log_file = log_dir / f"news_aggregator_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

@dataclass
class NewsArticle:
    title: str
    snippet: str
    source: str
    
@dataclass
class WeatherInfo:
    temperature: float
    description: str
    region: str

class NewsService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def fetch_news(self, query: str, limit: int = 5) -> List[NewsArticle]:
        """Obtiene noticias desde SerpAPI con manejo de errores mejorado"""
        try:
            encoded_query = urllib.parse.quote(query)  # Codificar query para URL
            url = (
                "https://serpapi.com/search.json"
                f"?q={encoded_query}&api_key={self.api_key}&hl=es&gl=es"
            )
            logger.info(f"Generated query URL: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            articles = response.json().get("news_results", [])
            logger.debug(f"Fetched {len(articles)} articles for query: {query}")
            return [
                NewsArticle(
                    title=article['title'],
                    snippet=article['snippet'],
                    source=article.get('source', 'Desconocido')
                )
                for article in articles[:limit]
            ]
        except requests.RequestException as e:
            logger.error(f"Error fetching news: {str(e)}", exc_info=True)
            return []

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_weather(self, region: str) -> Optional[WeatherInfo]:
        """Obtiene información del clima con manejo de errores mejorado"""
        try:
            url = (
                "http://api.openweathermap.org/data/2.5/weather"
                f"?q={region}&appid={self.api_key}&units=metric"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Fetched weather data for region: {region}")
            return WeatherInfo(
                temperature=data['main']['temp'],
                description=data['weather'][0]['description'],
                region=region
            )
        except requests.RequestException as e:
            logger.error(f"Error fetching weather: {str(e)}", exc_info=True)
            return None

class BaseNewsAgent(Agent):
    def __init__(self, name: str, instructions: str):
        super().__init__(name=name, instructions=instructions, functions=[self.fetch_news])
        logger.debug(f"Initialized {name} agent")

    def fetch_news(self, query: str, news_service: NewsService) -> str:
        logger.info(f"Executing query: '{query}'")
        articles = news_service.fetch_news(query)
        if not articles:
            return "No se encontraron noticias."
            
        return "\n\n".join(
            f"**{article.title}**\n{article.snippet}\n*Fuente: {article.source}*"
            for article in articles
        )

class LocalNewsAgent(BaseNewsAgent):
    def __init__(self):
        super().__init__(name="Local News Agent", instructions="Fetch local news")

class InternationalNewsAgent(BaseNewsAgent):
    def __init__(self):
        super().__init__(name="International News Agent", instructions="Fetch international news")

class BusinessNewsAgent(BaseNewsAgent):
    def __init__(self):
        super().__init__(name="Business News Agent", instructions="Fetch business news")

class TechnologyNewsAgent(BaseNewsAgent):
    def __init__(self):
        super().__init__(name="Technology News Agent", instructions="Fetch technology news")

class SportsNewsAgent(BaseNewsAgent):
    def __init__(self):
        super().__init__(name="Sports News Agent", instructions="Fetch sports news")

class NewsAggregator:
    def __init__(self, city: str):
        load_dotenv()
        logger.info(f"Initializing NewsAggregator for city: {city}")
        
        serpapi_key = os.getenv("SERPAPI_KEY")
        weather_api_key = os.getenv("WEATHER_API_KEY")
        
        if not serpapi_key or not weather_api_key:
            logger.error("Missing required API keys in environment variables")
            raise ValueError("Missing required API keys")
        
        self.city = city
        self.news_service = NewsService(serpapi_key)
        self.weather_service = WeatherService(weather_api_key)
        
        # Inicializar agentes sin guardar news_service en el objeto del agente
        self.agents = {
            "locales": LocalNewsAgent(),
            "internacionales": InternationalNewsAgent(),
            "negocios": BusinessNewsAgent(),
            "tecnología": TechnologyNewsAgent(),
            "deportes": SportsNewsAgent()
        }
        logger.debug("All news agents initialized successfully")

    def generate_report(self) -> str:
        """Genera el reporte de noticias completo"""
        logger.info(f"Generating report for {self.city}")
        sections = []
        
        # Obtener clima
        weather = self.weather_service.get_weather(self.city)
        if weather:
            sections.append(
                f"# Clima\n"
                f"El clima en {weather.region} es de {weather.temperature:.1f}°C, "
                f"con {weather.description}.\n"
            )
            logger.info(f"Weather information added for {self.city}")
        else:
            logger.warning(f"Could not get weather information for {self.city}")
        
        # Obtener noticias por sección
        for section_name, agent in self.agents.items():
            try:
                query = f"noticias {section_name} en {self.city}"
                logger.info(f"Fetching news for section: {section_name}")
                content = agent.fetch_news(query, news_service=self.news_service)
                sections.append(f"# Noticias {section_name.title()}\n{content}\n")
                logger.info(f"Successfully added content for section: {section_name}")
            except Exception as e:
                logger.error(f"Error getting {section_name} news: {str(e)}", exc_info=True)
                sections.append(f"# Noticias {section_name.title()}\n"
                              f"No se pudieron obtener las noticias.\n")
        
        return "\n".join(sections)
        
    def save_report(self, content: str) -> Path:
        """Guarda el reporte en un archivo markdown"""
        date = datetime.now().strftime("%d-%m-%Y")
        filename = Path(f"news-{self.city}-{date}.md")
        
        try:
            filename.write_text(content, encoding='utf-8')
            logger.info(f"Report saved successfully to {filename}")
            return filename
        except IOError as e:
            logger.error(f"Error saving report: {str(e)}", exc_info=True)
            raise

def main():
    try:
        logger.info("Starting news aggregator application")
        city = input("Introduce la ciudad para el noticiero (por defecto es Madrid): ").strip() or "Madrid"
        logger.info(f"User selected city: {city}")
        
        aggregator = NewsAggregator(city)
        content = aggregator.generate_report()
        aggregator.save_report(content)
        print(content)
        logger.info("Application completed successfully")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)
        print("Ocurrió un error al generar el reporte. Revise los logs para más detalles.")

if __name__ == "__main__":
    main()
