import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


# Load the API key from environment variables
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN not found. Did you create your .env file?")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=HF_TOKEN
)

completion = client.chat.completions.create(
    model="meta-llama-3.1-8b-instruct",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)

print(completion.choices[0].message)