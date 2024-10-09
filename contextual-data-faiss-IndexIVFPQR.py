from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss
import numpy as np
import time

# Inicializar el modelo de embeddings
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

# Crear menos documentos sintéticos
documents = []
topics = ["ciencia", "tecnología", "salud", "historia", "arte"]
for i in range(20):  # Reducimos a 20 documentos
    topic = topics[i % len(topics)]
    documents.append(Document(
        page_content=f"Breve texto sobre {topic} número {i + 1}.",
        metadata={
            "context": topic,
            "document_type": "PDF" if i % 2 == 0 else "doc",
            "creation_date": f"2024-{(i % 12) + 1:02d}-01",
        },
    ))

print(f"Creados {len(documents)} documentos.")

# Crear embeddings para los documentos en un solo lote
start_time = time.time()
embeddings = embeddings_model.embed_documents([doc.page_content for doc in documents])
embeddings = np.array(embeddings).astype('float32')
print(f"Tiempo para crear embeddings: {time.time() - start_time:.2f} segundos")

# Crear el índice FAISS usando IndexFlatL2 para simplicidad y rapidez
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)

# Añadir los embeddings al índice FAISS
start_time = time.time()
index.add(embeddings)
print(f"Tiempo para añadir al índice: {time.time() - start_time:.2f} segundos")

# Crear el docstore y el mapeo de índices
docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(documents)})
index_to_id = {i: str(i) for i in range(len(documents))}

# Crear el vector store usando FAISS
vector_store = FAISS(
    embedding_function=embeddings_model,
    index=index,
    docstore=docstore,
    index_to_docstore_id=index_to_id
)

# Realizar búsquedas
queries = [
    "Información sobre ciencia",
    "Avances tecnológicos recientes",
    "Consejos de salud"
]

for query in queries:
    start_time = time.time()
    results = vector_store.similarity_search(query, k=2)
    search_time = time.time() - start_time

    print(f"\nResultados para '{query}' (tiempo de búsqueda: {search_time:.4f} segundos):")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.page_content}")
        print(f"     Contexto: {result.metadata['context']}")