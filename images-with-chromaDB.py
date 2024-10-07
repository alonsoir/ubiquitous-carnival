from PIL import Image
import pytesseract
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document  # Importar la clase Document

# Cargar la imagen
image_path = "/Users/aironman/Desktop/pruebas/feynman-chat.jpeg"
image = Image.open(image_path)

# Aplicar OCR para extraer texto
extracted_text = pytesseract.image_to_string(image)

# Crear embeddings del texto extraído
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Crear un documento usando la clase Document
documents = [Document(page_content=extracted_text)]

# Crear el vector store y almacenar el texto con persistencia automática
vector_store = Chroma.from_documents(documents, embedding=embeddings_model, persist_directory="./data/chroma_db")

# Realizar una consulta para recuperar información relevante
query = "¿Qué información contiene el texto extraído?"
print(f"{query}\n")
results = vector_store.similarity_search(query)

# Mostrar los resultados recuperados
for result in results:
    print(result.page_content)  # Acceder al contenido de la página

# Inicializar el modelo de embeddings
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Cargar el vector store desde el directorio especificado
persist_directory = "./data/chroma_db"  # Asegúrate de que esta ruta es correcta
another_vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)

# Realizar una consulta para recuperar información relevante
query = "¿Qué información contiene el texto extraído?"
print(f"{query}\n")
results = another_vector_store.similarity_search(query)

# Mostrar los resultados recuperados
for result in results:
    print(result.page_content)  # Acceder al contenido de la página