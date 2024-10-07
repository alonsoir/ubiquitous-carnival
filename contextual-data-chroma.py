from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# Inicializar el modelo de embeddings
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Supongamos que tienes documentos extraídos con sus respectivos contextos
documents = [
    Document(page_content="Texto del PDF sobre ciencia.", metadata={
        "context": "ciencia",
        "document_type": "PDF",
        "creation_date": "2024-10-01",
        "author": "John Doe",
        "keywords": "biología, ecología, investigación"  # Convertido a cadena
    }),
    Document(page_content="Texto del PDF sobre tecnología.", metadata={
        "context": "tecnología",
        "document_type": "PDF",
        "creation_date": "2024-10-01",
        "author": "Jane Smith",
        "keywords": "innovación, desarrollo"  # Convertido a cadena
    }),
    Document(page_content="Texto del PDF sobre salud.", metadata={
        "context": "salud",
        "document_type": "PDF",
        "creation_date": "2024-10-01",
        "author": "Alice Johnson",
        "keywords": "bienestar, medicina"  # Convertido a cadena
    })
]

# Crear el vector store y almacenar los documentos
vector_store = Chroma.from_documents(documents, embedding=embeddings_model)

query = "¿Qué información contiene el texto extraído?"
results = vector_store.similarity_search(query)

# Filtrar resultados por contexto
filtered_results = [result for result in results if result.metadata["context"] == "ciencia"]

# Mostrar resultados filtrados
for result in filtered_results:
    print(result.page_content)