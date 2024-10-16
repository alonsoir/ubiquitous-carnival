import os
from swarms import Agent
from swarm_models import OpenAIChat
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI model
model = OpenAIChat(
    openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-4o-mini", temperature=0.1
)

# Initialize the agent
agent = Agent(
    agent_name="Financial-Analysis-Agent",
    system_prompt="Analyze financial situations and provide advice...",
    llm=model,
    max_loops=1,
    autosave=True,
    dashboard=False,
    verbose=True,
    saved_state_path="finance_agent.json"
)

# Run the agent on a financial query
out = agent.run("¿Cómo puedo establecer una cuenta IRA ROTH para comprar acciones y obtener una exención fiscal? ¿Cuáles son los criterios?")
print(out)