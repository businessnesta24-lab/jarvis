# llm_offline.py
import logging
logger = logging.getLogger(__name__)

# try to load a local HF causal model (this is optional / heavy)
_USE_HF = False
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    _USE_HF = True
except Exception:
    _USE_HF = False

class OfflineLLM:
    def __init__(self, model_name: str = None):
        self.model = None
        self.tokenizer = None
        if _USE_HF and model_name:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
                logger.info("Offline LLM loaded: %s", model_name)
            except Exception as e:
                logger.warning("Failed to load HF model: %s", e)
                self.model = None

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        if self.model is None or self.tokenizer is None:
            return "Offline LLM not available on this machine."
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
            return self.tokenizer.decode(out[0], skip_special_tokens=True)
        except Exception as e:
            logger.exception("Offline LLM generation failed: %s", e)
            return "Offline LLM error."
