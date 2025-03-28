agents = {}

def add_or_update_agent(agent_name, prompt, model_name):
    agents[agent_name] = {
        "name": agent_name,
        "prompt": prompt,
        "model": model_name
    }

def list_agents():
    return [f"Name: {agent['name']}" for agent in agents.values()]

def delete_agent(agent_name):
    if agent_name in agents:
        del agents[agent_name]
