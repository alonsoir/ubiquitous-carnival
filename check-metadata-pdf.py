import os
import pikepdf

def extract_pdf_metadata(pdf_path):
    """Extrae metadatos de un archivo PDF."""
    try:
        with pikepdf.open(pdf_path) as pdf:
            docinfo = pdf.docinfo
            print(f"Metadatos de {pdf_path}:")
            for key, value in docinfo.items():
                print(f"{key}: {value}")
            print("\n")
    except Exception as e:
        print(f"Error al procesar {pdf_path}: {e}")

def scan_pdfs_in_directory(directory):
    """Escanea todos los archivos PDF en un directorio y extrae sus metadatos."""
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            extract_pdf_metadata(pdf_path)

# Especifica la ruta a la carpeta que contiene los archivos PDF
directory_path = '/Users/aironman/Desktop/pruebas/'
scan_pdfs_in_directory(directory_path)