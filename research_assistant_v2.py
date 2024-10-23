import requests
from arxiv import Client, Search, SortOrder
from dotenv import load_dotenv
from openai import OpenAI  # Reemplaza con la librería que uses para LLM
import os
from serpapi import GoogleSearch
from datetime import datetime

load_dotenv()


def search_scholars(topic, num_agents=5):
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        print("Error: No se encontró la clave de API de SerpApi. Verifica tu archivo .env.")
        return []

    params = {
        "engine": "google_scholar",
        "q": topic,
        "num": num_agents,
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    if 'organic_results' not in results:
        print(f"No se encontraron resultados 'organic_results' en la respuesta: {results}")
        return []

    agents = []
    for result in results['organic_results'][:num_agents]:  # Obtener los más relevantes
        authors_info = result.get('publication_info', {}).get('authors', [])

        # Manejar la estructura de autores
        authors = []
        for author in authors_info:
            # Verifica si los nombres están en la estructura y úsalos
            if 'name' in author:
                authors.append(author['name'])  # Usa el nombre completo si está disponible
            else:
                # Si no hay 'name', imprime un mensaje de advertencia
                print("Advertencia: No se encontró el nombre completo del autor en:", author)

        agents.append({
            'title': result.get('title'),
            'authors': authors,
            'link': result.get('link'),
            'publication_info': result.get('publication_info', {}).get('summary', 'No disponible')
        })

    for agent in agents:
        print(f"## {agent['title']}\n")
        print(f"**Autores**: {', '.join(agent['authors']) if agent['authors'] else 'No disponible'}\n")
        print(f"**Enlace**: [{agent['link']}]({agent['link']})\n")
        print(f"**Resumen de Publicación**: {agent['publication_info']}\n\n")

    # Formatear la información y guardar en un archivo
    output_dir = 'agents'
    os.makedirs(output_dir, exist_ok=True)
    fecha = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(output_dir, f"agents-{topic.replace(' ', '_')}-{fecha}.md")

    with open(file_path, 'w') as f:
        f.write(f"# Agentes para el tema: {topic}\n\n")
        for agent in agents:
            f.write(f"## {agent['title']}\n")
            f.write(f"**Autores**: {', '.join(agent['authors']) if agent['authors'] else 'No disponible'}\n")
            f.write(f"**Enlace**: [{agent['link']}]({agent['link']})\n")
            f.write(f"**Resumen de Publicación**: {agent['publication_info']}\n\n")

    print(f"Información guardada en {file_path}")
    return agents


from arxiv import Client, Search, SortOrder


def search_arxiv(author_name):
    print(f"Buscando publicaciones de {author_name} en ArXiv...")
    try:
        client = Client()
        search = Search(
            query=f'au:"{author_name}"',
            max_results=5,
            sort_by=SortOrder.Ascending
        )
        results = client.results(search)  # Usa Client para obtener resultados
        papers = list(results)  # Convierte el resultado a una lista
        print(f"Se encontraron {len(papers)} publicaciones para {author_name}.")

        if not papers:
            print(f"No se encontraron publicaciones para {author_name}.")
            return []

        pdf_metadata = []
        for paper in papers:
            # Verificar si el paper tiene un enlace al PDF
            if paper.pdf_url:
                pdf_metadata.append({
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'pdf_url': paper.pdf_url,
                    'published': paper.published,
                    'summary': paper.summary
                })

        if pdf_metadata:
            print(f"Se encontraron {len(pdf_metadata)} publicaciones en PDF para {author_name}.")
            for metadata in pdf_metadata:
                print(f"Título: {metadata['title']}")
                print(f"Autores: {', '.join(metadata['authors'])}")
                print(f"URL PDF: {metadata['pdf_url']}")
                print(f"Publicado el: {metadata['published']}")
                print(f"Resumen: {metadata['summary']}\n")
        else:
            print(f"No se encontraron publicaciones en PDF para {author_name}.")

        return pdf_metadata

    except Exception as e:
        print(f"Error al buscar publicaciones de {author_name}: {e}")
        return []


def summarize_pdf(pdf_path):
    # Usa el modelo LLM para resumir el PDF
    with open(pdf_path, 'rb') as f:
        content = f.read()
    # Llama al modelo LLM (OpenAI, por ejemplo)
    summary = OpenAI.summarize(content)
    return summary

def search_linkedin(agent_name):
    # Aquí puedes hacer scraping o usar una API
    # Devuelve la información relevante sobre el agente
    pass

def save_agent_info(agent, arxiv_results, linkedin_info, output_dir):
    file_path = os.path.join(output_dir, f"{agent['title']}.md")
    with open(file_path, 'w') as f:
        f.write(f"# {agent['title']}\n\n")
        f.write(f"**Autores**: {', '.join(agent['authors'])}\n")
        f.write(f"**Enlace**: {agent['link']}\n\n")
        f.write(f"**Resumen de Publicación**: {agent['publication_info']}\n\n")
        f.write("## Resúmenes de Papers:\n")
        for paper in arxiv_results:
            f.write(f"### {paper.title}\n")
            f.write(f"{paper.summary}\n\n")
    print(f"Información guardada en {file_path}")

def main(topic):
    output_dir = 'resumenes'
    os.makedirs(output_dir, exist_ok=True)

    agents = search_scholars(topic)

    if not agents:
        print(f"No se encontraron agentes para el tema: {topic}")
        return

    for agent in agents:
        print(f"Procesando {agent['title']}...")

        for author_name in agent['authors']:
            arxiv_results = search_arxiv(author_name)

            for paper in arxiv_results:
                pdf_path = paper.pdf_url
                response = requests.get(pdf_path)
                pdf_file = os.path.join(output_dir, f"{author_name}_{paper.title}.pdf")
                with open(pdf_file, 'wb') as f:
                    f.write(response.content)

                summary = summarize_pdf(pdf_file)

            linkedin_info = search_linkedin(author_name)
            save_agent_info(agent, arxiv_results, linkedin_info, output_dir)

if __name__ == "__main__":
    topic = "machine learning in healthcare"
    main(topic)
