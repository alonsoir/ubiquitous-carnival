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
            "keywords": "biología, ecología, investigación",
        },
    ),
    Document(
        page_content="Texto del documento sobre ciencia.",
        metadata={
            "context": "ciencia",
            "document_type": "doc",
            "creation_date": "2024-10-01",
            "author": "John Doe",
            "keywords": "biología, ecología, investigación",
        },
    ),
    Document(
        page_content="Texto del PDF sobre tecnología.",
        metadata={
            "context": "tecnología",
            "document_type": "PDF",
            "creation_date": "2024-10-01",
            "author": "Jane Smith",
            "keywords": "innovación, desarrollo",
        },
    ),
    Document(
        page_content="Texto del PDF sobre salud.",
        metadata={
            "context": "salud",
            "document_type": "PDF",
            "creation_date": "2024-10-01",
            "author": "Alice Johnson",
            "keywords": "bienestar, medicina",
        },
    ),
]

# Crear embeddings para los documentos en lotes
batch_size = 2
embeddings = []

for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i + batch_size]
    batch_embeddings = embeddings_model.embed_documents([doc.page_content for doc in batch_docs])
    embeddings.extend(batch_embeddings)

# Convertir a un array numpy
embeddings = np.array(embeddings).astype('float32')

# Crear el índice FAISS usando IndexIVFPQ para optimización
dimension = len(embeddings[0])  # Dimensiones del vector de embeddings

# Ajustar nlist y el tamaño del código (code_size)
nlist = min(2, len(documents))  # Cambiado a 2 para evitar el warning
code_size = 8  # Tamaño del código para PQ

quantizer = faiss.IndexFlatL2(dimension)  # Usar L2 para la distancia
ivf_index = faiss.IndexIVFPQ(quantizer, dimension, nlist, code_size, faiss.METRIC_L2)

# Entrenar el índice con una muestra de los embeddings
ivf_index.train(embeddings)

# Añadir los embeddings al índice FAISS
ivf_index.add(embeddings)

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
    index=ivf_index,
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

'''
Aquí tienes una comparación entre los índices **IndexIVFFlat** e **IndexIVFPQ**, junto con algunas alternativas para su uso:

## Comparación: IndexIVFFlat vs. IndexIVFPQ

| Característica         | **IndexIVFFlat**                               | **IndexIVFPQ**                                   |
|------------------------|------------------------------------------------|--------------------------------------------------|
| **Tipo de Almacenamiento** | Almacena vectores en su forma original.     | Utiliza cuantización de producto (PQ) para comprimir vectores. |
| **Precisión**          | Alta precisión, ya que realiza búsquedas exactas dentro de las celdas. | Puede sacrificar algo de precisión por la compresión, pero aún proporciona buenos resultados. |
| **Velocidad de Búsqueda** | Más lento en grandes conjuntos de datos debido a la búsqueda exhaustiva. | Más rápido, especialmente en grandes conjuntos, gracias a la reducción del espacio de búsqueda. |
| **Uso de Memoria**     | Consume más memoria porque almacena todos los vectores sin compresión. | Consume significativamente menos memoria debido a la compresión (hasta 97% menos). |
| **Configuración**      | Más simple, solo requiere definir el número de celdas (nlist). | Requiere definir tanto el número de celdas (nlist) como el tamaño del código (code_size). |
| **Entrenamiento**      | Necesita ser entrenado para crear las celdas antes de añadir datos. | También necesita entrenamiento, pero el proceso es más complejo debido a la cuantización. |

### Pros y Contras

#### Pros de IndexIVFFlat
- **Precisión**: Proporciona resultados exactos al buscar en cada celda.
- **Simplicidad**: Fácil de entender y configurar.

#### Contras de IndexIVFFlat
- **Velocidad**: Puede ser muy lento con grandes volúmenes de datos.
- **Uso de Memoria**: No optimiza el uso de memoria, lo que puede ser un problema con conjuntos de datos grandes.

#### Pros de IndexIVFPQ
- **Velocidad**: Mucho más rápido en búsquedas debido a la reducción del espacio de búsqueda.
- **Eficiencia de Memoria**: Reduce significativamente el uso de memoria, lo que permite manejar conjuntos de datos más grandes.

#### Contras de IndexIVFPQ
- **Precisión**: Puede haber una ligera pérdida en la precisión debido a la compresión.
- **Complejidad**: La configuración y entrenamiento son más complejos que en IndexIVFFlat.

## Alternativas

1. **IndexFlatL2**
   - Realiza una búsqueda exhaustiva sin compresión. Ideal para conjuntos de datos pequeños donde se requiere precisión máxima.

2. **IndexPQ**
   - Utiliza solo cuantización de producto sin agrupación. Es útil cuando se necesita un balance entre velocidad y precisión, pero no se requiere agrupación.

3. **IndexIVFScalarQuantizer**
   - Combina el índice invertido con cuantización escalar, ofreciendo un enfoque diferente para reducir el uso de memoria y mejorar la velocidad.

4. **IndexIVFPQR**
   - Una variante que combina IVF y PQ con re-ranking basado en códigos, ofreciendo un equilibrio entre velocidad y precisión mejorada.

5. **Composite Indexes**
   - Usar `index_factory` para crear índices compuestos que combinan múltiples técnicas (por ejemplo, OPQ + IVF + PQ) para optimizar aún más el rendimiento.

Estas alternativas permiten adaptar la solución a diferentes necesidades en cuanto a precisión, velocidad y uso de memoria según el caso específico que estés abordando.

Citations:
[1] https://www.pinecone.io/learn/series/faiss/faiss-tutorial/
[2] https://www.pinecone.io/learn/series/faiss/product-quantization/
[3] https://www.pinecone.io/learn/series/faiss/composite-indexes/
[4] https://github.com/facebookresearch/faiss/wiki/Faiss-indexes/9df19586b3a75e4cb1c2fb915f2c695755a599b8
[5] https://faiss.ai/cpp_api/struct/structfaiss_1_1IndexIVFFlat.html
[6] https://pub.towardsai.net/unlocking-the-power-of-efficient-vector-search-in-rag-applications-c2e3a0c551d5?gi=71a82e3ea10e
[7] https://www.pingcap.com/article/mastering-faiss-vector-database-a-beginners-handbook/
[8] https://wangzwhu.github.io/home/file/acmmm-t-part3-ann.pdf
'''