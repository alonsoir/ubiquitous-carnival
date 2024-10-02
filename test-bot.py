import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

'''
This is a simple example of how to use the Anthropic API. A test.
'''

# Asegúrate de que tu clave API esté en el archivo .env como ANTHROPIC_API_KEY
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = "What is the capital of France?"

response = anthropic.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
    temperature=0,
    messages=[
        {"role": "user", "content": message}
    ]
)

print(response.content[0].text)