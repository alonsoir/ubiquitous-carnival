import requests
import random
from dotenv import load_dotenv
import os
import json

# Cargar variables de entorno
load_dotenv()
claude_api_key = os.getenv("ANTHROPIC_API_KEY")

# Datos simulados
absent_students = {
    "Juan Pérez": {"tutor": "+34667519829", "reason": "unknown"},
    "María García": {"tutor": "+34667519829", "reason": "unknown"}
}

medical_phone_numbers = ["+34900000001", "+34900000002", "+34900000003"]


# Función para enviar mensajes a través de CallmeBot
def send_message(phone, message):
    apikey = os.getenv("CALLMEBOT_API_KEY")
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={apikey}"
    print(f"Enviando mensaje a {phone}: {message}")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")


# Función para generar respuestas utilizando Claude
def generate_response(prompt):
    print(f"\nPrompt enviado a Claude:\n{prompt}")

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",  # URL correcta de la API
            headers={
                "x-api-key": claude_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-sonnet-20240229",  # Modelo actualizado
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )

        response.raise_for_status()  # Verificar si hay errores HTTP

        response_data = response.json()
        if 'content' in response_data:
            response_text = response_data['content'][0]['text']
            print(f"Respuesta de Claude:\n{response_text}\n")
            return response_text
        else:
            print("Error: Respuesta inesperada de la API")
            return "Lo siento, hubo un error al procesar la respuesta."

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud a Claude: {e}")
        return "Lo siento, hubo un error de comunicación con el servicio."
    except json.JSONDecodeError as e:
        print(f"Error al decodificar la respuesta JSON: {e}")
        return "Lo siento, hubo un error al procesar la respuesta."
    except Exception as e:
        print(f"Error inesperado: {e}")
        return "Lo siento, ocurrió un error inesperado."


# Función principal del chatbot
def absenteeism_chatbot():
    for student, info in absent_students.items():
        try:
            # Saludo inicial
            prompt = f"Saluda al tutor de {student} e infórmale sobre la ausencia del estudiante de manera educada pero firme."
            greeting = generate_response(prompt)
            if greeting:
                send_message(info['tutor'], greeting)

            # Preguntar sobre el motivo de la ausencia
            prompt = f"Pregunta al tutor si sabe el motivo de la ausencia de {student}."
            reason_question = generate_response(prompt)
            if reason_question:
                send_message(info['tutor'], reason_question)

            # Simular respuesta del tutor
            tutor_response = random.choice(["No lo sé", "Están enfermos", "Tuvieron una cita médica"])
            print(f"Respuesta simulada del tutor: {tutor_response}")

            # Generar respuesta según el caso
            if tutor_response == "No lo sé":
                prompt = f"El tutor no sabe por qué {student} está ausente. Sugiere programar una reunión para discutir seriamente la ausencia."
                suggestion = generate_response(prompt)
                if suggestion:
                    send_message(info['tutor'], suggestion)
            elif tutor_response in ["Están enfermos", "Tuvieron una cita médica"]:
                prompt = f"{student} está enfermo. Recomienda visitar a un médico y proporciona números de contacto si es necesario."
                recommendation = generate_response(prompt)
                if recommendation:
                    phone_numbers = ", ".join(medical_phone_numbers)
                    send_message(info['tutor'], f"{recommendation}\nContactos médicos: {phone_numbers}")

            # Despedida
            prompt = f"Dile adiós al tutor de {student} profesionalmente y ofrécele ayuda adicional si es necesario."
            farewell = generate_response(prompt)
            if farewell:
                send_message(info['tutor'], farewell)

        except Exception as e:
            print(f"Error procesando al estudiante {student}: {e}")


if __name__ == "__main__":
    absenteeism_chatbot()