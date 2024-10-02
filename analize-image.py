from openai import OpenAI

client = OpenAI()

import time
import functools

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"La función {func.__name__} tardó {execution_time:.4f} segundos en ejecutarse.")
        return result
    return wrapper

# Ejemplo de uso
@timing_decorator
def ejemplo_funcion(n):
    """Esta es una función de ejemplo que suma los números del 1 al n."""
    return sum(range(1, n+1))
@timing_decorator
def completion_sample():
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                    }
                },
            ],
        }
        ],
    )
    return completion

print(f"{completion_sample().choices[0].message.content}")