import requests
import random
from transformers import pipeline
from dotenv import load_dotenv
import os
# Cargar las variables de entorno
load_dotenv()

# Configuración del modelo de lenguaje
nlp = pipeline("text-generation", model="tiiuae/falcon-7b-instruct")

# Datos simulados de ausencias
ausentes = {
    "Juan Pérez": {"tutor": "+34667519829", "motivo": "desconocido"},
    "María García": {"tutor": "+34667519829", "motivo": "desconocido"}
}

# Lista de teléfonos de médicos
telefonos_medicos = ["+34900000001", "+34900000002", "+34900000003"]

# Función para enviar mensajes a través de CallmeBot
def enviar_mensaje(telefono, mensaje):
    apikey = os.getenv("CALLMEBOT_API_KEY", "")
    url = f"https://api.callmebot.com/whatsapp.php?phone={telefono}&text={mensaje}&apikey={apikey}"
    requests.get(url)

# Función para generar respuestas usando el modelo de lenguaje
def generar_respuesta(prompt, max_length=100):
    try:
        respuesta = nlp(prompt, max_length=max_length, num_return_sequences=1)[0]['generated_text']
        return respuesta.split(prompt)[1].strip()
    except Exception as e:
        print(f"Error generando respuesta: {e}")
        return "Error generando respuesta."

# Función principal del chatbot
def chatbot_absentismo():
    for estudiante, info in ausentes.items():
        # Generar saludo e informar de la ausencia
        prompt = (f"Eres un asistente del centro educativo y contactas de manera formal y cordial. "
                  f"Dirígete al tutor de {estudiante} e informa de su ausencia a clase hoy. "
                  f"Invítalo a proporcionar un motivo específico si lo conoce.")
        saludo = generar_respuesta(prompt)
        enviar_mensaje(info['tutor'], saludo)

        # Preguntar motivo de ausencia
        prompt = f"Pregunta cordialmente al tutor si conoce el motivo específico de la ausencia de {estudiante}:"
        pregunta_motivo = generar_respuesta(prompt)
        enviar_mensaje(info['tutor'], pregunta_motivo)

        # Simulación de respuesta del tutor para pruebas
        respuesta_tutor = random.choice(["No lo sé", "Está enfermo", "Tenía una cita médica", "Asunto personal"])

        if respuesta_tutor == "No lo sé":
            prompt = (f"El tutor no sabe la razón de la ausencia de {estudiante}. "
                      f"Responde de forma respetuosa sugiriendo que programe una reunión con el centro para discutir el apoyo necesario.")
            sugerencia = generar_respuesta(prompt)
            enviar_mensaje(info['tutor'], sugerencia)

        elif respuesta_tutor == "Está enfermo":
            prompt = (f"El tutor indica que {estudiante} está enfermo. "
                      f"Responde de manera empática, sugiriendo que el tutor considere una revisión médica si es necesario. "
                      f"Proporciona números de contacto de profesionales médicos de confianza.")
            recomendacion = generar_respuesta(prompt)
            numeros = ", ".join(telefonos_medicos)
            enviar_mensaje(info['tutor'], f"{recomendacion}\nNúmeros de médicos: {numeros}")

        elif respuesta_tutor == "Tenía una cita médica":
            prompt = (f"El tutor indica que {estudiante} tenía una cita médica. "
                      f"Agradece la información y ofrece al tutor la posibilidad de solicitar apoyo en temas escolares, si necesario.")
            agradecimiento = generar_respuesta(prompt)
            enviar_mensaje(info['tutor'], agradecimiento)

        elif respuesta_tutor == "Asunto personal":
            prompt = (f"El tutor menciona que la ausencia de {estudiante} es por un asunto personal. "
                      f"Responde de manera comprensiva y ofrece la posibilidad de coordinar cualquier asistencia escolar adicional si fuera necesaria.")
            respuesta_asunto_personal = generar_respuesta(prompt)
            enviar_mensaje(info['tutor'], respuesta_asunto_personal)

        # Despedida cordial y oferta de ayuda adicional
        prompt = (f"Despídete cordialmente del tutor de {estudiante}, "
                  f"reiterando la disposición del centro a ofrecer apoyo en caso de necesitar ayuda adicional.")
        despedida = generar_respuesta(prompt)
        enviar_mensaje(info['tutor'], despedida)

# Ejecutar el chatbot
if __name__ == "__main__":
    chatbot_absentismo()
