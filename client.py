import os
import json
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage, UserMessage, AssistantMessage, ToolMessage,
    ChatCompletionsToolDefinition, FunctionDefinition
)
from azure.core.credentials import AzureKeyCredential

load_dotenv()

GITHUB_TOKEN = os.getenv("HF_TOKEN")

client = ChatCompletionsClient(
    endpoint="https://models.inference.ai.azure.com",
    credential=AzureKeyCredential(GITHUB_TOKEN)
)

tools = [
    ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="get_weather",
            description="Get the current weather for a city",
            parameters={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        )
    )
]

def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny and 72°F"

messages = [
    SystemMessage(content="You are a helpful assistant with access to weather data.")
]

print("Chat with the LLM! Ask about weather. Type 'quit' to exit.\n")


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
        messages=messages,
        tools=tools
    )
    
    assistant_message = response.choices[0].message

    if assistant_message.tool_calls:
        print(f"[LLM wants to call a tool!]")
        
        tool_call = assistant_message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        print(f"[Tool: {tool_name}, Args: {tool_args}]")
        
        if tool_name == "get_weather":
            result = get_weather(tool_args["city"])
            print(f"[Tool result: {result}]")
        
        # Add the assistant's tool call to messages
        messages.append(AssistantMessage(
            content="",
            tool_calls=[tool_call]
        ))
        
        # Add the tool result to messages
        messages.append(ToolMessage(
            content=result,
            tool_call_id=tool_call.id
        ))
        
        # Call LLM again with the tool result
        response = client.complete(
            model="Llama-3.3-70B-Instruct",
            messages=messages,
            tools=tools
        )


        assisstant_message = response.choices[0].message

    messages.append(AssistantMessage(content=assisstant_message.content))

    print(f"Assistant: {assisstant_message.content}\n")