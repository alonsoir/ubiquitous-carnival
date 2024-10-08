from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import faiss
import numpy as np

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

# Crear embeddings para los documentos
embeddings = np.array([embeddings_model.embed_query(doc.page_content) for doc in documents]).astype('float32')

# Crear el índice FAISS
dimension = len(embeddings[0])  # Dimensiones del vector de embeddings
faiss_index = faiss.IndexFlatL2(dimension)  # Usar L2 para la distancia

# Añadir los embeddings al índice FAISS
faiss_index.add(embeddings)


# Crear un docstore (almacenamiento de documentos)
class SimpleDocstore:
    def __init__(self, documents):
        self.documents = documents

    def search(self, _id):
        return self.documents[_id]


# Instanciar el docstore
docstore = SimpleDocstore(documents)

# Crear el vector store usando FAISS
vector_store = FAISS(
    embedding_function=embeddings_model,
    index=faiss_index,
    docstore=docstore,
    index_to_docstore_id={i: i for i in range(len(documents))}
)

query = "¿Qué información contiene el texto extraído?"

# Realizar la búsqueda (sin filtros en este caso)
results = vector_store.similarity_search(query)

# Mostrar resultados
for result in results:
    print(result.page_content)
    print(result.metadata)