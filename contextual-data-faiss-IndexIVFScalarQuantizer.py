from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import faiss
import numpy as np

# Initialize the embeddings model
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Sample documents with their respective contexts
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

# Create embeddings for documents in batches
batch_size = 2
embeddings = []

for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i + batch_size]
    batch_embeddings = embeddings_model.embed_documents([doc.page_content for doc in batch_docs])
    embeddings.extend(batch_embeddings)

# Convert to a numpy array
embeddings = np.array(embeddings).astype('float32')

# Create the FAISS index using IndexIVFScalarQuantizer for optimization
dimension = len(embeddings[0])  # Dimensions of the embedding vector

# Adjust nlist
nlist = min(2, len(documents))  # Changed to 2 to avoid warning

# Create the quantizer
quantizer = faiss.IndexFlatL2(dimension)

# Create IndexIVFScalarQuantizer
ivf_index = faiss.IndexIVFScalarQuantizer(quantizer, dimension, nlist, faiss.ScalarQuantizer.QT_8bit, faiss.METRIC_L2)

# Train the index with a sample of the embeddings
ivf_index.train(embeddings)

# Add the embeddings to the FAISS index
ivf_index.add(embeddings)

# Create a docstore (document storage)
class SimpleDocstore:
    def __init__(self, documents):
        self.documents = documents

    def search(self, _id):
        return self.documents[_id]

# Instantiate the docstore
docstore = SimpleDocstore(documents)

# Create the vector store using FAISS
vector_store = FAISS(
    embedding_function=embeddings_model,
    index=ivf_index,
    docstore=docstore,
    index_to_docstore_id={i: i for i in range(len(documents))}
)

query = "¿Qué información contiene el texto extraído?"

# Perform the search (without filters in this case)
results = vector_store.similarity_search(query)

# Show results
for result in results:
    print(result.page_content)
    print(result.metadata)