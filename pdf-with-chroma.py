from pdfminer.high_level import extract_text
import pandas as pd
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# Inicializar el cliente de OpenAI
client = OpenAI()

# Crear embeddings del texto extraído
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Ruta al archivo PDF
pdf_path = '/Users/aironman/Desktop/pruebas/aqualia.pdf'

# Extraer texto del PDF
text = extract_text(pdf_path)

# Imprimir el texto extraído (opcional)
print(text)

# Convertir el texto a un DataFrame
# Suponiendo que el texto tiene líneas separadas por saltos de línea y columnas separadas por comas o tabulaciones
data = [line.split(',') for line in text.splitlines() if line.strip()]  # Cambia ',' por '\t' si es tabulación

# Crear un DataFrame
df = pd.DataFrame(data[1:], columns=data[0])  # Usar la primera línea como encabezados

# Mostrar el DataFrame (opcional)
#  print(df)

# Convertir cada fila del DataFrame a documentos para Chroma
documents = [Document(page_content=row.to_string(index=False)) for _, row in df.iterrows()]

# Crear embeddings y almacenar en Chroma
vector_store = Chroma.from_documents(documents, embedding=embeddings_model, persist_directory="./data/chroma_db")

# Realizar una consulta para recuperar información relevante
query = "¿Qué información contiene el texto extraído?"
print(f"{query}\n")
results = vector_store.similarity_search(query)

# Mostrar los resultados recuperados
for result in results:
    print(result.page_content)  # Acceder al contenido de la página