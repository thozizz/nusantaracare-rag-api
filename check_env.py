import os
from dotenv import load_dotenv

load_dotenv()
print("MODEL_NAME:", os.getenv("MODEL_NAME"))
print("LLM_PROVIDER:", os.getenv("LLM_PROVIDER"))
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY")[:10] + "..." if os.getenv("GROQ_API_KEY") else "TIDAK ADA")