from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    prompt="Un cuadro de nubes y niebla sobre el mar, al amanecer, realista", n=2, size="1024x1024"
)

for i, image in enumerate(response.data):
    print(f"Imagen {i+1}: {image.url}")
