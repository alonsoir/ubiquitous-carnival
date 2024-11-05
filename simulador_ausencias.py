from openai import OpenAI
import requests
import random
from dotenv import load_dotenv
import os

# Load environment variables (make sure your OpenAI API key is set in the .env file)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simulated data. The messsage will be sent to the tutor's phone number
absent_students = {
    "Juan Pérez": {"tutor": "+34667519829", "reason": "unknown"},
    "María García": {"tutor": "+34667519829", "reason": "unknown"}
}

medical_phone_numbers = ["+34900000001", "+34900000002", "+34900000003"]

# Function to send messages via CallmeBot
def send_message(phone, message):
    apikey = os.getenv("CALLMEBOT_API_KEY")
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={apikey}"
    print(f"Sending message to {phone}: {message}")  # Verbose message
    requests.get(url)

# Function to generate responses using GPT-4 from OpenAI
def generate_response(prompt):
    print(f"\nPrompt sent to GPT-4:\n{prompt}")  # Print prompt for tracking
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a cordial but firm assistant communicating with tutors about student absenteeism."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    response_text = response.choices[0].message.content.strip()
    print(f"Response from GPT-4:\n{response_text}\n")  # Print received response
    return response_text

# Main chatbot function. This is a simulation of the chatbot's behavior. It's not a real chatbot, but it simulates the conversation.
# In the real world, i should have a template for the messages and a way to store the messages in a database.
# I will try to guide the tutors asking them about the real reason for the absence. Right now, they are all sick, so they
# have to go to the hospital.
def absenteeism_chatbot():
    for student, info in absent_students.items():
        # Initial greeting
        prompt = f"Greet the tutor of {student} and inform them about the student's absence in a polite but firm manner."
        greeting = generate_response(prompt)
        send_message(info['tutor'], greeting)

        # Ask about the reason for the absence
        prompt = f"Ask the tutor if they know the reason for {student}'s absence."
        reason_question = generate_response(prompt)
        send_message(info['tutor'], reason_question)

        # Simulate tutor's response for testing
        tutor_response = random.choice(["I don't know", "They are sick", "They had a medical appointment"])
        print(f"Tutor's simulated response: {tutor_response}")  # Print simulated response

        # Generate suggestion or recommendation based on tutor's response
        if tutor_response == "I don't know":
            prompt = f"The tutor does not know why {student} is absent. Suggest scheduling a meeting to seriously discuss absenteeism."
            suggestion = generate_response(prompt)
            send_message(info['tutor'], suggestion)
        elif tutor_response in ["They are sick", "They had a medical appointment"]:
            prompt = f"{student} is sick. Recommend visiting a doctor and provide contact phone numbers if necessary."
            recommendation = generate_response(prompt)
            phone_numbers = ", ".join(medical_phone_numbers)
            send_message(info['tutor'], f"{recommendation}\nMedical contacts: {phone_numbers}")

        # Farewell
        prompt = f"Say goodbye to {student}'s tutor professionally and offer additional help if needed."
        farewell = generate_response(prompt)
        send_message(info['tutor'], farewell)

# Run the chatbot
if __name__ == "__main__":
    absenteeism_chatbot()
