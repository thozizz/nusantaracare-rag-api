import os
from openai import OpenAI

class LLMClient:
    def __init__(self, provider: str = None, model_name: str = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "groq")
        # Baca dari env, fallback ke model yang masih didukung
        self.model = model_name or os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
        
        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY tidak ditemukan di environment")
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY tidak ditemukan di environment")
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Provider '{self.provider}' tidak didukung.")
    
    def generate(self, messages, temperature=0.0):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content