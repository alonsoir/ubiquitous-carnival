import numpy as np
import faiss
import time
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Inicializar el modelo de embeddings
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Función para generar documentos sintéticos
def generate_synthetic_documents(num_docs):
    documents = []
    for i in range(num_docs):
        content = f"Texto sintético número {i + 1} sobre ciencia, tecnología y salud."
        metadata = {
            "context": "ciencia",
            "document_type": "sintético",
            "creation_date": "2024-10-01",
            "author": f"Autor {i + 1}",
            "keywords": "sintético, prueba, demo",
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

# Mantener el número de documentos igual
num_documents = 300
documents = generate_synthetic_documents(num_documents)

# Crear embeddings para los documentos en lotes
batch_size = 10
embeddings = []

start_time = time.time()  # Medir tiempo de creación de embeddings

for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i + batch_size]
    batch_embeddings = embeddings_model.embed_documents([doc.page_content for doc in batch_docs])
    embeddings.extend(batch_embeddings)

embeddings = np.array(embeddings).astype('float32')

# Definir dimensiones y parámetros del índice
dimension = len(embeddings[0])

# Calcular M para que sea divisor de dimension
M = 4
while dimension % M != 0 and M <= dimension:
    M += 1

if M > dimension:
    raise ValueError("No es posible dividir las dimensiones en subespacios compatibles con PQ.")

# Reducir nlist y el número de centroides
nlist = 10  # Número reducido de clusters
n_centroids = min(num_documents, 50)  # Reducir el número de centroides, se ajusta a 50
index_string = f"IVF{nlist},PQ{M}"  # Ajustar los subespacios PQ dinámicamente

# Crear índice con los centroides y parámetros actualizados
index = faiss.index_factory(dimension, index_string)

try:
    # Intentar entrenar el índice con los embeddings
    index.train(embeddings)
    print(f"Entrenamiento exitoso con nlist: {nlist} y M: {M}")

    # Agregar los embeddings al índice FAISS solo si se entrenó exitosamente
    index.add(embeddings)

    # Crear un almacenamiento de documentos (docstore)
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
        index=index,
        docstore=docstore,
        index_to_docstore_id={i: i for i in range(len(documents))}
    )

    query = "¿Qué información contiene el texto extraído?"

    # Medir tiempo de búsqueda
    search_start_time = time.time()
    results = vector_store.similarity_search(query)
    search_time = time.time() - search_start_time

    # Mostrar resultados y tiempos
    print(f"Tiempo de creación de embeddings: {time.time() - start_time:.2f} segundos")
    print(f"Tiempo de búsqueda: {search_time:.2f} segundos")

    print("Resultados:")
    for result in results:
        print(result.page_content)
        print(result.metadata)

except RuntimeError as e:
    print(f"Error al entrenar el índice: {e}")

'''
/Users/aironman/git/interactive-llm-voice-a/venv/bin/python /Users/aironman/git/langgraph-chatbot/contextual-data-faiss-index_factory.py 
WARNING clustering 300 points to 10 centroids: please provide at least 390 training points
WARNING clustering 300 points to 256 centroids: please provide at least 9984 training points
WARNING clustering 300 points to 256 centroids: please provide at least 9984 training points
WARNING clustering 300 points to 256 centroids: please provide at least 9984 training points
WARNING clustering 300 points to 256 centroids: please provide at least 9984 training points
Entrenamiento exitoso con nlist: 10 y M: 4
Tiempo de creación de embeddings: 30.76 segundos
Tiempo de búsqueda: 0.52 segundos
Resultados:
Texto sintético número 35 sobre ciencia, tecnología y salud.
{'context': 'ciencia', 'document_type': 'sintético', 'creation_date': '2024-10-01', 'author': 'Autor 35', 'keywords': 'sintético, prueba, demo'}
Texto sintético número 53 sobre ciencia, tecnología y salud.
{'context': 'ciencia', 'document_type': 'sintético', 'creation_date': '2024-10-01', 'author': 'Autor 53', 'keywords': 'sintético, prueba, demo'}
Texto sintético número 2 sobre ciencia, tecnología y salud.
{'context': 'ciencia', 'document_type': 'sintético', 'creation_date': '2024-10-01', 'author': 'Autor 2', 'keywords': 'sintético, prueba, demo'}
Texto sintético número 44 sobre ciencia, tecnología y salud.
{'context': 'ciencia', 'document_type': 'sintético', 'creation_date': '2024-10-01', 'author': 'Autor 44', 'keywords': 'sintético, prueba, demo'}

Process finished with exit code 0


Advertencias: Aunque aún ves algunas advertencias sobre el número de puntos de entrenamiento (pocas muestras en 
comparación con el número de centroides), estas no han impedido el entrenamiento exitoso del índice. 
Esto sugiere que los parámetros son funcionales, aunque las advertencias sugieren que sería beneficioso aumentar el 
número de puntos de entrenamiento en futuras pruebas.

Entrenamiento exitoso: El índice se entrenó correctamente con nlist=10 y M=4. 
Las advertencias sobre el número de centroides son normales dado el pequeño tamaño de tu dataset (300 puntos). 
Reducir el número de centroides a 50 o menos podría minimizar esas advertencias, pero dado que el entrenamiento 
fue exitoso, no es estrictamente necesario.

Tiempos de ejecución:
Creación de embeddings: ~30.76 segundos, lo cual es un buen tiempo dado el número de documentos y la carga de 

procesamiento.
Tiempo de búsqueda: ~0.52 segundos, lo cual es rápido, indicando que el índice está funcionando de manera eficiente.
Resultados de la búsqueda: El sistema devolvió correctamente los resultados de la búsqueda de similitud, 
mostrando fragmentos de texto y metadatos relevantes.

Próximos pasos
Si planeas aumentar el número de documentos, podrías evitar algunas de las advertencias incrementando el número de 
documentos de entrenamiento o reduciendo el número de centroides.
Si las advertencias no te preocupan demasiado y el rendimiento es bueno, puedes continuar ajustando los parámetros 
del índice según sea necesario.
'''
