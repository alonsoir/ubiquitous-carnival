from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Inicializar el modelo de embeddings
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Supongamos que tienes documentos extraídos con sus respectivos contextos
documents = [
    Document(
        page_content="Texto del PDF sobre ciencia.",
        metadata={
            "context": "ciencia",
            "document_type": "PDF",
            "creation_date": "2024-10-01",
            "author": "John Doe",
            "keywords": "biología, ecología, investigación",  # Convertido a cadena
        },
    ),
    Document(
        page_content="Texto del documento sobre ciencia.",
        metadata={
            "context": "ciencia",
            "document_type": "doc",
            "creation_date": "2024-10-01",
            "author": "John Doe",
            "keywords": "biología, ecología, investigación",  # Convertido a cadena
        },
    ),
    Document(
        page_content="Texto del PDF sobre tecnología.",
        metadata={
            "context": "tecnología",
            "document_type": "PDF",
            "creation_date": "2024-10-01",
            "author": "Jane Smith",
            "keywords": "innovación, desarrollo",  # Convertido a cadena
        },
    ),
    Document(
        page_content="Texto del PDF sobre salud.",
        metadata={
            "context": "salud",
            "document_type": "PDF",
            "creation_date": "2024-10-01",
            "author": "Alice Johnson",
            "keywords": "bienestar, medicina",  # Convertido a cadena
        },
    ),
]

# Crear el vector store y almacenar los documentos
vector_store = Chroma.from_documents(documents, embedding=embeddings_model)

query = "¿Qué información contiene el texto extraído?"
# Crear un filtro compuesto
filter_condition = {
    "$and": [
        {"context": "ciencia"},
        {"document_type": "doc"}
    ]
}
# # Filtrar solo por contexto
# results = vector_store.similarity_search(query, filter={"context": "ciencia"})
# Filtrar solo por tipo de documento
# results = vector_store.similarity_search(query, filter={"document_type": "doc"})

filter_condition_1 = {
    "$or": [
        {"context": "ciencia"},
        {"document_type": "doc"}
    ]
}

filter_condition_2 = {
        "author": "John Doe"
}

filter_condition_3 = {
    "$or": [
        {"author": "John Doe"},
        {"author": "Jane Smith"}
    ]
}

'''
filter_condition_4 = {
    "context": "tecnología",
    "creation_date": {"$gte": "2024-01-01", "$lt": "2024-10-01"}
}
'''
filter_condition_5 = {
    "keywords": {"$contains": "innovación"}
}

filter_condition_6 = {
    "author": {"$ne": "Alice Johnson"},
    "context": "ciencia"
}

filter_condition_7 = {
    "keywords": {"$contains": "investigación"},
    "document_type": {"$ne": "PDF"}
}

filter_condition_8 = {
    "$and": [
        {"keywords": {"$contains": "biología"}},
        {"keywords": {"$contains": "ecología"}}
    ]
}

filter_condition_9 = {
    "creation_date": {"$lt": "2024-10-01"}
}

filter_condition_10 = {
    "author": {"$contains": "John"},
    "context": "salud"
}

results = vector_store.similarity_search(query, filter=filter_condition)
for result in results:
    print(result.page_content)
    print(result.metadata)

results = vector_store.similarity_search(query, filter=filter_condition_1)
for result in results:
    print(result.page_content)
    print(result.metadata)

results = vector_store.similarity_search(query, filter=filter_condition_2)
for result in results:
    print(result.page_content)
    print(result.metadata)

results = vector_store.similarity_search(query, filter=filter_condition_3)
for result in results:
    print(result.page_content)
    print(result.metadata)
'''
results = vector_store.similarity_search(query, filter=filter_condition_4)
for result in results:
    print(result.page_content)
    print(result.metadata)
'''
results = vector_store.similarity_search(query, filter=filter_condition_5)
for result in results:
    print(result.page_content)
    print(result.metadata)

results = vector_store.similarity_search(query, filter=filter_condition_6)
for result in results:
    print(result.page_content)
    print(result.metadata)

results = vector_store.similarity_search(query, filter=filter_condition_7)
for result in results:
    print(result.page_content)
    print(result.metadata)

results = vector_store.similarity_search(query, filter=filter_condition_8)
for result in results:
    print(result.page_content)
    print(result.metadata)


results = vector_store.similarity_search(query, filter=filter_condition_9)
for result in results:
    print(result.page_content)
    print(result.metadata)


results = vector_store.similarity_search(query, filter=filter_condition_10)
for result in results:
    print(result.page_content)
    print(result.metadata)
# Ejemplo de cómo se usaría con ChromaDB (comentado para evitar errores si no está configurado)
# import chromadb
# client = chromadb.Client()
# collection = client.create_collection("my_collection")
# results = collection.query(
#     query_texts=["tu consulta aquí"],
#     where=filter_metadata_complex
# )

"""
ChromaDB no soporta características de indexacion avanzada como el uso de 
HNSW y/o IVFFlat. ChromaDB puede funcionar junto con FAISS que si soporta HNSW y IVFFlat.

Motores Vectoriales que Soportan HNSW e IVFFlat

1) pgvector:
Soporte: Activo para ambos índices.
Descripción: pgvector es una extensión de PostgreSQL que permite almacenar y buscar vectores utilizando técnicas de 
búsqueda de vecinos más cercanos. 
Se recomienda generalmente HNSW por su rendimiento y robustez ante cambios en los datos, mientras que IVFFlat es útil 
en casos específicos donde se requiere optimización en el tamaño del índice o el tiempo de construcción.

2) Faiss:
Soporte: Activo para HNSW y IVFFlat (también conocido como IVF).
Descripción: Faiss es una biblioteca desarrollada por Facebook AI Research para la búsqueda eficiente de vectores. 
Ofrece implementaciones altamente optimizadas de ambos algoritmos, permitiendo realizar búsquedas rápidas en grandes 
conjuntos de datos.

3) Annoy:
Soporte: Principalmente HNSW.
Descripción: Annoy (Approximate Nearest Neighbors Oh Yeah) es una biblioteca diseñada para realizar búsquedas rápidas de 
vecinos más cercanos. Aunque no implementa IVFFlat directamente, utiliza un enfoque similar basado en árboles 
aleatorios.

4) Milvus:
Soporte: Activo para ambos índices.
Descripción: Milvus es un motor de base de datos vectorial que permite realizar búsquedas eficientes utilizando varios 
algoritmos, incluyendo HNSW e IVFFlat. Es especialmente útil para aplicaciones de inteligencia artificial y aprendizaje 
automático.

5) Weaviate:
Soporte: HNSW.
Descripción: Weaviate es un motor de búsqueda semántica que utiliza HNSW para la búsqueda vectorial, aunque no se 
menciona específicamente el soporte para IVFFlat.

Consideraciones generales:

HNSW es preferido por su velocidad y eficiencia en la búsqueda, especialmente cuando se manejan datos dinámicos.
IVFFlat, aunque más lento en términos de construcción y mayor en uso de memoria, puede ser útil cuando se necesita un 
menor tamaño del índice y se trabaja con conjuntos de datos más estáticos.
"""
