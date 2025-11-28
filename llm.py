# llm.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class OfflineLLM:
    def __init__(self, model_name="TheBloke/Llama-2-7B-Chat-GPTQ"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, device_map="auto", torch_dtype=torch.float16
        )

    def generate(self, prompt: str, max_new_tokens=256) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
