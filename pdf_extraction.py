import pymupdf4llm

# Extract PDF content as Markdown
md_text = pymupdf4llm.to_markdown("pdf/cv.pdf")
# print(md_text[:500])  # Print first 500 characters
print(md_text)
# Extract PDF content as Markdown, just pages 1 and 2
md_text = pymupdf4llm.to_markdown("pdf/cv.pdf", pages=[1, 2])
# print(md_text[:500])  # Print first 500 characters
print(md_text)

llama_reader = pymupdf4llm.LlamaMarkdownReader()
llama_docs = llama_reader.load_data("pdf/cv.pdf")
print(f"Number of LlamaIndex documents: {len(llama_docs)}")
print(f"Content of first document: {llama_docs[0].text[:500]}")


# Extract PDF content as plain text
text = pymupdf4llm.to_markdown("pdf/aqualia.pdf")
print(text[:500])  # Print first 500 characters

endesa = pymupdf4llm.to_markdown("pdf/endesa.pdf")
print(endesa[:500])  # Print first 500 characters

receipt = pymupdf4llm.to_markdown("pdf/receipt.pdf")
print(receipt[:500])  # Print first 500 characters

md_text_images = pymupdf4llm.to_markdown(doc="pdf/formulas.pdf",
                                         pages=[1],
                                         page_chunks=True,
                                         write_images=True,
                                         image_path="images",
                                         image_format="jpg",
                                         dpi=200)
print(md_text_images[0]['images'])  # Print image information from the first chunk

md_text_chunks = pymupdf4llm.to_markdown(doc="pdf/cv.pdf",
                                         pages=[0,2,3,4,5,6,7,8,9,10,11],
                                         page_chunks=True)
print(f"There are {len(md_text_chunks)} chunks of text.")
print(md_text_chunks[0])  # Print the first chunk

md_text_words = pymupdf4llm.to_markdown(doc="pdf/formulas.pdf",
                                        pages=[1],
                                        page_chunks=True,
                                        write_images=True,
                                        image_path="images",
                                        image_format="jpg",
                                        dpi=200,
                                        extract_words=True)
print(md_text_words[0]['words'][:5])  # Print the first 5 words from the first chunk

import pandas as pd
import numpy as np
from fpdf import FPDF

# Generar datos aleatorios
num_rows = 10
data = {
    'ID': np.arange(1, num_rows + 1),
    'Nombre': [f'Nombre_{i}' for i in range(1, num_rows + 1)],
    'Edad': np.random.randint(18, 60, size=num_rows),
    'Ciudad': [f'Ciudad_{i}' for i in range(1, num_rows + 1)]
}

df = pd.DataFrame(data)

# Crear un archivo PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Agregar encabezados de tabla
for column in df.columns:
    pdf.cell(40, 10, column, border=1)
pdf.ln()

# Agregar filas de datos
for index, row in df.iterrows():
    for item in row:
        pdf.cell(40, 10, str(item), border=1)
    pdf.ln()

# Guardar el archivo PDF
pdf.output("pdf/tabla_datos_aleatorios.pdf")

print("PDF generado con éxito: pdf/tabla_datos_aleatorios.pdf")

import pymupdf4llm
import json

md_text_tables = pymupdf4llm.to_markdown(doc="pdf/tabla_datos_aleatorios.pdf",
                                         pages=[0],  # Specify pages containing tables
                                         )
print(md_text_tables)