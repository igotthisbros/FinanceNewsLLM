import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv()

GITHUB_TOKEN = os.getenv("HF_TOKEN")

client = ChatCompletionsClient(
    endpoint="https://models.inference.ai.azure.com",
    credential=AzureKeyCredential(GITHUB_TOKEN)
)

messages = [
    SystemMessage(content="You are a helpful assistant."),
]

while True:
    user_input = input("You : ").strip()
    
    if user_input.lower() in ["quit","exit"]:
        print("Goodbye!")
        break

    messages.append(UserMessage(content=user_input))
    
    response = client.complete(
        model="Llama-3.3-70B-Instruct",
        messages=messages
    )

    llm_reply = response.choices[0].message.content

    #add llm's response to conversation history
    messages.append(AssistantMessage(content=llm_reply))

    print(f"Assistant: {llm_reply}\n")