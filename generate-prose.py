from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Escribe un haiku sobre la recursión en programación.",
        },
    ],
)

print(f"{completion.choices[0].message.content}")


response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": """
                        You are a helpful assistant that answers programming questions 
                        in the style of a southern belle from the southeast United States.
                    """,
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Are semicolons optional in JavaScript?"}
            ],
        },
    ],
)
print(f"{response.choices[0].message.content}")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": [{"type": "text", "text": "knock knock."}]},
        {"role": "assistant", "content": [{"type": "text", "text": "Who's there?"}]},
        {"role": "user", "content": [{"type": "text", "text": "Orange."}]},
    ],
)
print(f"{response.choices[0].message.content}")
