from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    prompt="Un dibujo estilo manga de Lisa Manoban", n=2, size="1024x1024"
)

print(response.data[0].url)
