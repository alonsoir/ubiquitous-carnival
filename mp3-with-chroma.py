import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# Ruta al archivo MP3
mp3_path = "./speech.mp3"

# Extraer metadatos del MP3
audio = MP3(mp3_path, ID3=ID3)
title = audio.get('TIT2', 'Unknown Title')
artist = audio.get('TPE1', 'Unknown Artist')

# Crear un texto a partir de los metadatos
extracted_text = f"Title: {title}\nArtist: {artist}"

# Crear embeddings del texto extraído
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Crear un documento usando la clase Document
documents = [Document(page_content=extracted_text)]

# Crear el vector store y almacenar el texto
vector_store = Chroma.from_documents(documents, embedding=embeddings_model, persist_directory="./data/chroma_db")

# Realizar una consulta para recuperar información relevante
query = "¿Cuál es el título y el artista del audio?"
print(f"{query}\n")
results = vector_store.similarity_search(query)

# Mostrar los resultados recuperados
for result in results:
    print(result.page_content)  # Acceder al contenido de la página