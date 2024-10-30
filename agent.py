from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from dotenv import load_dotenv
from rich.console import Console
import pyfiglet
import arrow
from textblob import TextBlob
blob_message="Python is amazing!"
blob = TextBlob(blob_message)


now = arrow.now()


result = pyfiglet.figlet_format("AGENT 007")
console = Console()

console.print(f"[red]{result}[/red]")


console.print("[red]This is a helpful assistant tasked with writing performing arithmetic on a set of inputs.[/red]")
console.print("[red]You can use the following tools:[/red]")
console.print("[blue]add, multiply, divide[/blue]")
console.print("[yellow]The tools will be invoked by the llm.[/yellow]")
console.print(f"Today is {now.shift(hours=+0).format('YYYY-MM-DD HH:mm:ss')}")
load_dotenv()
console.print(f"This is the blob_message: {blob_message}. [blue]Calculate the sentiment of the blob_message[/blue]")
console.print(f"{blob.sentiment}")  # Outputs the sentiment of the text

def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiplies a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


def divide(a: int, b: int) -> float:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


tools = [add, multiply, divide]

# Define LLM with bound tools
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(
    content="You are a helpful assistant tasked with writing performing arithmetic on a set of inputs."
)


# Node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Compile graph
graph = builder.compile()

first_message="What is 2 + 2?"
console.print(f"[blue]{first_message}[/blue]")
output = graph.invoke({"messages": [HumanMessage(content=first_message)]})
for m in output["messages"][-1:]:
    console.print(m.pretty_print())

second_message="What is 2 * 3?"
console.print(f"[blue]{second_message}[/blue]")
output = graph.invoke({"messages": [HumanMessage(content=second_message)]})
for m in output["messages"][-1:]:
    console.print(m.pretty_print())

third_message="What is 2 / 2?"
console.print(f"[blue]{third_message}[/blue]")
output = graph.invoke({"messages": [HumanMessage(content=third_message)]})
for m in output["messages"][-1:]:
    console.print(m.pretty_print())

