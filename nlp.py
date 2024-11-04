from textblob import TextBlob
blob = TextBlob("Python is amazing!")
print(blob.sentiment)  # Outputs the sentiment of the text

# Lista de frases para analizar
texts = [
    "Python is amazing!",
    "I hate bugs in my code.",
    "This library makes programming easier.",
    "I feel sad when I can't solve a problem."
]

# Analizar cada frase y mostrar su sentimiento
for text in texts:
    blob = TextBlob(text)
    sentiment = blob.sentiment
    print(f"Texto: {text}")
    print(f"Polaridad: {sentiment.polarity}, Subjetividad: {sentiment.subjectivity}\n")