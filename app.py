import gradio as gr
from agents import agents
from conversation import generate

def run_conversation(topic, rounds):
    if len(agents) < 2:
        return "Please add at least two agents."

    names = list(agents.keys())
    a1, a2 = agents[names[0]], agents[names[1]]
    history = f"Topic: {topic}\n"
    last_msg = "Hello, I received a message about my energy bill. Can you help?"
    conversation_log = []

    for _ in range(rounds):
        reply1 = generate(a1, history, last_msg)
        conversation_log.append(f"{a1['name']}: {reply1}")
        history += f"\n{a1['name']}: {reply1}"

        reply2 = generate(a2, history, reply1)
        conversation_log.append(f"{a2['name']}: {reply2}")
        history += f"\n{a2['name']}: {reply2}"

        last_msg = reply2

    return "\n".join(conversation_log)

with gr.Blocks(css="body { background-color: black; color: white; }") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Agent Setup")
            agent_name = gr.Textbox(label="Agent Name")
            agent_prompt = gr.Textbox(label="Agent Prompt", lines=5)
            model_name = gr.Textbox(label="Model Name (e.g., TheBloke/Llama-3-OpenOrca-1B-GGUF)")
            add_btn = gr.Button("Update Agent")
            agent_list = gr.Markdown("Agents:")

            def update_agents(name, prompt, model):
                from agents import add_or_update_agent, list_agents
                add_or_update_agent(name, prompt, model)
                return "\n".join(list_agents())

            add_btn.click(update_agents, inputs=[agent_name, agent_prompt, model_name], outputs=agent_list)

            delete_name = gr.Textbox(label="Delete Agent Name")
            del_btn = gr.Button("Delete Agent")
            def delete_and_list(name):
                from agents import delete_agent, list_agents
                delete_agent(name)
                return "\n".join(list_agents())
            del_btn.click(delete_and_list, inputs=delete_name, outputs=agent_list)

        with gr.Column(scale=2):
            gr.Markdown("### MultiAgent Chatbot")
            topic = gr.Textbox(label="Topic")
            rounds = gr.Slider(minimum=1, maximum=20, step=1, value=10, label="Rounds")
            start_btn = gr.Button("Start Conversation")
            output = gr.Textbox(label="Conversation Output", lines=25)
            start_btn.click(fn=run_conversation, inputs=[topic, rounds], outputs=output)

if __name__ == "__main__":
    demo.launch()
