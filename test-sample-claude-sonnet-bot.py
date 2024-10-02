from typing import List, TypedDict
from typing_extensions import NotRequired
import os
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END

from anthropic import Anthropic

# Cargar variables de entorno
load_dotenv()


# Definir el estado
class State(TypedDict):
    messages: NotRequired[List[BaseMessage]]


# Crear el constructor del grafo
graph = StateGraph(State)

# Inicializar el cliente de Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# Definir la función del chatbot
def chatbot(state: State) -> State:
    messages = state.get("messages", [])
    anthropic_messages = [
        {
            "role": "user" if isinstance(msg, HumanMessage) else "assistant",
            "content": msg.content,
        }
        for msg in messages
    ]
    response = client.messages.create(
        model="claude-3-sonnet-20240229", messages=anthropic_messages, max_tokens=1000
    )
    ai_message = response.content[0].text

    return {"messages": messages + [AIMessage(content=ai_message)]}


# Agregar el nodo del chatbot al grafo
graph.add_node("chatbot", chatbot)

# Configurar el flujo del grafo
graph.set_entry_point("chatbot")
graph.add_edge("chatbot", END)

# Compilar el grafo
chain = graph.compile()


# Función para interactuar con el chatbot
def chat_with_bot(user_input: str) -> str:
    result = chain.invoke({"messages": [HumanMessage(content=user_input)]})
    return result["messages"][-1].content


# Ejemplo de uso
if __name__ == "__main__":
    print("Bienvenido al chatbot. Escribe 'salir' para terminar.")
    while True:
        user_input = input("Tú: ")
        if user_input.lower() == "salir":
            break
        response = chat_with_bot(user_input)
        print(f"Bot: {response}")
