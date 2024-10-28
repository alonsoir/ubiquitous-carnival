import os
import requests
from swarm import Agent
from swarm import Swarm
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

swarm_client = Swarm()

# Función para obtener la fecha actual en formato deseado
def get_current_date():
    return datetime.now().strftime("%d-%m-%Y")  # Formato: "28-10-2024"

# Solicitar al usuario la ciudad deseada
local_city = input("Introduce la ciudad para el noticiero (por defecto es Madrid): ") or "Madrid"

# Contexto local con fecha y ubicación automática
local_context = {
    "local_context": local_city,
    "todays_date": get_current_date()
}

def fetch_google_news(query):
    """Función para obtener noticias de SerpAPI"""
    api_key = os.getenv("SERPAPI_KEY")  # Asegúrate de tener tu clave API para SerpAPI
    url = f"https://serpapi.com/search.json?q={query}&api_key={api_key}&hl=es&gl=es"

    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("news_results", [])
        if articles:
            return "\n".join([f"{article['title']} - {article['snippet']}" for article in articles[:5]])  # Obtener los primeros 5 artículos
        else:
            return "No se encontraron noticias."
    else:
        return "No se pudo obtener la información de noticias."

def weather_tool(region: str):
    """Llama a esta herramienta cuando necesites saber sobre el clima en una región específica"""
    api_key = os.getenv("WEATHER_API_KEY")
    response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={region}&appid={api_key}&units=metric")
    
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        return f"El clima en {region} es de {temperature} grados C, con {weather_description}."
    else:
        return "No se pudo obtener la información del clima."

# Definición de agentes para cada sección de noticias
class LocalNewsAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Agente de Noticias Locales",
            instructions="Proporciona las últimas noticias locales.",
            functions=[fetch_google_news]
        )

class InternationalNewsAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Agente de Noticias Internacionales",
            instructions="Proporciona un resumen de las principales noticias internacionales.",
            functions=[fetch_google_news]
        )

class BusinessNewsAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Agente de Noticias de Negocios",
            instructions="Comenta sobre las últimas novedades en el ámbito empresarial.",
            functions=[fetch_google_news]
        )

class TechnologyNewsAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Agente de Noticias de Tecnología",
            instructions="Habla sobre los avances y noticias en tecnología.",
            functions=[fetch_google_news]
        )

class SportsNewsAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Agente de Noticias Deportivas",
            instructions="Informa sobre los eventos deportivos recientes.",
            functions=[fetch_google_news]
        )

class WeatherAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Agente del Tiempo",
            instructions="Proporciona información sobre el clima local.",
            functions=[weather_tool]
        )

# Generación del archivo .md y salida en pantalla
def generate_markdown_file(content):
    filename = f"news-{local_city}-{get_current_date()}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Archivo {filename} generado exitosamente.")

# Bucle principal para la transmisión
def main_loop():
    news_content = ""
    
    # Inicializar agentes
    local_agent = LocalNewsAgent()
    international_agent = InternationalNewsAgent()
    business_agent = BusinessNewsAgent()
    technology_agent = TechnologyNewsAgent()
    sports_agent = SportsNewsAgent()
    weather_agent = WeatherAgent()

    # Noticias Locales
    news_content += "# Noticias Locales\n"
    try:
        local_news_query = f"noticias locales en {local_city}"
        local_news_result = local_agent.run(messages=[{"role": "user", "content": local_news_query}])
        news_content += local_news_result + "\n\n"
        print(f"# Noticias Locales\n{local_news_result}\n")
    except Exception as e:
        news_content += "No se pudo obtener noticias locales.\n\n"
        print("No se pudo obtener noticias locales.\n")

    # Noticias Internacionales
    news_content += "# Noticias Internacionales\n"
    try:
        international_news_query = f"noticias internacionales sobre {local_city}"
        international_news_result = international_agent.run(messages=[{"role": "user", "content": international_news_query}])
        news_content += international_news_result + "\n\n"
        print(f"# Noticias Internacionales\n{international_news_result}\n")
    except Exception as e:
        news_content += "No se pudo obtener noticias internacionales.\n\n"
        print("No se pudo obtener noticias internacionales.\n")

    # Noticias de Negocios
    news_content += "# Noticias de Negocios\n"
    try:
        business_news_query = f"noticias de negocios en {local_city}"
        business_news_result = business_agent.run(messages=[{"role": "user", "content": business_news_query}])
        news_content += business_news_result + "\n\n"
        print(f"# Noticias de Negocios\n{business_news_result}\n")
    except Exception as e:
        news_content += "No se pudo obtener noticias de negocios.\n\n"
        print("No se pudo obtener noticias de negocios.\n")

    # Noticias de Tecnología
    news_content += "# Noticias de Tecnología\n"
    try:
        technology_news_query = f"noticias de tecnología en {local_city}"
        technology_news_result = technology_agent.run(messages=[{"role": "user", "content": technology_news_query}])
        news_content += technology_news_result + "\n\n"
        print(f"# Noticias de Tecnología\n{technology_news_result}\n")
    except Exception as e:
        news_content += "No se pudo obtener noticias de tecnología.\n\n"
        print("No se pudo obtener noticias de tecnología.\n")

    # Noticias Deportivas
    news_content += "# Noticias Deportivas\n"
    try:
        sports_news_query = f"noticias deportivas en {local_city}"
        sports_news_result = sports_agent.run(messages=[{"role": "user", "content": sports_news_query}])
        news_content += sports_news_result + "\n\n"
        print(f"# Noticias Deportivas\n{sports_news_result}\n")
    except Exception as e:
        news_content += "No se pudo obtener noticias deportivas.\n\n"
        print("No se pudo obtener noticias deportivas.\n")

    # Clima
    news_content += "# Clima\n"
    try:
        weather_info = weather_agent.run(messages=[{"role": "user", "content": f"¿Cuál es el clima en {local_city}?"}])
        news_content += weather_info + "\n\n"
        print(f"# Clima\n{weather_info}\n")
    except Exception as e:
        news_content += "No se pudo obtener información del clima.\n\n"
        print("No se pudo obtener información del clima.\n")

    generate_markdown_file(news_content)

if __name__ == "__main__":
    main_loop()