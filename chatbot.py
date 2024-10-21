import getpass
import os
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage

# We will use this model for both the conversation and the summarization
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# In memory
conn = sqlite3.connect(":memory:", check_same_thread=False)
print(f"in memory {conn}")
db_path = "state_db/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
print(f"in memory database {db_path} {conn}")

# Here is our checkpointer

memory = SqliteSaver(conn)


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


# _set_env("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain-academy"
load_dotenv()
model = ChatOpenAI(model="gpt-4o", temperature=0)


# State class to store messages and summary
class State(MessagesState):
    summary: str
class OverallState(TypedDict):
    question: str
    answer: str
    notes: str

def thinking_node(state: OverallState):
    return {"answer": "bye", "notes": "... his is name is Lance"}

def answer_node(state: OverallState):
    return {"answer": "bye Lance"}

class PrivateState(TypedDict):
    baz: int

def node_1(state: OverallState) -> PrivateState:
    print("---Node 1---")
    return {"baz": state['foo'] + 1}

def node_2(state: PrivateState) -> OverallState:
    print("---Node 2---")
    return {"foo": state['baz'] + 1}

# Define the logic to call the model
def call_model(state: State):
    # Get summary if it exists
    summary = state.get("summary", "")

    # If there is summary, then we add it to messages
    if summary:

        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"

        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]

    else:
        messages = state["messages"]

    response = model.invoke(messages)
    return {"messages": response}


# Determine whether to end or summarize the conversation
def should_continue(state: State):
    """Return the next node to execute."""

    messages = state["messages"]

    # If there are more than six messages, then we summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"

    # Otherwise we can just end
    return END


def summarize_conversation(state: State):
    # First get the summary if it exists
    summary = state.get("summary", "")

    # Create our summarization prompt
    if summary:

        # If a summary already exists, add it to the prompt
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )

    else:
        # If no summary exists, just create a new one
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    # Delete all but the 2 most recent messages and add our summary to the state
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


# Define a new graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile
graph = workflow.compile(checkpointer=memory)

print("grafo compilado con checkpointer basado en sqlLite!")

# Build graph
# builder = StateGraph(OverallState)
# builder.add_node("node_1", node_1)
# builder.add_node("node_2", node_2)

# Logic
# builder.add_edge(START, "node_1")
# builder.add_edge("node_1", "node_2")
# builder.add_edge("node_2", END)

# Add
# graph = builder.compile()

# Attention! i cannot create two different graphs with the same name!
# I can just create one graph and add nodes to it

# Create a thread
config = {"configurable": {"thread_id": "1"}}

# Start conversation
input_message = HumanMessage(content="hola, encantado de conocerte!, me llamo Alonso, como te llamas?")
output = graph.invoke({"messages": [input_message]}, config)
for m in output["messages"][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="perdona, como me llamo?")
output = graph.invoke({"messages": [input_message]}, config)
for m in output["messages"][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="soy fan del Real Madrid, que tal fue el último partido?")
output = graph.invoke({"messages": [input_message]}, config)
for m in output["messages"][-1:]:
    m.pretty_print()

config = {"configurable": {"thread_id": "1"}}
graph_state = graph.get_state(config)
print(graph_state)
