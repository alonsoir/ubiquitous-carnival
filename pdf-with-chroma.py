import os
import shutil
from pdfminer.high_level import extract_text
import pandas as pd
import re
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma  # Asegúrate de importar desde langchain_chroma
from langchain.schema import Document

# Inicializar el cliente de OpenAI
client = OpenAI()

# Crear embeddings del texto extraído
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Ruta al archivo PDF
pdf_path = "/Users/aironman/Desktop/pruebas/Hoja de fórmulas.pdf"
persist_directory = "./data/chroma_db"

# Limpiar la base de datos existente eliminando el directorio
if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory)  # Eliminar todo el directorio

# Inicializar ChromaDB con la función de embeddings
vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings_model)

# Extraer texto del PDF
text = extract_text(pdf_path)

# Imprimir el texto extraído para revisión
print("Texto extraído del PDF:")
print(text)

# Normalizar el texto: eliminar saltos de línea innecesarios y espacios adicionales
text = re.sub(r'\n+', ' ', text)  # Reemplazar múltiples saltos de línea por un espacio
text = re.sub(r'\s+', ' ', text)   # Reemplazar múltiples espacios por uno solo

# Filtrar líneas que contengan ecuaciones usando regex
equation_lines = re.findall(r'(\S.*?[=<>≤≥\+\-\*/]\S.*?)(?=\s+|$)', text)

# Verificar si se encontraron ecuaciones
if not equation_lines:
    raise ValueError("No se encontraron ecuaciones en el texto extraído.")

# Unir líneas que deberían estar juntas (por ejemplo, aquellas que terminan con ciertos operadores)
joined_lines = []
temp_line = ""

for line in equation_lines:
    if re.search(r'[=<>≤≥\+\-\*/]$', line):
        temp_line += line + " "
    else:
        if temp_line:
            temp_line += line.strip()
            joined_lines.append(temp_line.strip())
            temp_line = ""
        else:
            joined_lines.append(line.strip())

# Convertir el texto a un DataFrame solo si hay datos válidos
if joined_lines:
    data = [line.split() for line in joined_lines]

    if len(data) > 1:
        num_columns = max(len(row) for row in data)
        consistent_data = [row for row in data if len(row) == num_columns]

        if consistent_data:
            df = pd.DataFrame(consistent_data)
            print(df.head())  # Mostrar las primeras filas del DataFrame (opcional)
        else:
            raise ValueError("No hay datos consistentes para crear un DataFrame.")
    else:
        raise ValueError("No hay suficientes datos para crear un DataFrame.")
else:
    raise ValueError("No se encontraron ecuaciones en el texto extraído.")

# Convertir cada fila del DataFrame a documentos para Chroma
documents = [
    Document(page_content=row.to_string(index=False)) for _, row in df.iterrows()
]

# Crear embeddings y almacenar en Chroma
vector_store.add_documents(documents)

# Realizar una consulta para recuperar información relevante
query = "¿Qué información contiene el texto extraído?"
print(f"{query}\n")
results = vector_store.similarity_search(query)

# Mostrar los resultados recuperados
for result in results:
    print(result.page_content)  # Acceder al contenido de la página