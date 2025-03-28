import gradio as gr
from agents import AGENTS
from conversation import generate

def run_conversation(topic, rounds):
    history = f"Topic: {topic}\n"
    last_msg = "Hello, I received a message about my energy bill. Can you help?"
    conversation_log = []

    for _ in range(rounds):
        # CustomerService response
        agent1_prompt = AGENTS["CustomerService"]["prompt"]
        response1 = generate(agent1_prompt, history, last_msg)
        conversation_log.append(f"CustomerService: {response1}")
        history += f"\nCustomerService: {response1}"

        # Customer2 response
        agent2_prompt = AGENTS["Customer2"]["prompt"]
        response2 = generate(agent2_prompt, history, response1)
        conversation_log.append(f"Customer2: {response2}")
        history += f"\nCustomer2: {response2}"

        last_msg = response2

    return "\n".join(conversation_log)

with gr.Blocks(theme=gr.themes.Base(), css="body { background-color: black; color: white; }") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Agent Configuration")

            gr.Markdown("**Name: CustomerService**")
            gr.Textbox(label="Agent Prompt", value=AGENTS["CustomerService"]["prompt"], lines=10, interactive=False)
            gr.Markdown("**Model: LLaMA 3.2 1B Instruct**")

            gr.Markdown("**Name: Customer2**")
            gr.Textbox(label="Agent Prompt", value=AGENTS["Customer2"]["prompt"], lines=5, interactive=False)

            topic = gr.Textbox(label="Topic", value="Focus on how you can lower Mr. Billing’s energy consumption and how he can clear outstanding balances on his energy bill. Remember to keep your replies brief, friendly, and professional.")
            rounds = gr.Slider(minimum=1, maximum=20, step=1, value=10, label="Rounds")

            btn = gr.Button("Start Conversation")

        with gr.Column(scale=2):
            gr.Markdown("### MultiAgent Chatbot")
            output = gr.Textbox(label="", lines=30)

    btn.click(fn=run_conversation, inputs=[topic, rounds], outputs=output)

if __name__ == "__main__":
    demo.launch()
