from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Definir parámetros
MODEL = "gpt-4"  # Usa "gpt-4" o "gpt-4-turbo" para optimización de tokens
MAX_TOKENS_PER_CHUNK = 3000  # Límite de tokens por sección, ajustado para evitar errores
SUMMARY_TOKEN_LIMIT = 100  # Tokens para el resumen de cada sección


def summarize_section(text):
    """Genera un resumen breve de una sección de texto."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Resume este texto en 400 caracteres o menos."},
            {"role": "user", "content": text}
        ],
        max_tokens=SUMMARY_TOKEN_LIMIT,
        temperature=0.5
    )
    summary = response.choices[0].message.content
    return summary.strip()


def split_text(text, max_tokens):
    """Divide el texto en secciones según el límite de tokens."""
    tokens = text.split()  # Asume que cada palabra cuenta como un token aprox.
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk = " ".join(tokens[i:i + max_tokens])
        chunks.append(chunk)

    return chunks


def summarize_document(text):
    """Genera un resumen iterativo de un documento largo."""
    # Dividir el texto en secciones manejables
    sections = split_text(text, MAX_TOKENS_PER_CHUNK)

    # Resumir cada sección
    section_summaries = []
    for i, section in enumerate(sections):
        print(f"Resumiendo sección {i + 1}/{len(sections)}...")
        summary = summarize_section(section)
        section_summaries.append(summary)

    # Combinar resúmenes de secciones y resumir el resultado
    combined_summary_text = " ".join(section_summaries)
    print("Generando el resumen final...")
    final_summary = summarize_section(combined_summary_text)

    return final_summary


def download_text_from_gutenberg(url):
    """Descarga el texto completo desde una URL de Proyecto Gutenberg."""
    print(f"Descargando texto from {url}...")
    response = requests.get(url)
    response.raise_for_status()

    # Limpiar el texto para eliminar cabecera y pie de página de Proyecto Gutenberg
    text = response.text

    return text


# Descargar "Moby Dick" de Proyecto Gutenberg
url = "https://www.gutenberg.org/files/2701/2701-0.txt"
texto_largo = download_text_from_gutenberg(url)

# Ejecutar el resumen del documento
resumen_final = summarize_document(texto_largo)
print("Resumen final:")
print(resumen_final)