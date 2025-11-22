import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key="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"
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