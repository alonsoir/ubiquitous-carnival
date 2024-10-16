from swarms import Agent, SequentialWorkflow
from swarm_models import Anthropic

# Initialize agents
agent1 = Agent(agent_name="Blog generator", system_prompt="Generate a blog post", llm=Anthropic(), max_loops=1)
agent2 = Agent(agent_name="Summarizer", system_prompt="Summarize the blog post", llm=Anthropic(), max_loops=1)

# Create Sequential workflow
workflow = SequentialWorkflow(agents=[agent1, agent2], max_loops=1)

# Run workflow
output = workflow.run("Generate a blog post on how swarms of agents can help businesses grow.")
print(output)