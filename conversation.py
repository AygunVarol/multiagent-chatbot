from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

loaded_models = {}

def load_model(model_name):
    if model_name not in loaded_models:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
        loaded_models[model_name] = (tokenizer, model)
    return loaded_models[model_name]

def generate(agent, history, user_input):
    tokenizer, model = load_model(agent['model'])
    prompt = f"{agent['prompt']}\n\nConversation:\n{history}\n{user_input}\n"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=150, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("Conversation:")[-1].strip()
