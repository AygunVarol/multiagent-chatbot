from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

loaded_models = {}

def load_model(model_name):
    if model_name not in loaded_models:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
        loaded_models[model_name] = (tokenizer, model)
    return loaded_models[model_name]

def generate_stream(agent, history, user_input):
    tokenizer, model = load_model(agent['model'])

    # Build clean prompt with consistent role format
    prompt = f"{agent['prompt']}\n\n" \
             f"### Conversation History:\n{history}\n" \
             f"[{agent['name']}]:"

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(model.device)

    output_ids = model.generate(
        **inputs,
        max_new_tokens=60,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_p=0.9,
        top_k=40,
        temperature=0.7,
        repetition_penalty=1.2,
        eos_token_id=tokenizer.eos_token_id
    )

    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Extract response
    answer = output_text.split("### Conversation History:")[-1]
    answer = answer.split(f"[{agent['name']}]:")[-1].strip()

    # Clean and stream
    for token in answer.split():
        yield token + ' '