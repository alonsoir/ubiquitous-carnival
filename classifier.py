# Good way: HuggingFace to the rescue
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
print(classifier("I love Python!"))