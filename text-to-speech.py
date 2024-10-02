import subprocess
from pathlib import Path

from openai import OpenAI


def play_mp3(file_path):
  """
  Reproduce un archivo MP3 en macOS usando el comando afplay.

  :param file_path: Ruta al archivo MP3
  """
  file_path = Path(file_path).resolve()
  if not file_path.exists():
    print(f"El archivo {file_path} no existe.")
    return

  try:
    subprocess.run(["afplay", str(file_path)], check=True)
    print(f"Reproducción de {file_path} completada.")
  except subprocess.CalledProcessError as e:
    print(f"Error al reproducir el archivo: {e}")
client = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"

try:
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Por favor, no useis esta tecnología para hacer el mal. Gracias."
    )

    # Escribir directamente el contenido de la respuesta al archivo
    with open(speech_file_path, "wb") as file:
        file.write(response.content)

    print(f"Archivo de audio guardado en: {speech_file_path}")
    play_mp3(speech_file_path)
except Exception as e:
    print(f"Ocurrió un error: {e}")
