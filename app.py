import gradio as gr
from agents import agents, add_or_update_agent, list_agents, delete_agent
from conversation import generate_stream
import time
import os

conversation_log = []
stop_flag = False

def run_conversation(topic, rounds):
    global conversation_log, stop_flag
    stop_flag = False
    conversation_log = []

    if len(agents) < 2:
        return [["system", "Please add at least two agents."]], ""

    names = list(agents.keys())
    agent_cycle = [agents[name] for name in names]
    history = f"Topic: {topic}\n"
    last_msg = "Hi! What are your thoughts on this topic?"

    chat_display = [[agent_cycle[0]["name"], last_msg]]
    conversation_log.append(f"{agent_cycle[0]['name']}: {last_msg}")
    history += f"{agent_cycle[0]['name']}: {last_msg}"

    yield chat_display + [["system", "Conversation started"]], ""

    for round_num in range(rounds):
        if stop_flag:
            break
        for agent in agent_cycle:
            if stop_flag:
                break
            live_reply = ""
            for token in generate_stream(agent, history, last_msg):
                live_reply += token
                yield chat_display + [[agent["name"], live_reply]], ""
            chat_display.append([agent["name"], live_reply])
            conversation_log.append(f"{agent['name']}: {live_reply}")
            history += f"\n{agent['name']}: {live_reply}"
            last_msg = live_reply

    yield chat_display + [["system", "Conversation ended"]], ""

def stop_conversation():
    global stop_flag
    stop_flag = True
    return "Conversation stopped."

def download_conversation():
    filename = f"conversation_{int(time.time())}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(conversation_log))
    return filename

def export_conversation_pretty():
    filename = f"chat_export_{int(time.time())}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Formatted Conversation\n=====================\n")
        for line in conversation_log:
            name, msg = line.split(": ", 1)
            f.write(f"[{name}] >> {msg}\n")
    return filename

def update_agent_ui(name, prompt, model):
    add_or_update_agent(name, prompt, model)
    return "\n".join(list_agents())

def delete_agent_ui(name):
    delete_agent(name)
    return "\n".join(list_agents())

with gr.Blocks(css="body { background-color: black; color: white; }") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Agent Setup")
            agent_name = gr.Textbox(label="Agent Name")
            agent_prompt = gr.Textbox(label="Agent Prompt", lines=5)
            model_name = gr.Textbox(label="Model Name (e.g., meta-llama/Llama-3.2-1B-Instruct)")
            add_btn = gr.Button("Update Agent")
            agent_list = gr.Markdown("Agents:")

            add_btn.click(update_agent_ui,
                          inputs=[agent_name, agent_prompt, model_name],
                          outputs=agent_list)

            delete_name = gr.Textbox(label="Delete Agent Name")
            del_btn = gr.Button("Delete Agent")
            del_btn.click(delete_agent_ui,
                          inputs=delete_name,
                          outputs=agent_list)

        with gr.Column(scale=2):
            gr.Markdown("### MultiAgent Chatbot")
            topic = gr.Textbox(label="Topic")
            rounds = gr.Slider(minimum=1, maximum=20, step=1, value=10, label="Rounds")
            start_btn = gr.Button("Start Conversation")
            stop_btn = gr.Button("Stop Conversation")
            download_btn = gr.Button("Download Raw Log")
            export_btn = gr.Button("Export Pretty Chat")

            chatbot = gr.Chatbot(label="Conversation", height=500, avatar_images=["🧑", "🤖", "💡", "🧠"])
            output_status = gr.Textbox(label="Status Message", lines=1)

            start_btn.click(fn=run_conversation, inputs=[topic, rounds], outputs=[chatbot, output_status])
            stop_btn.click(fn=stop_conversation, outputs=output_status)
            download_btn.click(fn=download_conversation, outputs=gr.File())
            export_btn.click(fn=export_conversation_pretty, outputs=gr.File())

if __name__ == "__main__":
    demo.launch()